import logging
from datetime import date

from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class HRHDoctor(models.Model):
    _name = "hr.hospital.doctor"
    _description = "Doctor"
    _inherit = ['hr.hospital.abstract.person']

    active = fields.Boolean(default=True)
    description = fields.Text()

    supervisor_id = fields.Many2one(
        comodel_name='hr.hospital.doctor',
        string='Supervisor Doctor',
    )
    user_id = fields.Many2one(
        comodel_name='res.users',
        string='System User',
    )
    specialty_id = fields.Many2one(
        comodel_name='hr.hospital.doctor.specialty',
        string='Specialty',
    )
    is_intern = fields.Boolean(string='Intern', default=False)
    mentor_id = fields.Many2one(
        comodel_name='hr.hospital.doctor',
        string='Mentor',
    )
    license_number = fields.Char(
        string='License Number',
        required=True,
        copy=False,
    )
    license_date = fields.Date(string='License Issue Date')
    experience_years = fields.Integer(
        string='Experience (Years)',
        compute='_compute_experience_years',
    )
    rating = fields.Float(string='Rating', digits=(3, 2))
    schedule_ids = fields.One2many(
        comodel_name='hr.hospital.doctor.schedule',
        inverse_name='doctor_id',
        string='Work Schedule',
    )
    education_country_id = fields.Many2one(
        comodel_name='res.country',
        string='Country of Education',
    )

    res_partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Contact',
    )

    @api.depends('license_date')
    def _compute_experience_years(self):
        today = date.today()
        for record in self:
            if record.license_date:
                delta = today - record.license_date
                record.experience_years = delta.days // 365
            else:
                record.experience_years = 0
