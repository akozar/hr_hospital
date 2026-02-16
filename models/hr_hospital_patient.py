import logging

from odoo import models, fields, api

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

    def write(self, vals):
        if 'doctor_id' in vals:
            for record in self:
                if record.doctor_id and record.doctor_id.id != vals['doctor_id']:
                    # Close previous history record
                    active_history = self.env['hr.hospital.patient.doctor.history'].search([
                        ('patient_id', '=', record.id),
                        ('active', '=', True),
                    ], limit=1)
                    if active_history:
                        active_history.write({
                            'date_end': fields.Date.today(),
                            'active': False,
                        })
                    # Create new history record
                    if vals['doctor_id']:
                        self.env['hr.hospital.patient.doctor.history'].create({
                            'patient_id': record.id,
                            'doctor_id': vals['doctor_id'],
                            'date_start': fields.Date.today(),
                        })
        return super().write(vals)

    @api.onchange('country_id')
    def _onchange_country_id(self):
        if self.country_id:
            lang = self.env['res.lang'].search([
                ('code', '=like', self.country_id.code.lower() + '%'),
                ('active', '=', True),
            ], limit=1)
            if lang:
                self.lang_id = lang
