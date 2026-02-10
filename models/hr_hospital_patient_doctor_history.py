import logging

from odoo import models, fields

_logger = logging.getLogger(__name__)


class HRHPatientDoctorHistory(models.Model):
    _name = 'hr.hospital.patient.doctor.history'
    _description = 'Patient Doctor History'

    patient_id = fields.Many2one(
        comodel_name='hr.hospital.patient',
        string='Patient',
        required=True,
        ondelete='cascade',
    )
    doctor_id = fields.Many2one(
        comodel_name='hr.hospital.doctor',
        string='Doctor',
        required=True,
    )
    date_start = fields.Date(
        string='Assignment Date',
        required=True,
        default=fields.Date.today,
    )
    date_end = fields.Date(string='End Date')
    reason = fields.Text(string='Reason for Change')
    active = fields.Boolean(string='Active', default=True)
