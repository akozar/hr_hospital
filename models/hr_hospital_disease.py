import logging

from odoo import models, fields

_logger = logging.getLogger(__name__)

class HRHDisease(models.Model):
    _name = "hr.hospital.disease"
    _description = "Disease"

    name = fields.Char()
    description = fields.Text()

    patient_visit_id = fields.Many2one(
        comodel_name='hr.hospital.patient.visit',
        string='Patient visit',
    )
