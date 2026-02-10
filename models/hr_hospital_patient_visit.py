import logging

from odoo import models, fields

_logger = logging.getLogger(__name__)


class HRHPatientVisit(models.Model):
    _name = "hr.hospital.patient.visit"
    _description = "Patient Visit"

    state = fields.Selection(
        selection=[
            ('scheduled', 'Scheduled'),
            ('done', 'Completed'),
            ('cancelled', 'Cancelled'),
            ('no_show', 'No Show'),
        ],
        string='Status',
        default='scheduled',
    )
    scheduled_time = fields.Datetime(string='Scheduled Date and Time')
    actual_time = fields.Datetime(string='Actual Date and Time')
    doctor_id = fields.Many2one(
        comodel_name='hr.hospital.doctor',
        string='Doctor',
        required=True,
    )
    patient_id = fields.Many2one(
        comodel_name='hr.hospital.patient',
        string='Patient',
        required=True,
    )
    visit_type = fields.Selection(
        selection=[
            ('primary', 'Primary'),
            ('follow_up', 'Follow-up'),
            ('preventive', 'Preventive'),
            ('emergency', 'Emergency'),
        ],
        string='Visit Type',
    )
    diagnosis_ids = fields.One2many(
        comodel_name='hr.hospital.diagnosis',
        inverse_name='visit_id',
        string='Diagnoses',
    )
    recommendations = fields.Html(string='Recommendations')
    cost = fields.Monetary(string='Visit Cost', currency_field='currency_id')
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='Currency',
    )

    # Keep old field for compatibility
    visit_time = fields.Datetime(string='Visit Date and Time')
    disease_id = fields.Many2one(
        comodel_name='hr.hospital.disease',
        string='Disease',
    )
