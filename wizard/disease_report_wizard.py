import logging

from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class DiseaseReportWizard(models.TransientModel):
    _name = 'disease.report.wizard'
    _description = 'Disease Report Wizard'

    doctor_ids = fields.Many2many(
        comodel_name='hr.hospital.doctor',
        help='If empty, all doctors will be included',
    )
    disease_ids = fields.Many2many(
        comodel_name='hr.hospital.disease',
        help='If empty, all diseases will be included',
    )
    country_ids = fields.Many2many(
        comodel_name='res.country',
        string='Patient Countries',
        help='Filter by patient citizenship country',
    )
    date_from = fields.Date(
        required=True,
    )
    date_to = fields.Date(
        required=True,
    )

    # TODO What is a difference?
    report_type = fields.Selection(
        selection=[
            ('detailed', 'Detailed'),
            ('summary', 'Summary'),
        ],
        default='detailed',
        required=True,
    )
    # How to do this?
    group_by = fields.Selection(
        selection=[
            ('doctor', 'By Doctor'),
            ('disease', 'By Disease'),
            ('month', 'By Month'),
            ('country', 'By Country'),
        ],
        default='doctor',
    )

    def action_generate_report(self):
        """Generate report and return diagnoses matching criteria."""
        # First, find visits matching date and other criteria
        visit_domain = self._build_visit_domain()
        visits = self.env['hr.hospital.patient.visit'].search(visit_domain)

        # Then filter diagnoses
        diagnosis_domain = [('visit_id', 'in', visits.ids)]
        if self.disease_ids:
            diagnosis_domain.append(('disease_id', 'in', self.disease_ids.ids))

        diagnoses = self.env['hr.hospital.diagnosis'].search(diagnosis_domain)

        # Return action to display results
        return {
            'name': 'Disease Report Results',
            'type': 'ir.actions.act_window',
            'res_model': 'hr.hospital.diagnosis',
            'view_mode': 'list,form',
            'domain': [('id', 'in', diagnoses.ids)],
            'target': 'current',
        }

    def _build_visit_domain(self):
        """Build search domain for visits based on wizard filters."""
        from datetime import datetime, timedelta

        domain = []

        # Date range filter (convert Date to Datetime for comparison)
        date_from_dt = datetime.combine(self.date_from, datetime.min.time())
        date_to_dt = datetime.combine(self.date_to, datetime.max.time())

        domain.append(('scheduled_time', '>=', date_from_dt))
        domain.append(('scheduled_time', '<=', date_to_dt))

        # Doctor filter
        if self.doctor_ids:
            domain.append(('doctor_id', 'in', self.doctor_ids.ids))

        # Country filter (patient citizenship)
        if self.country_ids:
            domain.append(('patient_id.country_id', 'in', self.country_ids.ids))

        return domain

