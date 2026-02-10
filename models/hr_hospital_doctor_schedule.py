import logging

from odoo import models, fields

_logger = logging.getLogger(__name__)


class HRHDoctorSchedule(models.Model):
    _name = 'hr.hospital.doctor.schedule'
    _description = 'Doctor Schedule'

    doctor_id = fields.Many2one(
        comodel_name='hr.hospital.doctor',
        string='Doctor',
        required=True,
        ondelete='cascade',
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
        string='Day of Week',
    )
    date = fields.Date(string='Specific Date')
    time_from = fields.Float(string='From')
    time_to = fields.Float(string='To')
    schedule_type = fields.Selection(
        selection=[
            ('working', 'Working Day'),
            ('vacation', 'Vacation'),
            ('sick_leave', 'Sick Leave'),
            ('conference', 'Conference'),
        ],
        string='Type',
        default='working',
    )
    notes = fields.Char(string='Notes')
