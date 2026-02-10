import logging

from odoo import models, fields

_logger = logging.getLogger(__name__)


class HRHDiagnosis(models.Model):
    _name = 'hr.hospital.diagnosis'
    _description = 'Diagnosis'

    visit_id = fields.Many2one(
        comodel_name='hr.hospital.patient.visit',
        string='Visit',
        required=True,
        ondelete='cascade',
    )
    disease_id = fields.Many2one(
        comodel_name='hr.hospital.disease',
        string='Disease',
    )
    description = fields.Text(string='Diagnosis Description')
    treatment = fields.Html(string='Prescribed Treatment')
    is_approved = fields.Boolean(string='Approved', default=False)
    approved_by_id = fields.Many2one(
        comodel_name='hr.hospital.doctor',
        string='Approved By',
        readonly=True,
    )
    approval_date = fields.Datetime(string='Approval Date', readonly=True)
    severity = fields.Selection(
        selection=[
            ('mild', 'Mild'),
            ('moderate', 'Moderate'),
            ('severe', 'Severe'),
            ('critical', 'Critical'),
        ],
        string='Severity',
    )
