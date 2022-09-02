# -*- coding: utf-8 -*-
import datetime 
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class KnockHistory(models.Model):
    _name = 'knock.history'

    partner_id = fields.Many2one('res.partner', string="Parnter")
    user_id = fields.Many2one('res.users', string="User")
    history_date = fields.Date(string="Time")


class Users(models.Model):
    _inherit = 'res.users'

    cool_off_days = fields.Integer(string='Cool off days')
    knocked_days = fields.Integer(string='knocked days', default=30)
    available_credit = fields.Integer(string='Available Credit')
    monthaly_credit = fields.Integer(string='Monthaly Credit')
    cooloff_start_day = fields.Date(string="CoolOff start Day")

    @api.onchange('cool_off_days')
    def _onchange_cool_off_days(self):
        if self.cool_off_days:
            self.cooloff_start_day = False

    def cron_knock_credit_monthly(self):
        all_users = self.search([])
        for rec in all_users:
            rec.available_credit = rec.monthaly_credit

class Partner(models.Model):
    _inherit = 'res.partner'

    z_time = fields.Integer(string='Z Time')
    knock_history_ids = fields.One2many('knock.history', 'partner_id', string="Knock History")

    def check_contact_info_exsit(self):
        for record in self:
            is_detail_exist = False
            if record.x_primary_phone or record.x_secondary_email or record.x_other_email or \
                record.x_secondary_phone or record.x_other_phone or record.x_primary_email:
                    is_detail_exist = True
            return is_detail_exist

    def open_contect_detail_wiz(self):
        is_detail_exist = self.check_contact_info_exsit()
        active_user = self.env.user
        if is_detail_exist:
            login_user_history_ids = self.env['knock.history'].search([('user_id', '=', active_user.id)])
            if not login_user_history_ids:
                if active_user.available_credit <= 0:
                    raise UserError("Sorry, out of credit. Please call support.")
                if active_user.available_credit > 0:
                    active_user.available_credit -= 1
                    self.env.user.cooloff_start_day = fields.Datetime.now()
            # found_diff_partner_ids = login_user_history_ids.filtered(lambda x: x.partner_id==self.id)
            # if not found_diff_partner_ids:
            #     if active_user.available_credit <= 0:
            #         raise UserError("Sorry, out of credit. Please call support.")
            #     if active_user.available_credit > 0:
            #         active_user.available_credit -= 1
                    self.env.user.cooloff_start_day = fields.Datetime.now()
        self.update({'knock_history_ids': [
                (0,0, {
                    'partner_id': self.id,
                    'user_id': self.env.user.id,
                    'history_date': fields.Datetime.now()
                })
            ]})

        if is_detail_exist:
            user_cooloff_day = self.env.user.cool_off_days
            if not self.env.user.cooloff_start_day:
                self.env.user.cooloff_start_day = fields.Datetime.now()
            end_date = self.env.user.cooloff_start_day + datetime.timedelta(days=user_cooloff_day)

            if fields.Date.today() >= end_date:
                last30_date = fields.Date.today() - datetime.timedelta(days=30)
                get_last_30_entry = self.env['knock.history'].search([
                    ('partner_id', '=', self.id),
                    ('history_date', '<=', fields.Date.today()),
                    ('history_date', '>=', last30_date)])

                if len(get_last_30_entry) > self.z_time:
                    raise UserError("Sorry, this contact has been knocked enough!")
                if active_user.available_credit <= 0:
                    raise UserError("Sorry, out of credit. Please call support.")
                if active_user.available_credit > 0:
                    active_user.available_credit -= 1
                    self.env.user.cooloff_start_day = fields.Datetime.now()
            else:
                last30_date = fields.Date.today() - datetime.timedelta(days=30)
                get_last_30_entry = self.env['knock.history'].search([
                    ('partner_id', '=', self.id),
                    ('history_date', '<=', fields.Date.today()),
                    ('history_date', '>=', last30_date)])

                if len(get_last_30_entry) > self.z_time:
                    raise UserError("Sorry, this contact has been knocked enough!")
                if active_user.available_credit <= 0:
                    raise UserError("Sorry, out of credit. Please call support.")
                # if active_user.available_credit > 0:
                    # active_user.available_credit -= 1

        action = {
                'name': _('Contact Detail'),
                'view_mode': 'form',
                'res_model': 'hide.fields.wizard',
                'type': 'ir.actions.act_window',
                'context': {'default_partner_id': self.id},
                'target': 'new'
            }
        return action
