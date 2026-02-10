import logging

from odoo import models, fields

_logger = logging.getLogger(__name__)


class HRHDoctorSpecialty(models.Model):
    _name = 'hr.hospital.doctor.specialty'
    _description = 'Doctor Specialty'

    name = fields.Char(string='Specialty Name', required=True)
    code = fields.Char(string='Specialty Code', size=10, required=True)
    description = fields.Text(string='Description')
    active = fields.Boolean(string='Active', default=True)
    doctor_ids = fields.One2many(
        comodel_name='hr.hospital.doctor',
        inverse_name='specialty_id',
        string='Doctors',
    )
