import logging
from datetime import timedelta

from odoo import models, fields
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class HRHDiagnosis(models.Model):
    _name = 'hr.hospital.diagnosis'
    _description = 'Diagnosis'

    visit_id = fields.Many2one(
        comodel_name='hr.hospital.patient.visit',
        required=True,
        ondelete='cascade',
        domain=lambda self: [
            ('state', '=', 'done'),
            ('scheduled_time', '>=', fields.Datetime.now() - timedelta(days=30)),
        ],
    )
    disease_id = fields.Many2one(
        comodel_name='hr.hospital.disease',
        domain=[
            ('is_contagious', '=', True),
            ('danger_level', 'in', ['high', 'critical']),
        ],
    )
    description = fields.Text()
    treatment = fields.Html(string='Prescribed Treatment')
    is_approved = fields.Boolean(default=False)
    approved_by_id = fields.Many2one(
        comodel_name='hr.hospital.doctor',
        readonly=True,
    )
    approval_date = fields.Datetime(readonly=True)
    severity = fields.Selection(
        selection=[
            ('mild', 'Mild'),
            ('moderate', 'Moderate'),
            ('severe', 'Severe'),
            ('critical', 'Critical'),
        ],
    )

    def action_approve(self):
        self.ensure_one()

        # Get current user's doctor record
        current_doctor = self.env['hr.hospital.doctor'].search([
            ('user_id', '=', self.env.uid),
        ], limit=1)

        visit_doctor = self.visit_id.doctor_id

        if not current_doctor:
            raise ValidationError(self.env._("You must be a doctor to approve diagnoses."))

        # If visit doctor is intern, only their mentor can approve
        if visit_doctor.is_intern:
            if current_doctor != visit_doctor.mentor_id:
                raise ValidationError(
                    self.env._(
                        "Only the mentor (%(mentor)s) can approve diagnoses for intern %(intern)s.",
                        mentor=visit_doctor.mentor_id.name,
                        intern=visit_doctor.name,
                    )
                )

        self.write({
            'is_approved': True,
            'approved_by_id': current_doctor.id if current_doctor else False,
            'approval_date': fields.Datetime.now(),
        })
