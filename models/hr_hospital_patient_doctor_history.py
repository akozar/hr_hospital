import logging

from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class HRHPatientDoctorHistory(models.Model):
    _name = 'hr.hospital.patient.doctor.history'
    _description = 'Patient Doctor History'

    patient_id = fields.Many2one(
        comodel_name='hr.hospital.patient',
        required=True,
        ondelete='cascade',
    )
    doctor_id = fields.Many2one(
        comodel_name='hr.hospital.doctor',
        required=True,
    )
    date_start = fields.Date(
        string='Assignment Date',
        required=True,
        default=fields.Date.today,
    )
    date_end = fields.Date()
    reason = fields.Text(string='Reason for Change')
    active = fields.Boolean(default=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('patient_id'):
                # Deactivate previous active records
                self.search([
                    ('patient_id', '=', vals['patient_id']),
                    ('active', '=', True),
                ]).write({
                    'date_end': fields.Date.today(),
                    'active': False,
                })
        return super().create(vals_list)
