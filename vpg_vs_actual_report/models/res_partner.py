from odoo import models, fields, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    customer_type_id = fields.Selection([('local', 'Local'), ('export', 'Export'), ('industrial', 'Industrial')],
                                        string='Customer Type')
