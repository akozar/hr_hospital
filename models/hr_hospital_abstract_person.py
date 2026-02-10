import logging
import re
from datetime import date

from odoo import models, fields, api
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class AbstractPerson(models.AbstractModel):
    _name = 'hr.hospital.abstract.person'
    _description = 'Abstract Person'
    _inherit = ['image.mixin']

    # Name fields (ПІБ)
    surname = fields.Char(string='Surname')
    first_name = fields.Char(string='First Name')
    patronymic = fields.Char(string='Patronymic')

    # Computed full name
    name = fields.Char(
        string='Full Name',
        compute='_compute_name',
        store=True,
    )

    # Contact info with validation
    phone = fields.Char(string='Phone')
    email = fields.Char(string='Email')

    # Gender selection
    gender = fields.Selection(
        selection=[
            ('male', 'Male'),
            ('female', 'Female'),
            ('other', 'Other'),
        ],
        string='Gender',
    )

    # Birth date and computed age
    birth_date = fields.Date(string='Date of Birth')
    age = fields.Integer(
        string='Age',
        compute='_compute_age',
    )

    # Related fields
    country_id = fields.Many2one(
        comodel_name='res.country',
        string='Country of Citizenship',
    )
    lang_id = fields.Many2one(
        comodel_name='res.lang',
        string='Communication Language',
    )

    @api.depends('surname', 'first_name', 'patronymic')
    def _compute_name(self):
        for record in self:
            parts = filter(None, [record.surname, record.first_name, record.patronymic])
            record.name = ' '.join(parts) or False

    @api.depends('birth_date')
    def _compute_age(self):
        today = date.today()
        for record in self:
            if record.birth_date:
                bd = record.birth_date
                record.age = today.year - bd.year - ((today.month, today.day) < (bd.month, bd.day))
            else:
                record.age = 0

    @api.constrains('phone')
    def _check_phone(self):
        phone_pattern = re.compile(r'^\+?[\d\s\-\(\)]{7,20}$')
        for record in self:
            if record.phone and not phone_pattern.match(record.phone):
                raise ValidationError("Invalid phone format")

    @api.constrains('email')
    def _check_email(self):
        email_pattern = re.compile(r'^[\w\.-]+@[\w\.-]+\.\w+$')
        for record in self:
            if record.email and not email_pattern.match(record.email):
                raise ValidationError("Invalid email format")

    @api.constrains('birth_date')
    def _check_age_positive(self):
        today = date.today()
        for record in self:
            if record.birth_date:
                if record.birth_date > today:
                    raise ValidationError("Birth date cannot be in the future!")
                bd = record.birth_date
                age = today.year - bd.year - ((today.month, today.day) < (bd.month, bd.day))
                if age <= 0:
                    raise ValidationError("Age must be greater than 0!")
