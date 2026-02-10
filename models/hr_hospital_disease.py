import logging

from odoo import models, fields

_logger = logging.getLogger(__name__)

class HRHDisease(models.Model):
    _name = "hr.hospital.disease"
    _description = "Disease"

    name = fields.Char()
    description = fields.Text()

    patient_visit_ids = fields.One2many(
        comodel_name='hr.hospital.patient.visit',
        inverse_name='disease_id',
        string='Patient visits',
    )
