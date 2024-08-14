from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import re

TIPE_RUANGAN = [
    ('meeting_room_kecil', 'Meeting Room Kecil'),
    ('meeting_room_besar', 'Meeting Room Besar'),
    ('aula', 'Aula')
]

LOKASI_RUANGAN = [
    ('1a', '1A'),
    ('1b', '1B'),
    ('1c', '1C'),
    ('2a', '2a'),
    ('2b', '2B'),
    ('2c', '2C')
]

STATUS_PEMESANAN = [
    ('draft', 'Draft'),
    ('on_going', 'On Going'),
    ('done', 'Done')
]


sql_pattern = re.compile(r"(\bor\b|\band\b|--|;|/\*|\*/|union|select|drop|insert|update|delete)", re.IGNORECASE)

class MasterRuangan(models.Model):
    _name = 'master.ruangan'

    name = fields.Char(string="Nama Ruangan", required=True, sanitize=True)
    tipe_ruangan = fields.Selection(TIPE_RUANGAN, string='Tipe Ruangan', required=True)
    lokasi_ruangan = fields.Selection(LOKASI_RUANGAN, string="Lokasi Ruangan", required=True)
    photo = fields.Binary(string="Foto Ruangan", required=True)
    kapasitas = fields.Integer(string="Kapasitas Ruangan", required=True)
    notes = fields.Text(string="Keterangan", sanitize=True)

    @api.model
    def create(self, vals):
        name = vals.get('name')
        # Check Nama
        exist_name = self.search_count([('name', '=', name)])
        if exist_name > 0:
            raise ValidationError("Nama sudah dipakai!")
            # Check SQL injection di text field dan char field
        if sql_pattern.search(vals.get('name')):
            raise ValidationError('Not Valid Name')
        if sql_pattern.search(vals.get('notes')):
            raise ValidationError('Not Valid Notes')
        return super(MasterRuangan, self).create(vals)

    # Check apakah ada nama yang sama
    @api.onchange('name')
    def _onchange_name(self):
        for rec in self:
            if rec.name:
                check = self.env['master.ruangan'].search_count([('name', '=', rec.name)])
                if check > 0:
                    raise ValidationError('Nama sudah digunakan!')
                else:
                    if sql_pattern.search(rec.name):
                        raise ValidationError('Not Valid Name')
                    else:
                        continue

    @api.onchange('notes')
    def _onchange_notes(self):
        for rec in self:
            if rec.notes:
                if sql_pattern.search(rec.notes):
                    raise ValidationError('Not Valid Notes')
                else:
                    continue


class PemesananRuangan(models.Model):
    _name = 'pemesanan.ruangan'
    _description = 'Model Pemesanan Ruangan'
    _rec_name = 'number'

    number = fields.Char(string="Nomor Pemesanan", required=True, default=lambda self: _('New'))
    ruangan = fields.Many2one('master.ruangan', string="Ruangan", required=True)
    name = fields.Char(string="Nama Pemesanan", required=True, sanitize=True)
    tanggal = fields.Date(string="Tanggal Pemesanan", required=True)
    state = fields.Selection(STATUS_PEMESANAN, string="Status Pemesanan", default='draft')
    notes = fields.Text(string="Catatan", sanitize=True)
    riwayat_pemesanan = fields.One2many('riwayat.pemesanan', 'transaction_id', string="Riwayat Pemesanan")

    @api.model
    def create(self, vals):
        ruangan = self.env['master.ruangan'].browse(vals.get('ruangan'))
        tipe_ruangan = ruangan.tipe_ruangan.upper()
        if vals.get('number', 'New') == 'New':
            number = self.env['ir.sequence'].next_by_code('pemesanan.ruangan') or 'New'
            print(number)
            vals['number'] = f"BOOKING-{tipe_ruangan}/{vals.get('tanggal')}/{number}"
        name = vals.get('name')
        # Check Nama
        exist_name = self.search_count([('name', '=', name)])
        if exist_name > 0:
            raise ValidationError("Nama sudah dipakai!")
        ruangan = vals.get('ruangan')
        tanggal = vals.get('tanggal')
        # Check tanggal dan ruangan
        exist_tanggal = self.search_count([('ruangan', '=', ruangan), ('tanggal', '=', tanggal)])
        if exist_tanggal > 0:
            raise ValidationError(f"Pemesanan untuk ruangan tersebut dengan tanggal {tanggal} sudah penuh!")

        # Check SQL injection di text field dan char field
        if sql_pattern.search(vals.get('name')):
            raise ValidationError('Not Valid Name')
        if sql_pattern.search(vals.get('notes')):
            raise ValidationError('Not Valid Notes')

        res = super(PemesananRuangan, self).create(vals)
        self.env['riwayat.pemesanan'].create({
            'transaction_id': res.id,
            'event': 'Pemesanan Dibuat'
        })
        return res

    @api.onchange('notes')
    def _onchange_notes(self):
        for rec in self:
            if rec.notes:
                if sql_pattern.search(rec.notes):
                    raise ValidationError('Not Valid Notes')
                else:
                    continue

    # Check ubah name
    @api.onchange('name')
    def _onchange_name(self):
        for rec in self:
            if rec.name:
                check_count = self.search_count([('name', '=', rec.name)])
                if check_count > 0:
                    raise ValidationError("Nama sudah dipakai!")
                if sql_pattern.search(rec.name):
                    raise ValidationError('Not Valid Name')


    @api.onchange('tanggal')
    def _onchange_tanggal(self):
        for rec in self:
            if rec.tanggal:
                check_count = self.search_count([('ruangan', '=', rec.ruangan.id), ('tanggal', '=', rec.tanggal)])
                if check_count > 0:
                    raise ValidationError(f"Pemesanan untuk {rec.ruangan.name} tersebut dengan tanggal {rec.tanggal} "
                                          f"sudah penuh")

    @api.onchange('ruangan')
    def _onchange_ruangan(self):
        for rec in self:
            if rec.ruangan:
                check_count = self.search_count([('ruangan', '=', rec.ruangan.id), ('tanggal', '=', rec.tanggal)])
                if check_count > 0:
                    raise ValidationError(f"Pemesanan untuk {rec.ruangan.name} tersebut dengan tanggal {rec.tanggal} "
                                          f"sudah penuh")


    def proses_pemesanan(self):

        if self.state == 'draft':
            event = f"Update pesanan: status Draft -> On Going"
            self.state = 'on_going'
            self.env['riwayat.pemesanan'].create({
                'transaction_id': self.id,
                'event': event
            })
        elif self.state == 'on_going':
            event = f"Update pesanan: Pesanan selesai"
            self.state = 'done'
            self.env['riwayat.pemesanan'].create({
                'transaction_id': self.id,
                'event': event
            })
        else:
            raise ValidationError("Sudah di akhir")


class RiwayatPemesanan(models.Model):
    _name = 'riwayat.pemesanan'
    _description = "Model Riwayat Pemesanan"

    transaction_id = fields.Many2one('pemesanan.ruangan', string="Transaksi")
    event = fields.Char(string="Event")
