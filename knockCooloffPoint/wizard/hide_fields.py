# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class HideFields(models.TransientModel):
    _name = 'hide.fields.wizard'
    _description = "Hide Fields Wizard"


    partner_id = fields.Many2one('res.partner',string="Partner")
    primary_phone = fields.Char(related='partner_id.x_primary_phone', string='Primary Phone')
    secondary_phone = fields.Char(related='partner_id.x_secondary_phone', string='Secondary Phone')
    other_phone = fields.Char(related='partner_id.x_other_phone', string='Other Phone')
    primary_email = fields.Char(related='partner_id.x_primary_email', string='Primary Email')
    secondary_email = fields.Char(related='partner_id.x_secondary_email', string='Secondary Email')
    other_email = fields.Char(related='partner_id.x_other_email', string='Other Email')
