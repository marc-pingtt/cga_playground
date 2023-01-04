from odoo import models, fields, api


class ApprovalProductLine(models.Model):
    _inherit = 'approval.product.line'

    price_unit = fields.Float(string='Unit Price',required=True, digits='Product Price')
    price_subtotal = fields.Float(compute='_compute_amount_product', string='Subtotal', store=True)
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  default=lambda self: self.env.user.company_id.currency_id, tracking=True)

    @api.onchange('product_id')
    def product_onchange(self):
        for res in self:
            if res.product_id:
                res.price_unit = res.product_id.lst_price

    @api.depends('price_unit', 'quantity')
    def _compute_amount_product(self):
        for rec in self:
            if rec.product_id:
                rec.price_subtotal = rec.quantity * rec.price_unit




