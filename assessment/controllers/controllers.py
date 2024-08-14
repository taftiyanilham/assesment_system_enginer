import json
import base64
import logging

from odoo import api, fields, models, tools, _
from odoo import http
from odoo.http import request, Response
from datetime import datetime, time, date


class PemesananRuanganControllers(http.Controller):

    @http.route('/track/<path:number>', type='http', auth='public', website=True)
    def get_badge_count(self, number=None ,**kwargs):
        # model = post.get("model")
        # actions = request.env['ir.actions.server'].search([('model_id.model', '=', model)])
        # notification_count = self.find_notification_by_action(actions, model)[0]
        if not number:
            serialize = {
                'message': 'Data tidak ditemukan URL salah'
            }
            status = 404

        transaction = request.env['pemesanan.ruangan'].search([('number', '=', number)], limit=1)
        if transaction:
            transaction_history = request.env['riwayat.pemesanan'].search([('transaction_id', '=', transaction.id)])
            history_list = []
            for history in transaction_history:
                history_list.append({
                    'event': history.event,
                    'date': str(history.create_date)
                })
            print(number)
            serialize = {
                'ruangan': transaction.ruangan.name,
                'number': transaction.number,
                'tanggal': str(transaction.tanggal),
                'riwayat': history_list
            }
            status = 200
        else:
            serialize = {
                'message': 'Data tidak ditemukan'
            }
            status = 404

        return Response(
            json.dumps(serialize),
            content_type='application/json',
            status=status
        )
