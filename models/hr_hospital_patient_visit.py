import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

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
        domain=[('license_number', '!=', False)],
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

    diagnosis_count = fields.Integer(
        string='Number of Diagnoses',
        compute='_compute_diagnosis_count',
    )

    @api.depends('diagnosis_ids')
    def _compute_diagnosis_count(self):
        for record in self:
            record.diagnosis_count = len(record.diagnosis_ids)

    @api.onchange('patient_id')
    def _onchange_patient_id(self):
        if self.patient_id and self.patient_id.allergies:
            return {
                'warning': {
                    'title': 'Allergy Alert!',
                    'message': f'Patient has allergies: {self.patient_id.allergies}',
                }
            }

    @api.onchange('doctor_id')
    def _onchange_doctor_id(self):
        if self.doctor_id and self.doctor_id.is_intern:
            if self.doctor_id.mentor_id:
                return {
                    'warning': {
                        'title': 'Intern Doctor',
                        'message': f'This is an intern. Mentor: {self.doctor_id.mentor_id.name}',
                    }
                }

    @api.constrains('patient_id', 'doctor_id', 'scheduled_time')
    def _check_one_visit_per_day(self):
        for record in self:
            if record.scheduled_time and record.patient_id and record.doctor_id:
                visit_date = record.scheduled_time.date()
                existing = self.search([
                    ('id', '!=', record.id),
                    ('patient_id', '=', record.patient_id.id),
                    ('doctor_id', '=', record.doctor_id.id),
                    ('scheduled_time', '>=', visit_date.strftime('%Y-%m-%d 00:00:00')),
                    ('scheduled_time', '<=', visit_date.strftime('%Y-%m-%d 23:59:59')),
                    ('state', '!=', 'cancelled'),
                ])
                if existing:
                    raise ValidationError(
                        _("Patient '%s' already has a visit scheduled with doctor '%s' on %s!") %
                        (record.patient_id.name, record.doctor_id.name, visit_date)
                    )

    def unlink(self):
        for record in self:
            if record.diagnosis_ids:
                raise ValidationError(
                    _("Cannot delete visit with diagnoses! Remove diagnoses first.")
                )
        return super().unlink()

    def write(self, vals):
        protected_fields = {'doctor_id', 'scheduled_time', 'patient_id'}
        if protected_fields & set(vals.keys()):
            for record in self:
                if record.state == 'done':
                    raise ValidationError(
                        _("Cannot modify doctor, patient or scheduled time of completed visits!")
                    )
        return super().write(vals)
