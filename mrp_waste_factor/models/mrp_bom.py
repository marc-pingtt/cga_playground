from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class WasteFactor(models.Model):
    _inherit = 'mrp.bom.line'

    bom_waste_factor = fields.Float(string='Waste Factor')

    @api.onchange('product_id')
    def onchange_product_factor(self):
        if self.product_id:
            self.bom_waste_factor = 0.05

    @api.constrains('bom_waste_factor')
    def check_quantity(self):
        for rec in self:
            if rec.bom_waste_factor > 0.0 and not rec.bom_waste_factor <= 5.0:
                raise ValidationError(
                    _('The Waste Factor Should be in range up to 5'))
