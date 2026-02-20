from odoo import models, fields, api

class FisheryRegulation(models.Model):
    _name = 'fishery.regulation'
    _description = 'Registro de normativas legales'
    _rec_name = 'official_regulations'
    _inherit = ["mail.thread", "mail.activity.mixin"]

    official_gazette = fields.Integer(
        string = 'N° gaceta oficial',
        required = True,
        help="Ingrese solo el número, sin puntos ni letras.",
        tracking=True
    )

    official_regulations = fields.Integer(
        string = 'N° de Normativa',
        required = True,
        help="Ingrese solo el número, sin puntos ni letras.",
        tracking=True
    )

    is_extraordinary = fields.Boolean(
        string = '¿Es Extraordinario?',
        required = True,
        tracking=True
    )

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

    publication_date = fields.Date(
        string = 'Facha de publicación',
        default = fields.Date.today
    )

    legal_instrument = fields.Html(
        string = 'Instrumento Jurídico / Descripción',
        required = True
    )

    attachment_ids = fields.Many2many(
        'ir.attachment',
        string = 'Adjunto Digital',
        required = True
    )

    @api.model # para que A se actualice solo
    def create(self, vals):
        record = super().create(vals)
        if record.type_status == 'vigente' and record.derogates_id:
            record.derogates_id.write({
                'type_status': 'derogado',
                'derogated_by_id': record.id
            })
        return record

    def write(self, vals): # evitar que B se seleccione a sí mismo
        res = super().write(vals)
        if 'type_status' in vals or 'derogates_id' in vals:
            for record in self:
                if record.type_status == 'vigente' and record.derogates_id:
                    if record.derogates_id.id != record.id:
                        record.derogates_id.write({
                            'type_status': 'derogado',
                            'derogated_by_id': record.id
                        })
        return res