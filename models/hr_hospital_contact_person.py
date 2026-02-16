import logging

from odoo import models, fields

_logger = logging.getLogger(__name__)


class HRHContactPerson(models.Model):
    _name = 'hr.hospital.contact.person'
    _description = 'Contact Person'
    _inherit = ['hr.hospital.abstract.person']

    patient_ids = fields.Many2many(
        comodel_name='hr.hospital.patient',
        string='Patients',
        domain=[('allergies', '!=', False)],
    )
