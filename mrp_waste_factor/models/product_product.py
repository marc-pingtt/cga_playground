from odoo import models, fields


class ProductInherit(models.Model):
    _inherit = 'product.product'

    tag_id = fields.Selection(
        [('semi', 'Semi Finished'), ('finished', 'Finished'),
         ('material', 'Material')],
        string='Tags')
