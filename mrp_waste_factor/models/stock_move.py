from odoo import models, fields, api, _
from odoo.exceptions import UserError


class StockMove(models.Model):
    _inherit = 'stock.move'

    forecast_waste_factor = fields.Float(string="Forecast Waste Factor",
                                         compute='compute_waste_factor',
                                         store=True)
    actual_waste_factor = fields.Float(string="Actual Waste Factor")
    waste_factor_variance = fields.Float(string='Waste Factor Variance')
    forecast_waste_cost = fields.Float(string='Forecast Waste Cost',
                                       compute='compute_waste_cost', store=True)
    actual_waste_cost = fields.Float(string='Actual Waste Cost',
                                     compute='compute_waste_cost', store=True)
    forecast_waste_quantity = fields.Float(string='Forecast Waste Quantity',
                                           compute='compute_waste_quantity',
                                           store=True)
    actual_waste_quantity = fields.Float(string='Actual Waste Quantity',
                                         compute='compute_waste_quantity',
                                         store=True)

    @api.depends('raw_material_production_id.product_id',
                 'raw_material_production_id.bom_id',
                 'raw_material_production_id.product_id.tag_id',
                 'raw_material_production_id.bom_id.bom_line_ids')
    def compute_waste_factor(self):
        for rec in self:
            if rec.raw_material_production_id.product_id.tag_id == 'semi' and not rec.raw_material_production_id.bom_id:
                rec.forecast_waste_factor = 0.05
            elif rec.raw_material_production_id.bom_id.bom_line_ids.filtered(
                    lambda x: x.product_id.id == rec.product_id.id):
                rec.forecast_waste_factor = sum(
                    rec.raw_material_production_id.bom_id.bom_line_ids.filtered(
                        lambda x: x.product_id.id == rec.product_id.id).mapped(
                        'bom_waste_factor'))
            else:
                rec.forecast_waste_factor = 0.0

    @api.onchange('actual_waste_factor')
    def waste_variance(self):
        for rec in self:
            if rec.actual_waste_factor:
                rec.waste_factor_variance = rec.forecast_waste_factor - rec.actual_waste_factor
                # rec.waste_factor_percent = rec.waste_factor_variance
            else:
                rec.waste_factor_variance = 0.0

    @api.depends('raw_material_production_id.bom_id.bom_line_ids.product_qty',
                 'product_uom_qty', 'actual_waste_factor')
    def compute_waste_quantity(self):
        for rec in self:
            if rec.product_uom_qty:
                rec.forecast_waste_quantity = rec.product_uom_qty * rec.forecast_waste_factor
                rec.actual_waste_quantity = rec.product_uom_qty * rec.actual_waste_factor

    @api.depends('product_id.standard_price',
                 'raw_material_production_id.bom_id', 'actual_waste_factor')
    def compute_waste_cost(self):
        for rec in self:
            if rec.product_id:
                rec.forecast_waste_cost = rec.product_id.standard_price * rec.forecast_waste_factor
                rec.actual_waste_cost = rec.product_id.standard_price * rec.actual_waste_factor

    def _generate_valuation_lines_data(self, partner_id, qty, debit_value,
                                       credit_value, debit_account_id,
                                       credit_account_id, description):
        # This method returns a dictionary to provide an easy extension hook to modify the valuation lines (see purchase for an example)
        self.ensure_one()
        debit_line_vals = {
            'name': description,
            'product_id': self.product_id.id,
            'quantity': qty,
            'product_uom_id': self.product_id.uom_id.id,
            'ref': description,
            'partner_id': partner_id,
            'debit': debit_value if debit_value > 0 else 0,
            'credit': -debit_value if debit_value < 0 else 0,
            'account_id': debit_account_id,
            'forecast_waste_factor': self.forecast_waste_factor,
            'actual_waste_factor': self.actual_waste_factor,
            'waste_factor_variance': self.waste_factor_variance,
            'forecast_waste_cost': self.forecast_waste_cost,
            'actual_waste_cost': self.actual_waste_cost,
            'forecast_waste_quantity': self.forecast_waste_quantity,
            'actual_waste_quantity': self.actual_waste_quantity,
        }

        credit_line_vals = {
            'name': description,
            'product_id': self.product_id.id,
            'quantity': qty,
            'product_uom_id': self.product_id.uom_id.id,
            'ref': description,
            'partner_id': partner_id,
            'credit': credit_value if credit_value > 0 else 0,
            'debit': -credit_value if credit_value < 0 else 0,
            'account_id': credit_account_id,
            'forecast_waste_factor': self.forecast_waste_factor,
            'actual_waste_factor': self.actual_waste_factor,
            'waste_factor_variance': self.waste_factor_variance,
            'forecast_waste_cost': self.forecast_waste_cost,
            'actual_waste_cost': self.actual_waste_cost,
            'forecast_waste_quantity': self.forecast_waste_quantity,
            'actual_waste_quantity': self.actual_waste_quantity,
        }

        rslt = {'credit_line_vals': credit_line_vals,
                'debit_line_vals': debit_line_vals}
        if credit_value != debit_value:
            # for supplier returns of product in average costing method, in anglo saxon mode
            diff_amount = debit_value - credit_value
            price_diff_account = self.product_id.property_account_creditor_price_difference

            if not price_diff_account:
                price_diff_account = self.product_id.categ_id.property_account_creditor_price_difference_categ
            if not price_diff_account:
                raise UserError(
                    _('Configuration error. Please configure the price difference account on the product or its category to process this operation.'))

            rslt['price_diff_line_vals'] = {
                'name': self.name,
                'product_id': self.product_id.id,
                'quantity': qty,
                'product_uom_id': self.product_id.uom_id.id,
                'ref': description,
                'partner_id': partner_id,
                'credit': diff_amount > 0 and diff_amount or 0,
                'debit': diff_amount < 0 and -diff_amount or 0,
                'account_id': price_diff_account.id,
                'forecast_waste_factor': self.forecast_waste_factor,
                'actual_waste_factor': self.actual_waste_factor,
                'waste_factor_variance': self.waste_factor_variance,
                'forecast_waste_cost': self.forecast_waste_cost,
                'actual_waste_cost': self.actual_waste_cost,
                'forecast_waste_quantity': self.forecast_waste_quantity,
                'actual_waste_quantity': self.actual_waste_quantity,
            }
        return rslt
