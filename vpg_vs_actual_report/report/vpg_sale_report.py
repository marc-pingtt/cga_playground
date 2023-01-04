from odoo import api, models, _


class VPGOrder(models.AbstractModel):
    _name = 'report.vpg_vs_actual_report.vpg_sale_report'

    @api.model
    def _get_report_values(self, docids, data=None):
        if self.env.context.get('vpg_order_report'):

            if data.get('report_data'):
                data.update({'report_main_line_data': data,
                             'Filters': data.get('report_data')['report_filter'],
                             'company': self.env.company,
                             })
            return data
