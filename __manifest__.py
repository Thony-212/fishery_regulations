{
    'name' : 'Gestión de Normativas Pesqueras',
    'version' : '1.0',
    'category' : 'Intranet',
    'description' : "Registro de normativas legales.",
    'author' : 'Anthony',
    'depends' : ['base',"mail"],

    'data' : [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/views.xml',
    ],

    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
