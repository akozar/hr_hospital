import logging

from odoo import models, fields

_logger = logging.getLogger(__name__)


class HRHDoctorSchedule(models.Model):
    _name = 'hr.hospital.doctor.schedule'
    _description = 'Doctor Schedule'

    _check_time_range = models.Constraint(
        'CHECK(time_to > time_from)',
        'End time must be greater than start time!',
    )

    doctor_id = fields.Many2one(
        comodel_name='hr.hospital.doctor',
        required=True,
        ondelete='cascade',
        domain=[('specialty_id', '!=', False)],
    )
    day_of_week = fields.Selection(
        selection=[
            ('0', 'Monday'),
            ('1', 'Tuesday'),
            ('2', 'Wednesday'),
            ('3', 'Thursday'),
            ('4', 'Friday'),
            ('5', 'Saturday'),
            ('6', 'Sunday'),
        ],
    )
    date = fields.Date()
    time_from = fields.Float()
    time_to = fields.Float()
    schedule_type = fields.Selection(
        selection=[
            ('working', 'Working Day'),
            ('vacation', 'Vacation'),
            ('sick_leave', 'Sick Leave'),
            ('conference', 'Conference'),
        ],
        default='working',
    )
    notes = fields.Char()
