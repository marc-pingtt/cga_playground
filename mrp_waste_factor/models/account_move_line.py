from odoo import models, fields


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    forecast_waste_factor = fields.Float(string='Forecast Waste Factor')
    actual_waste_factor = fields.Float(string='Actual Waste Factor')
    waste_factor_variance = fields.Float(string='Waste Factor Variance')
    forecast_waste_cost = fields.Float(string='Forecast Waste Cost')
    actual_waste_cost = fields.Float(string='Actual Waste Cost')
    forecast_waste_quantity = fields.Float(string='Forecast Waste Quantity')
    actual_waste_quantity = fields.Float(string='Actual Waste Quantity')


