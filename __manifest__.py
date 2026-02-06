{
    'name': 'HR Hospital',
    'summary': '',
    'author': 'Oleksandr Kozar',
    'website': 'https://odoo.school/',
    'category': 'Customizations',
    'license': 'OPL-1',
    'version': '19.0.0.0.0',

    'depends': [
        'base',
    ],

    'external_dependencies': {
        'python': [],
    },

    'data': [
        'security/ir.model.access.csv',
        'views/hr_hospital_menu.xml',
        'views/hr_hospital_doctor_views.xml',
        'views/hr_hospital_patient_views.xml',
        'views/hr_hospital_disease_views.xml',
        'data/master_data.xml',
        # 'views/hr_hospital_patient_views.xml',
    ],
    'demo': [
    ],

    'installable': True,
    'auto_install': False,

    'images': [
    ],

}
