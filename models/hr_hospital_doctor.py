import logging

from odoo import models, fields

_logger = logging.getLogger(__name__)

class HRHDoctor(models.Model):
    _name = "hr.hospital.doctor"
    _description = "Doctor"

    name = fields.Char()

    active = fields.Boolean(
        default=True, )
    description = fields.Text()

    supervisor_id = fields.Many2one(
        comodel_name='hr.hospital.doctor',
        string='Supervisor Doctor'
    )

    res_partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Contact'
    )
