import logging

from odoo import models, fields

_logger = logging.getLogger(__name__)


class HRHPatient(models.Model):
    _name = "hr.hospital.patient"
    _description = "Patient"
    _inherit = ['hr.hospital.abstract.person']

    description = fields.Text()

    doctor_id = fields.Many2one(
        comodel_name='hr.hospital.doctor',
        string='Personal Doctor',
    )
    passport_data = fields.Char(string='Passport Data', size=10)
    contact_person_id = fields.Many2one(
        comodel_name='hr.hospital.contact.person',
        string='Contact Person',
    )
    blood_group = fields.Selection(
        selection=[
            ('o_pos', 'O(I) Rh+'),
            ('o_neg', 'O(I) Rh-'),
            ('a_pos', 'A(II) Rh+'),
            ('a_neg', 'A(II) Rh-'),
            ('b_pos', 'B(III) Rh+'),
            ('b_neg', 'B(III) Rh-'),
            ('ab_pos', 'AB(IV) Rh+'),
            ('ab_neg', 'AB(IV) Rh-'),
        ],
        string='Blood Group',
    )
    allergies = fields.Text(string='Allergies')
    insurance_company_id = fields.Many2one(
        comodel_name='res.partner',
        string='Insurance Company',
        domain=[('is_company', '=', True)],
    )
    insurance_policy_number = fields.Char(string='Insurance Policy Number')
    doctor_history_ids = fields.One2many(
        comodel_name='hr.hospital.patient.doctor.history',
        inverse_name='patient_id',
        string='Doctor History',
    )

    res_partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Contact',
    )
