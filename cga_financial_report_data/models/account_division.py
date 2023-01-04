from odoo import models, fields


class AccountDivision(models.Model):
    _name = 'account.division'

    name = fields.Char(string='Division')
