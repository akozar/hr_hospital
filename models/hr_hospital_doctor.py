import logging
from datetime import date

from odoo import models, fields, api
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class HRHDoctor(models.Model):
    _name = "hr.hospital.doctor"
    _description = "Doctor"
    _inherit = ['hr.hospital.abstract.person']

    _check_rating_range = models.Constraint(
        'CHECK(rating >= 0 AND rating <= 5)',
        'Rating must be between 0.00 and 5.00!',
    )
    _unique_license_number = models.Constraint(
        'UNIQUE(license_number)',
        'License number must be unique!',
    )

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
    )
    is_intern = fields.Boolean(default=False)
    mentor_id = fields.Many2one(
        comodel_name='hr.hospital.doctor',
        domain=[('is_intern', '=', False)],
    )
    license_number = fields.Char(
        required=True,
        copy=False,
    )
    license_date = fields.Date(string='License Issue Date')
    experience_years = fields.Integer(
        string='Experience (Years)',
        compute='_compute_experience_years',
    )
    rating = fields.Float(digits=(3, 2))
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

    @api.depends('name', 'specialty_id')
    def _compute_display_name(self):
        for record in self:
            if record.specialty_id:
                record.display_name = f"{record.name} ({record.specialty_id.name})"
            else:
                record.display_name = record.name or ""

    @api.constrains('mentor_id')
    def _check_mentor_not_intern(self):
        for record in self:
            if record.mentor_id and record.mentor_id.is_intern:
                raise ValidationError(self.env._("Mentor cannot be an intern!"))

    @api.constrains('mentor_id')
    def _check_mentor_not_self(self):
        for record in self:
            if record.mentor_id and record.mentor_id == record:
                raise ValidationError(self.env._("Doctor cannot be their own mentor!"))

    def write(self, vals):
        if 'active' in vals and not vals['active']:
            for record in self:
                active_visits = self.env['hr.hospital.patient.visit'].search([
                    ('doctor_id', '=', record.id),
                    ('state', '=', 'scheduled'),
                ])
                if active_visits:
                    raise ValidationError(
                        self.env._(
                            "Cannot archive doctor '%(name)s' with active scheduled visits!",
                            name=record.name,
                        )
                    )
        return super().write(vals)
