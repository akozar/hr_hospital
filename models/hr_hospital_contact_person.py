import logging

from odoo import models, fields

_logger = logging.getLogger(__name__)


class HRHContactPerson(models.Model):
    _name = 'hr.hospital.contact.person'
    _description = 'Contact Person'
    _inherit = ['hr.hospital.abstract.person']
