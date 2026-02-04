import logging

from odoo import models, fields

_logger = logging.getLogger(__name__)

class HRHPatientVisit(models.Model):
    _name = "hr.hospital.patient.visit"
    _description = "Patient Visit"

    visit_time = fields.Datetime(
        string='Visit date and time',
    )

    patient_id = fields.Many2one(
        comodel_name='hr.hospital.patient',
        string="Patient",
    )

    disease_id = fields.One2many(
        comodel_name='hr.hospital.disease',
        inverse_name='patient_visit_id',
        string="Patient",
    )
