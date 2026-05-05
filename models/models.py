from odoo import models, fields, api

class FisheryRegulation(models.Model):
    _name = 'fishery.regulation'
    _description = 'Registro de normativas legales'
    _inherit = ["mail.thread", "mail.activity.mixin"]

# información básica de la normativa
    name = fields.Char(
        string='Título',
        readonly=True,
        tracking=True,
        default="GACETA OFICIAL DE LA REPÚBLICA BOLIVARIANA DE VENEZUELA N°.",
        help="El título se genera automáticamente a partir del número de gaceta oficial y si es extraordinaria o no."
    )

    official_gazette = fields.Integer(
        string = 'N° gaceta oficial',
        required = True,
        help="Ingrese solo el número, sin puntos ni letras.",
        tracking=True
    )

    official_regulations = fields.Char(
        string = 'N°',
        required = True,
        help="Ingrese solo el número, sin puntos ni letras.",
        tracking=True
    )

    is_extraordinary = fields.Boolean(
        string = 'Extraordinario',
        default = False,
        tracking=True
    )

# información adicional de la normativa
    regulation_type = fields.Selection( 
        [
            ('ley', 'Ley'),
            ('decreto', 'Decreto'),
            ('resolucion', 'Resolución'),
            ('providencia', 'Providencia Administrativa'),
        ],
        string = 'Tipo de Normativa',
        required = True,
        tracking=True
    )

    type_status = fields.Selection(
        [
            ('derogado', 'Derogado'),
            ('vigente', 'Vigente')
        ],
        string = 'Estado',
        default = 'vigente',
        required = True,
        tracking=True
    )

#información de relaciones entre normativas
    derogated_by_id = fields.Many2one( # "A" Normativa que es derogada.
        'fishery.regulation',
        string = 'Derogada por ...',
        help = 'Normativa de la cual es derogada',
        readonly=True,
        tracking=True
    )

    derogates_id = fields.Many2one( # "B" Normativa que deroga.
        'fishery.regulation',
        string = 'Deroga a...',
        help = 'Normativa a la cual deroga'
    )

#información adicional de la normativa
    publication_date = fields.Date(
        string = 'Fecha de publicación',
        default = fields.Date.today
    )

    normative_date = fields.Date(

        string = 'Fecha de normativa',
        default = fields.Date.today
    )

    legal_instrument = fields.Html(
        string = 'Descripción',
        help = 'Ingrese una descripción de la normativa, incluyendo su contenido y alcance.',
    )

    attachment_ids = fields.Many2many(
        'ir.attachment',
        string = 'Adjunto Digital',
        required = True
    )

# --- LÓGICA DE TÍTULO ---
    def _generate_formal_title(self, vals):
        base = "GACETA OFICIAL DE LA REPÚBLICA BOLIVARIANA DE VENEZUELA"
        
        # Obtenemos valores de vals (si se están escribiendo) o del registro actual
        num = vals.get('official_gazette') or self.official_gazette
        extra = vals.get('is_extraordinary') if 'is_extraordinary' in vals else self.is_extraordinary
        
        tipo = " EXTRAORDINARIO" if extra else ""
        return f"{base} N°. {num}{tipo}"

    # --- MÉTODOS CRUD (FUSIONADOS) ---
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            # 1. Generar título antes de crear
            vals['name'] = self.env['fishery.regulation']._generate_formal_title(vals)
        
        records = super(FisheryRegulation, self).create(vals_list)

        # 2. Lógica de derogación tras crear
        for record in records:
            if record.type_status == 'vigente' and record.derogates_id:
                if record.derogates_id.id == record.id:
                    raise ValidationError(_("Una normativa no puede derogarse a sí misma."))
                record.derogates_id.write({
                    'type_status': 'derogado',
                    'derogated_by_id': record.id
                })
        return records

    def write(self, vals):
        # 1. Si cambian campos del título, recalcularlo
        if 'official_gazette' in vals or 'is_extraordinary' in vals:
            for record in self:
                vals['name'] = record._generate_formal_title(vals)

        res = super(FisheryRegulation, self).write(vals)

        # 2. Lógica de derogación al actualizar
        if 'type_status' in vals or 'derogates_id' in vals:
            for record in self:
                if record.type_status == 'vigente' and record.derogates_id:
                    if record.derogates_id.id == record.id:
                        raise ValidationError(_("Una normativa no puede derogarse a sí misma."))
                    record.derogates_id.write({
                        'type_status': 'derogado',
                        'derogated_by_id': record.id
                    })
        return res