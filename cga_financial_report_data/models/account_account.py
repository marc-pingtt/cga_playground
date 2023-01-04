from odoo import models, fields


class AccountAccount(models.Model):
    _inherit = 'account.account'

    div_id = fields.Many2one('account.division', string='Division')
