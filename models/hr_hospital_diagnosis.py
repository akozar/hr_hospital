import logging

from odoo import models, fields, api
from odoo.exceptions import ValidationError

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

    def action_approve(self):
        self.ensure_one()

        # Get current user's doctor record
        current_doctor = self.env['hr.hospital.doctor'].search([
            ('user_id', '=', self.env.uid),
        ], limit=1)

        visit_doctor = self.visit_id.doctor_id

        if not current_doctor:
            raise ValidationError("You must be a doctor to approve diagnoses.")

        # If visit doctor is intern, only their mentor can approve
        if visit_doctor.is_intern:
            if current_doctor != visit_doctor.mentor_id:
                raise ValidationError(
                    f"Only the mentor ({visit_doctor.mentor_id.name}) "
                    f"can approve diagnoses for intern {visit_doctor.name}."
                )

        self.write({
            'is_approved': True,
            'approved_by_id': current_doctor.id if current_doctor else False,
            'approval_date': fields.Datetime.now(),
        })
