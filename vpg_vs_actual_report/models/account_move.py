from odoo import models, fields,api


class AccountMove(models.Model):
    _inherit = 'account.move'

    customer_type_id = fields.Selection([('local', 'Local'), ('export', 'Export'), ('industrial', 'Industrial')],
                                        string='Customer Type')

    @api.onchange('partner_id')
    def onchange_partner(self):
        if self.partner_id:
            if self.partner_id.customer_type_id == 'local':
                self.customer_type_id = 'local'
            if self.partner_id.customer_type_id == 'export':
                self.customer_type_id = 'export'
            if self.partner_id.customer_type_id == 'industrial':
                self.customer_type_id = 'industrial'

