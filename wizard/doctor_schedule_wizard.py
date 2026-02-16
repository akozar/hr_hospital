import logging
from datetime import timedelta

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class DoctorScheduleWizard(models.TransientModel):
    _name = 'doctor.schedule.wizard'
    _description = 'Doctor Schedule Wizard'

    doctor_id = fields.Many2one(
        comodel_name='hr.hospital.doctor',
        string='Doctor',
        required=True,
    )
    week_start = fields.Date(
        string='Week Start Date',
        required=True,
    )
    num_weeks = fields.Integer(
        string='Number of Weeks',
        default=1,
        required=True,
    )
    schedule_pattern = fields.Selection(
        selection=[
            ('standard', 'Standard (All Weeks)'),
            ('even_week', 'Even Weeks Only'),
            ('odd_week', 'Odd Weeks Only'),
        ],
        string='Schedule Pattern',
        default='standard',
        required=True,
    )
    monday = fields.Boolean(string='Monday', default=True)
    tuesday = fields.Boolean(string='Tuesday', default=True)
    wednesday = fields.Boolean(string='Wednesday', default=True)
    thursday = fields.Boolean(string='Thursday', default=True)
    friday = fields.Boolean(string='Friday', default=True)
    saturday = fields.Boolean(string='Saturday', default=False)
    sunday = fields.Boolean(string='Sunday', default=False)
    time_from = fields.Float(
        string='Start Time',
        required=True,
        default=9.0,
    )
    time_to = fields.Float(
        string='End Time',
        required=True,
        default=17.0,
    )
    break_from = fields.Float(string='Break From')
    break_to = fields.Float(string='Break To')

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        active_id = self.env.context.get('active_id')
        if active_id and self.env.context.get('active_model') == 'hr.hospital.doctor':
            res['doctor_id'] = active_id
        return res

    @api.constrains('time_from', 'time_to')
    def _check_time_range(self):
        for record in self:
            if record.time_to <= record.time_from:
                raise ValidationError(
                    _("End time must be greater than start time!")
                )

    @api.constrains('break_from', 'break_to')
    def _check_break_range(self):
        for record in self:
            if record.break_from and record.break_to:
                if record.break_to <= record.break_from:
                    raise ValidationError(
                        _("Break end must be after break start!")
                    )
                if (record.break_from < record.time_from or
                        record.break_to > record.time_to):
                    raise ValidationError(
                        _("Break must be within working hours!")
                    )

    @api.constrains('num_weeks')
    def _check_num_weeks(self):
        for record in self:
            if record.num_weeks < 1:
                raise ValidationError(
                    _("Number of weeks must be at least 1!")
                )

    def action_generate_schedule(self):
        self.ensure_one()

        Schedule = self.env['hr.hospital.doctor.schedule']
        created_count = 0

        # Map day fields to day_of_week values
        day_mapping = {
            'monday': '0',
            'tuesday': '1',
            'wednesday': '2',
            'thursday': '3',
            'friday': '4',
            'saturday': '5',
            'sunday': '6',
        }

        # Get selected days
        selected_days = []
        for day_name, day_value in day_mapping.items():
            if getattr(self, day_name):
                selected_days.append((day_name, day_value))

        if not selected_days:
            raise ValidationError(_("Please select at least one working day!"))

        # Calculate dates for each week
        current_date = self.week_start

        for week_num in range(self.num_weeks):
            # Check schedule pattern
            week_number = current_date.isocalendar()[1]

            if self.schedule_pattern == 'even_week' and week_number % 2 != 0:
                current_date += timedelta(days=7)
                continue
            elif self.schedule_pattern == 'odd_week' and week_number % 2 == 0:
                current_date += timedelta(days=7)
                continue

            # Create schedule for each selected day
            for day_name, day_value in selected_days:
                # Calculate specific date for this day
                day_offset = int(day_value) - current_date.weekday()
                if day_offset < 0:
                    day_offset += 7
                specific_date = current_date + timedelta(days=day_offset)

                # Check if schedule already exists for this date
                existing = Schedule.search([
                    ('doctor_id', '=', self.doctor_id.id),
                    ('date', '=', specific_date),
                ])
                if existing:
                    continue

                # Create schedule record(s)
                if self.break_from and self.break_to:
                    # Split into two periods: before and after break
                    Schedule.create({
                        'doctor_id': self.doctor_id.id,
                        'day_of_week': day_value,
                        'date': specific_date,
                        'time_from': self.time_from,
                        'time_to': self.break_from,
                        'schedule_type': 'working',
                    })
                    Schedule.create({
                        'doctor_id': self.doctor_id.id,
                        'day_of_week': day_value,
                        'date': specific_date,
                        'time_from': self.break_to,
                        'time_to': self.time_to,
                        'schedule_type': 'working',
                    })
                    created_count += 2
                else:
                    # Single period
                    Schedule.create({
                        'doctor_id': self.doctor_id.id,
                        'day_of_week': day_value,
                        'date': specific_date,
                        'time_from': self.time_from,
                        'time_to': self.time_to,
                        'schedule_type': 'working',
                    })
                    created_count += 1

            current_date += timedelta(days=7)

        # Return action to show created schedules
        return {
            'type': 'ir.actions.act_window',
            'name': _('Generated Schedules'),
            'res_model': 'hr.hospital.doctor.schedule',
            'view_mode': 'list,form',
            'domain': [('doctor_id', '=', self.doctor_id.id)],
            'target': 'current',
        }
