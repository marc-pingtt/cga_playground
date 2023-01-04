from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    post_enable = fields.Boolean(string='Enable Account Post', default=False)
    post_waste_ac = fields.Many2one('account.account',
                                    string='Post Waste Account',
                                    config_parameter='mrp_waste_factor.post_waste_ac')
