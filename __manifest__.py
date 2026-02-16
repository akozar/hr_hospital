{
    'name': 'HR Hospital',
    'author': 'Oleksandr Kozar',
    'website': 'https://odoo.school/',
    'category': 'Customizations',
    'license': 'LGPL-3',
    'version': '19.0.0.0.4',

    'depends': [
        'base',
    ],

    'external_dependencies': {
        'python': [],
    },

    'data': [
        'security/ir.model.access.csv',
        'views/hr_hospital_menu.xml',
        'views/hr_hospital_doctor_specialty_views.xml',
        'views/hr_hospital_doctor_views.xml',
        'views/hr_hospital_doctor_schedule_views.xml',
        'views/hr_hospital_patient_views.xml',
        'views/hr_hospital_disease_views.xml',
        'views/hr_hospital_contact_person_views.xml',
        'views/hr_hospital_patient_visit_views.xml',
        'views/hr_hospital_diagnosis_views.xml',
        'wizard/mass_reassign_doctor_wizard_views.xml',
        'wizard/disease_report_wizard_views.xml',
        'wizard/reschedule_visit_wizard_views.xml',
        'wizard/doctor_schedule_wizard_views.xml',
        'wizard/patient_card_export_wizard_views.xml',
        'data/hr_hospital_disease_master_data.xml',
    ],
    'demo': [
        'demo/hr_hospital_doctor_specialty_demo.xml',
        'demo/hr_hospital_contact_person_demo.xml',
        'demo/hr_hospital_doctor_demo.xml',
        'demo/hr_hospital_doctor_schedule_demo.xml',
        'demo/hr_hospital_patient_demo.xml',
        'demo/hr_hospital_patient_doctor_history_demo.xml',
        'demo/hr_hospital_patient_visit_demo.xml',
        'demo/hr_hospital_diagnosis_demo.xml',
    ],
}
