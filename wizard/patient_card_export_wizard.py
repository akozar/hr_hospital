import json
import csv
import io
import base64
import logging
from datetime import datetime

from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)


class PatientCardExportWizard(models.TransientModel):
    _name = 'patient.card.export.wizard'
    _description = 'Patient Card Export Wizard'

    patient_id = fields.Many2one(
        comodel_name='hr.hospital.patient',
        string='Patient',
        required=True,
    )
    date_from = fields.Date(string='Date From')
    date_to = fields.Date(string='Date To')
    include_diagnoses = fields.Boolean(
        string='Include Diagnoses',
        default=True,
    )
    include_recommendations = fields.Boolean(
        string='Include Recommendations',
        default=True,
    )
    lang_id = fields.Many2one(
        comodel_name='res.lang',
        string='Report Language',
    )
    export_format = fields.Selection(
        selection=[
            ('json', 'JSON'),
            ('csv', 'CSV'),
        ],
        string='Export Format',
        default='json',
        required=True,
    )
    # For file download
    export_file = fields.Binary(string='Export File', readonly=True)
    export_filename = fields.Char(string='Filename', readonly=True)

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        active_id = self.env.context.get('active_id')
        if active_id and self.env.context.get('active_model') == 'hr.hospital.patient':
            patient = self.env['hr.hospital.patient'].browse(active_id)
            res['patient_id'] = active_id
            if patient.lang_id:
                res['lang_id'] = patient.lang_id.id
        return res

    @api.onchange('patient_id')
    def _onchange_patient_id(self):
        if self.patient_id and self.patient_id.lang_id:
            self.lang_id = self.patient_id.lang_id

    def _get_visits(self):
        domain = [('patient_id', '=', self.patient_id.id)]
        if self.date_from:
            domain.append(('scheduled_time', '>=',
                datetime.combine(self.date_from, datetime.min.time())))
        if self.date_to:
            domain.append(('scheduled_time', '<=',
                datetime.combine(self.date_to, datetime.max.time())))
        return self.env['hr.hospital.patient.visit'].search(
            domain, order='scheduled_time'
        )

    def _build_export_data(self):
        patient = self.patient_id
        visits = self._get_visits()

        data = {
            'patient': {
                'name': patient.name or '',
                'birth_date': str(patient.birth_date) if patient.birth_date else '',
                'age': patient.age,
                'gender': patient.gender or '',
                'blood_group': patient.blood_group or '',
                'allergies': patient.allergies or '',
                'personal_doctor': patient.doctor_id.name if patient.doctor_id else '',
            },
            'visits': []
        }

        for visit in visits:
            visit_data = {
                'date': str(visit.scheduled_time) if visit.scheduled_time else '',
                'doctor': visit.doctor_id.name if visit.doctor_id else '',
                'type': visit.visit_type or '',
                'status': visit.state or '',
            }

            if self.include_diagnoses:
                visit_data['diagnoses'] = [{
                    'disease': d.disease_id.name if d.disease_id else '',
                    'description': d.description or '',
                    'severity': d.severity or '',
                    'treatment': d.treatment or '',
                    'approved': d.is_approved,
                } for d in visit.diagnosis_ids]

            if self.include_recommendations:
                visit_data['recommendations'] = visit.recommendations or ''

            data['visits'].append(visit_data)

        return data

    def _export_json(self, data):
        return json.dumps(data, indent=2, ensure_ascii=False)

    def _export_csv(self, data):
        output = io.StringIO()
        writer = csv.writer(output)

        # Patient info header
        writer.writerow(['Patient Information'])
        writer.writerow(['Name', data['patient']['name']])
        writer.writerow(['Birth Date', data['patient']['birth_date']])
        writer.writerow(['Age', data['patient']['age']])
        writer.writerow(['Gender', data['patient']['gender']])
        writer.writerow(['Blood Group', data['patient']['blood_group']])
        writer.writerow(['Allergies', data['patient']['allergies']])
        writer.writerow(['Personal Doctor', data['patient']['personal_doctor']])
        writer.writerow([])

        # Visits header
        headers = ['Visit Date', 'Doctor', 'Type', 'Status']
        if self.include_diagnoses:
            headers.extend(['Disease', 'Severity', 'Description'])
        if self.include_recommendations:
            headers.append('Recommendations')

        writer.writerow(['Visits'])
        writer.writerow(headers)

        for visit in data['visits']:
            if self.include_diagnoses and visit.get('diagnoses'):
                for diag in visit['diagnoses']:
                    row = [
                        visit['date'],
                        visit['doctor'],
                        visit['type'],
                        visit['status']
                    ]
                    row.extend([
                        diag['disease'],
                        diag['severity'],
                        diag['description']
                    ])
                    if self.include_recommendations:
                        row.append(visit.get('recommendations', ''))
                    writer.writerow(row)
            else:
                row = [
                    visit['date'],
                    visit['doctor'],
                    visit['type'],
                    visit['status']
                ]
                if self.include_diagnoses:
                    row.extend(['', '', ''])
                if self.include_recommendations:
                    row.append(visit.get('recommendations', ''))
                writer.writerow(row)

        return output.getvalue()

    def action_export(self):
        self.ensure_one()

        data = self._build_export_data()

        if self.export_format == 'json':
            content = self._export_json(data)
            filename = f"patient_card_{self.patient_id.id}.json"
        else:
            content = self._export_csv(data)
            filename = f"patient_card_{self.patient_id.id}.csv"

        # Encode and save
        self.export_file = base64.b64encode(content.encode('utf-8'))
        self.export_filename = filename

        # Return download action
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content?model={self._name}&id={self.id}'
                   f'&field=export_file&filename_field=export_filename&download=true',
            'target': 'new',
        }
