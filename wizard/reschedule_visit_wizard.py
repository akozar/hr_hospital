import logging
from datetime import datetime, timedelta

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class RescheduleVisitWizard(models.TransientModel):
    _name = 'reschedule.visit.wizard'
    _description = 'Reschedule Visit Wizard'

    visit_id = fields.Many2one(
        comodel_name='hr.hospital.patient.visit',
        string='Current Visit',
        required=True,
        readonly=True,
    )
    patient_id = fields.Many2one(
        related='visit_id.patient_id',
        string='Patient',
        readonly=True,
    )
    current_doctor_id = fields.Many2one(
        related='visit_id.doctor_id',
        string='Current Doctor',
        readonly=True,
    )
    current_scheduled_time = fields.Datetime(
        related='visit_id.scheduled_time',
        string='Current Scheduled Time',
        readonly=True,
    )
    new_doctor_id = fields.Many2one(
        comodel_name='hr.hospital.doctor',
        string='New Doctor',
    )
    new_date = fields.Date(
        string='New Date',
        required=True,
    )
    new_time = fields.Float(
        string='New Time',
        required=True,
    )
    reason = fields.Text(
        string='Reason for Rescheduling',
        required=True,
    )

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        active_id = self.env.context.get('active_id')
        if active_id:
            visit = self.env['hr.hospital.patient.visit'].browse(active_id)
            res['visit_id'] = active_id
            res['new_doctor_id'] = visit.doctor_id.id
            if visit.scheduled_time:
                res['new_date'] = visit.scheduled_time.date()
                res['new_time'] = (
                    visit.scheduled_time.hour +
                    visit.scheduled_time.minute / 60.0
                )
        return res

    @api.constrains('visit_id')
    def _check_visit_state(self):
        for record in self:
            if record.visit_id.state != 'scheduled':
                raise ValidationError(
                    _("Only scheduled visits can be rescheduled!")
                )

    def action_reschedule(self):
        self.ensure_one()

        # Validate visit state
        if self.visit_id.state != 'scheduled':
            raise ValidationError(_("Only scheduled visits can be rescheduled!"))

        # Build new scheduled_time from date + time
        hours = int(self.new_time)
        minutes = int((self.new_time - hours) * 60)
        new_scheduled_time = datetime.combine(
            self.new_date,
            datetime.min.time()
        ) + timedelta(hours=hours, minutes=minutes)

        # Cancel old visit
        self.visit_id.write({'state': 'cancelled'})

        # Create new visit
        new_visit = self.env['hr.hospital.patient.visit'].create({
            'patient_id': self.visit_id.patient_id.id,
            'doctor_id': (self.new_doctor_id or self.visit_id.doctor_id).id,
            'scheduled_time': new_scheduled_time,
            'visit_type': self.visit_id.visit_type,
            'state': 'scheduled',
        })

        # Return action to view new visit
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'hr.hospital.patient.visit',
            'res_id': new_visit.id,
            'view_mode': 'form',
            'target': 'current',
        }
