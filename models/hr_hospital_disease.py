import logging

from odoo import models, fields

_logger = logging.getLogger(__name__)


class HRHDisease(models.Model):
    _name = "hr.hospital.disease"
    _description = "Disease"

    name = fields.Char(required=True)
    description = fields.Text()

    # Hierarchical structure
    parent_id = fields.Many2one(
        comodel_name='hr.hospital.disease',
        string='Parent Disease',
    )
    child_ids = fields.One2many(
        comodel_name='hr.hospital.disease',
        inverse_name='parent_id',
        string='Child Diseases',
    )

    # Medical classification
    icd10_code = fields.Char(string='ICD-10 Code', size=10)
    danger_level = fields.Selection(
        selection=[
            ('low', 'Low'),
            ('medium', 'Medium'),
            ('high', 'High'),
            ('critical', 'Critical'),
        ],
    )
    is_contagious = fields.Boolean(default=False)
    symptoms = fields.Text()
    region_ids = fields.Many2many(
        comodel_name='res.country',
        string='Spread Regions',
    )

    # Related visits
    patient_visit_ids = fields.One2many(
        comodel_name='hr.hospital.patient.visit',
        inverse_name='disease_id',
        string='Patient Visits',
    )
