{
    'name': 'Record Relationship Explorer',
    'summary': 'Visualize and open relationships around any Odoo record.',
    'description': """
Record Relationship Explorer
============================
Adds a reusable Owl relationship graph to Odoo 19. Open it from the Action
menu of any saved form record. Sale Orders receive a richer graph connecting
the customer, invoices, reconciled payments, and delivery orders/pickings.
Other models expose their readable relational fields automatically.
""",
    'version': '19.0.1.0.1',
    'category': 'Tools/UI',
    'author': 'SARANG T',
    'license': 'LGPL-3',
    'images': ['static/description/icon.png'],
    'depends': ['web', 'sale_stock', 'account'],
    'data': [
        'security/ir.model.access.csv',
    ],
    'assets': {
        'web.assets_backend': [
            'record_relationship_explorer/static/src/xml/relationship_explorer.xml',
            'record_relationship_explorer/static/src/js/relationship_explorer.js',
            'record_relationship_explorer/static/src/scss/relationship_explorer.scss',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}

