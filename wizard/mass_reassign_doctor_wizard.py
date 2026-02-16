import logging

from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class MassReassignDoctorWizard(models.TransientModel):
    _name = 'mass.reassign.doctor.wizard'
    _description = 'Mass Reassign Doctor Wizard'

    new_doctor_id = fields.Many2one(
        comodel_name='hr.hospital.doctor',
        string='New Doctor',
        required=True,
    )
    patient_ids = fields.Many2many(
        comodel_name='hr.hospital.patient',
        string='Patients',
    )
    change_date = fields.Date(
        string='Change Date',
        default=fields.Date.today,
        required=True,
    )
    reason = fields.Text(
        string='Reason for Change',
        required=True,
    )

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        # Get selected patients from context
        active_ids = self.env.context.get('active_ids', [])
        if active_ids:
            res['patient_ids'] = [(6, 0, active_ids)]
        return res

    def action_reassign(self):
        for patient in self.patient_ids:
            patient.write({
                'doctor_id': self.new_doctor_id.id,
            })
            # History is created automatically via Patient.write() override
            # Update reason in latest history record
            latest_history = self.env['hr.hospital.patient.doctor.history'].search([
                ('patient_id', '=', patient.id),
                ('active', '=', True),
            ], limit=1)
            if latest_history:
                latest_history.write({'reason': self.reason})
        return {'type': 'ir.actions.act_window_close'}
