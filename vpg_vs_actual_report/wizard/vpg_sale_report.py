from odoo.exceptions import UserError, ValidationError

from odoo import models, fields, api, _


class VPGActualSale(models.Model):
    _name = 'vpg.actual.sale'

    date_from = fields.Datetime(string="Date From")
    date_to = fields.Datetime(string="Date to")
    report_type = fields.Selection([
        ('report_by_total', 'Report By Total'),
        ('report_by_local', 'Report By Local'),
        ('report_by_export', 'Report By Export'),
        ('report_by_industry', 'Report By Industrial')],
        default='report_by_total')

    @api.model
    def create(self, vals):
        # vals['target_move'] = 'posted'
        res = super(VPGActualSale, self).create(vals)
        return res

    @api.model
    def write(self, values, option):

        # if values.get('date_from', False) and values.get('date_to', False):
        #     if values['date_from'] > values['date_to']:
        #         raise ValidationError(_('Start Date must be greater than End Date'))

        report_values = self.env['vpg.actual.sale'].search([('id', '=', option)])
        data = {
            'report_type': report_values.report_type,
            'model': self,
        }

        if values.get('date_from', False):
            data.update({
                'date_from': values['date_from'],
            })

        if values.get('date_to', False):
            data.update({
                'date_to': values['date_to'],
            })


        approvals = self.env['approval.request']

        industry = approvals.search(
            [('category_id.name', '=', 'Industrial VPG Request'), ('request_status', '=', 'approved')])
        local = approvals.search([('category_id.name', '=', 'Local VPG Request'), ('request_status', '=', 'approved')])
        export = approvals.search(
            [('category_id.name', '=', 'Export VPG Request'), ('request_status', '=', 'approved')])

        domain = [('state', '=', 'posted')]

        if data.get('date_from', False):
            domain.append(('invoice_date', '>=', data.get('date_from')))

        if data.get('date_to', False):
            domain.append(('invoice_date', '<=', data.get('date_to')))


        invoice_data = self.env['account.move'].search(domain)
        product_cat = self.env['product.category'].search([])

        export_invoice_data_fil = invoice_data.filtered(lambda x: x.customer_type_id == 'export')
        local_invoice_data_fil = invoice_data.filtered(lambda y: y.customer_type_id == 'local')
        industrial_invoice_data_fil = invoice_data.filtered(lambda z: z.customer_type_id == 'industrial')

        loc_vals = []
        exp_vals = []
        ind_vals = []
        total_vals = []

        loc_categ = {}
        exp_categ = {}
        ind_categ = {}
        total_categ = {}

        if local_invoice_data_fil:
            inv_local_product_ids = local_invoice_data_fil.invoice_line_ids.mapped('product_id')
            local_forecast_vals = []
            count = 1
            for loc in inv_local_product_ids:
                inv_local_quantity = local_invoice_data_fil.invoice_line_ids.filtered(
                    lambda x: x.product_id.id == loc.id)
                fore_local_quantity = local.product_line_ids.filtered(lambda x: x.product_id.id == loc.id)
                for fore_loc in fore_local_quantity:
                    if inv_local_quantity:
                        val = {
                            'product': loc.name,
                            'product_cat': loc.categ_id.name,
                            'actual_qty': sum(inv_local_quantity.mapped(lambda x: x.quantity)),
                            'actual_total': sum(inv_local_quantity.mapped(lambda x: x.price_subtotal)),
                            'forecasted': sum(fore_loc.mapped(lambda x: x.quantity)),
                            'forecasted_total': sum(fore_loc.mapped(lambda x: x.price_subtotal))
                        }
                        if fore_loc:
                            local_forecast_vals.append(fore_loc.id)
                        loc_vals.append(val)
                        if loc_categ == {}:
                            loc_categ[loc.categ_id.name] = [val]
                        else:
                            if loc.categ_id.name in loc_categ.keys():
                                loc_categ[loc.categ_id.name].append(val)
                            else:
                                loc_categ[loc.categ_id.name] = [val]

                    count += 1

        if export_invoice_data_fil:
            inv_export_product_ids = export_invoice_data_fil.invoice_line_ids.mapped('product_id')
            export_forecast_vals = []
            count = 1
            for exp in inv_export_product_ids:
                inv_export_quantity = export_invoice_data_fil.invoice_line_ids.filtered(
                    lambda x: x.product_id.id == exp.id)
                fore_export_quantity = export.product_line_ids.filtered(lambda x: x.product_id.id == exp.id)
                for fore_exp in fore_export_quantity:
                    if inv_export_quantity:
                        val = {
                            'product': exp.name,
                            'product_cat': exp.categ_id.name,
                            'actual_qty': sum(inv_export_quantity.mapped(lambda x: x.quantity)),
                            'actual_total': sum(inv_export_quantity.mapped(lambda x: x.price_subtotal)),
                            'forecasted': sum(fore_exp.mapped(lambda x: x.quantity)),
                            'forecasted_total': sum(fore_exp.mapped(lambda x: x.price_subtotal)),
                        }
                        if fore_exp:
                            export_forecast_vals.append(fore_exp.id)
                        exp_vals.append(val)
                        if exp_categ == 0:
                            exp_categ[exp.categ_id.name] = [val]
                        else:
                            if exp.categ_id.id in exp_categ.keys():
                                exp_categ[exp.categ_id.name].append(val)
                            else:
                                exp_categ[exp.categ_id.name] = [val]
                    count += 1

        if industrial_invoice_data_fil:
            inv_industrial_product_ids = industrial_invoice_data_fil.invoice_line_ids.mapped('product_id')
            industrial_forecast_vals = []
            count = 1
            for ind in inv_industrial_product_ids:
                inv_industrial_quantity = industrial_invoice_data_fil.invoice_line_ids.filtered(
                    lambda x: x.product_id.id == ind.id)
                fore_industry_quantity = industry.product_line_ids.filtered(lambda x: x.product_id.id == ind.id)
                for fore_ind in fore_industry_quantity:
                    if inv_industrial_quantity:
                        val = {
                            'product': ind.name,
                            'product_cat': ind.categ_id.name,
                            'actual_qty': sum(inv_industrial_quantity.mapped(lambda x: x.quantity)),
                            'actual_total': sum(inv_industrial_quantity.mapped(lambda x: x.price_subtotal)),
                            'forecasted': sum(fore_ind.mapped(lambda x: x.quantity)),
                            'forecasted_total': sum(fore_ind.mapped(lambda x: x.price_subtotal))
                        }
                        if fore_ind:
                            industrial_forecast_vals.append(fore_ind.id)
                        ind_vals.append(val)
                        if ind_categ == 0:
                            ind_categ[ind.categ_id.name] = [val]
                        else:
                            if ind.categ_id.name in ind_categ.keys():
                                ind_categ[ind.categ_id.name].append(val)
                            else:
                                ind_categ[ind.categ_id.name] = [val]
                        count += 1

        if local_invoice_data_fil:
            inv_local_product_ids = local_invoice_data_fil.invoice_line_ids.mapped('product_id')
            local_forecast_vals = []
            count = 1
            for loc in inv_local_product_ids:
                inv_local_quantity = local_invoice_data_fil.invoice_line_ids.filtered(
                    lambda x: x.product_id.id == loc.id)
                fore_local_quantity = local.product_line_ids.filtered(lambda x: x.product_id.id == loc.id)
                for fore_loc in fore_local_quantity:
                    if inv_local_quantity:
                        val = {
                            'product': loc.name,
                            'product_cat': loc.categ_id.name,
                            'actual_qty': sum(inv_local_quantity.mapped(lambda x: x.quantity)),
                            'actual_total': sum(inv_local_quantity.mapped(lambda x: x.price_subtotal)),
                            'forecasted': sum(fore_loc.mapped(lambda x: x.quantity)),
                            'forecasted_total': sum(fore_loc.mapped(lambda x: x.price_subtotal))
                        }
                        if fore_loc:
                            local_forecast_vals.append(fore_loc.id)
                        total_vals.append(val)
                        if total_categ == 0:
                            total_categ[loc.categ_id.name] = [val]
                        else:
                            if loc.categ_id.name in total_categ.keys():
                                total_categ[loc.categ_id.name].append(val)
                            else:
                                total_categ[loc.categ_id.name] = [val]
                        count += 1
        if export_invoice_data_fil:
            inv_export_product_ids = export_invoice_data_fil.invoice_line_ids.mapped('product_id')
            export_forecast_vals = []
            count = 1
            for exp in inv_export_product_ids:
                inv_export_quantity = export_invoice_data_fil.invoice_line_ids.filtered(
                    lambda x: x.product_id.id == exp.id)
                fore_export_quantity = export.product_line_ids.filtered(lambda x: x.product_id.id == exp.id)
                for fore_exp in fore_export_quantity:
                    if inv_export_quantity:
                        val = {
                            'product': exp.name,
                            'product_cat': exp.categ_id.name,
                            'actual_qty': sum(inv_export_quantity.mapped(lambda x: x.quantity)),
                            'actual_total': sum(inv_export_quantity.mapped(lambda x: x.price_subtotal)),
                            'forecasted': sum(fore_exp.mapped(lambda x: x.quantity)),
                            'forecasted_total': sum(fore_exp.mapped(lambda x: x.price_subtotal)),
                        }
                        if fore_exp:
                            export_forecast_vals.append(fore_exp.id)
                        total_vals.append(val)

                        if total_categ == 0:
                            total_categ[exp.categ_id.name] = [val]
                        else:
                            if exp.categ_id.name in total_categ.keys():
                                total_categ[exp.categ_id.name].append(val)
                            else:
                                total_categ[exp.categ_id.name] = [val]
                        count += 1
        if industrial_invoice_data_fil:
            inv_industrial_product_ids = industrial_invoice_data_fil.invoice_line_ids.mapped('product_id')
            industrial_forecast_vals = []
            count = 1
            for ind in inv_industrial_product_ids:
                inv_industrial_quantity = industrial_invoice_data_fil.invoice_line_ids.filtered(
                    lambda x: x.product_id.id == ind.id)
                fore_industry_quantity = industry.product_line_ids.filtered(lambda x: x.product_id.id == ind.id)
                for fore_ind in fore_industry_quantity:
                    if inv_industrial_quantity:
                        val = {
                            'product': ind.name,
                            'product_cat': ind.categ_id.name,
                            'actual_qty': sum(inv_industrial_quantity.mapped(lambda x: x.quantity)),
                            'actual_total': sum(inv_industrial_quantity.mapped(lambda x: x.price_subtotal)),
                            'forecasted': sum(fore_ind.mapped(lambda x: x.quantity)),
                            'forecasted_total': sum(fore_ind.mapped(lambda x: x.price_subtotal))
                        }
                        if fore_ind:
                            industrial_forecast_vals.append(fore_ind.id)
                        total_vals.append(val)
                        if total_categ == 0:
                            total_categ[ind.categ_id.name] = [val]
                        else:
                            if ind.categ_id.name in total_categ.keys():
                                total_categ[ind.categ_id.name].append(val)
                            else:
                                total_categ[ind.categ_id.name] = [val]
                        count += 1

        res = super(VPGActualSale, self).write(values)
        return {
            'res': res,
            'loc_categ': loc_categ,
            'loc_keys': list(loc_categ.keys()),
            'exp_categ': exp_categ,
            'exp_keys': list(exp_categ.keys()),
            'ind_categ': ind_categ,
            'ind_keys': list(ind_categ.keys()),
            'total_categ': total_categ,
            'total_keys': list(total_categ.keys()),
            'orders': data,
        }

    @api.model
    def vpg_sale_report(self, values, option):
        report_values = self.env['vpg.actual.sale'].search(
            [('id', '=', option)])

        data = {
            'report_type': report_values.report_type,
            'model': self,
        }

        approvals = self.env['approval.request']

        industry = approvals.search(
            [('category_id.name', '=', 'Industrial VPG Request'), ('request_status', '=', 'approved')])
        local = approvals.search([('category_id.name', '=', 'Local VPG Request'), ('request_status', '=', 'approved')])
        export = approvals.search(
            [('category_id.name', '=', 'Export VPG Request'), ('request_status', '=', 'approved')])

        invoice_data = self.env['account.move'].search([('state', '=', 'posted')])
        product_cat = self.env['product.category'].search([])
        export_invoice_data_fil = invoice_data.filtered(lambda x: x.customer_type_id == 'export')
        local_invoice_data_fil = invoice_data.filtered(lambda y: y.customer_type_id == 'local')
        industrial_invoice_data_fil = invoice_data.filtered(lambda z: z.customer_type_id == 'industrial')

        total_datas = []
        total_categ = {}

        if local_invoice_data_fil:
            inv_local_product_ids = local_invoice_data_fil.invoice_line_ids.mapped('product_id')
            local_forecast_vals = []
            count = 1
            for loc in inv_local_product_ids:
                inv_local_quantity = local_invoice_data_fil.invoice_line_ids.filtered(
                    lambda x: x.product_id.id == loc.id)
                fore_local_quantity = local.product_line_ids.filtered(lambda x: x.product_id.id == loc.id)
                for fore_loc in fore_local_quantity:
                    if inv_local_quantity:
                        val = {
                            'product': loc.name,
                            'product_cat': loc.categ_id.name,
                            'actual_qty': sum(inv_local_quantity.mapped(lambda x: x.quantity)),
                            'actual_total': sum(inv_local_quantity.mapped(lambda x: x.price_subtotal)),
                            'forecasted': sum(fore_loc.mapped(lambda x: x.quantity)),
                            'forecasted_total': sum(fore_loc.mapped(lambda x: x.price_subtotal))
                        }

                        if fore_loc:
                            local_forecast_vals.append(fore_loc.id)
                        total_datas.append(val)
                        if total_categ == 0:
                            total_categ[loc.categ_id.name] = [val]
                        else:
                            if loc.categ_id.name in total_categ.keys():
                                total_categ[loc.categ_id.name].append(val)
                            else:
                                total_categ[loc.categ_id.name] = [val]
                        count += 1
        if export_invoice_data_fil:
            inv_export_product_ids = export_invoice_data_fil.invoice_line_ids.mapped('product_id')
            export_forecast_vals = []
            count = 1
            for exp in inv_export_product_ids:
                inv_export_quantity = export_invoice_data_fil.invoice_line_ids.filtered(
                    lambda x: x.product_id.id == exp.id)
                fore_export_quantity = export.product_line_ids.filtered(lambda x: x.product_id.id == exp.id)
                for fore_exp in fore_export_quantity:
                    if inv_export_quantity:
                        val = {
                            'product': exp.name,
                            'product_cat': exp.categ_id.name,
                            'actual_qty': sum(inv_export_quantity.mapped(lambda x: x.quantity)),
                            'actual_total': sum(inv_export_quantity.mapped(lambda x: x.price_subtotal)),
                            'forecasted': sum(fore_exp.mapped(lambda x: x.quantity)),
                            'forecasted_total': sum(fore_exp.mapped(lambda x: x.price_subtotal)),
                        }
                        if fore_exp:
                            export_forecast_vals.append(fore_exp.id)
                        total_datas.append(val)

                        if total_categ == 0:
                            total_categ[exp.categ_id.name] = [val]
                        else:
                            if exp.categ_id.name in total_categ.keys():
                                total_categ[exp.categ_id.name].append(val)
                            else:
                                total_categ[exp.categ_id.name] = [val]
                        count += 1
        if industrial_invoice_data_fil:
            inv_industrial_product_ids = industrial_invoice_data_fil.invoice_line_ids.mapped('product_id')
            industrial_forecast_vals = []
            count = 1
            for ind in inv_industrial_product_ids:
                inv_industrial_quantity = industrial_invoice_data_fil.invoice_line_ids.filtered(
                    lambda x: x.product_id.id == ind.id)
                fore_industry_quantity = industry.product_line_ids.filtered(lambda x: x.product_id.id == ind.id)
                for fore_ind in fore_industry_quantity:
                    if inv_industrial_quantity:
                        val = {
                            'product': ind.name,
                            'product_cat': ind.categ_id.name,
                            'actual_qty': sum(inv_industrial_quantity.mapped(lambda x: x.quantity)),
                            'actual_total': sum(inv_industrial_quantity.mapped(lambda x: x.price_subtotal)),
                            'forecasted': sum(fore_ind.mapped(lambda x: x.quantity)),
                            'forecasted_total': sum(fore_ind.mapped(lambda x: x.price_subtotal))
                        }
                        if fore_ind:
                            industrial_forecast_vals.append(fore_ind.id)
                        total_datas.append(val)

                        if total_categ == 0:
                            total_categ[ind.categ_id.name] = [val]
                        else:
                            if ind.categ_id.name in total_categ.keys():
                                total_categ[ind.categ_id.name].append(val)
                            else:
                                total_categ[ind.categ_id.name] = [val]
                        count += 1

        filters = self.get_filter(option)
        return {
            'filters': filters,
            'total_datas': total_datas,
            'total_categ': total_categ,
            'total_keys': list(total_categ.keys())
        }

    def get_filter(self, option):
        data = self.get_filter_data(option)
        filters = {}
        if data.get('report_type') == 'report_by_total':
            filters['report_type'] = 'Report By Total'
        elif data.get('report_type') == 'report_by_local':
            filters['report_type'] = 'Report By Local'
        elif data.get('report_type') == 'report_by_export':
            filters['report_type'] = 'Report By Export'
        elif data.get('report_type') == 'report_by_industry':
            filters['report_type'] = 'Report By Industrial'
        else:
            filters['report_type'] = 'report_by_total'

        return filters

    def get_filter_data(self, option):
        r = self.env['vpg.actual.sale'].search([('id', '=', option[0])])
        default_filters = {}

        filter_dict = {
            'report_type': r.report_type,
        }
        filter_dict.update(default_filters)
        return filter_dict

    @api.model
    def vpg_report(self, values, option):

        report_values = self.env['vpg.actual.sale'].search([('id', '=', option)])

        data = {
            'model': self,
        }
        if values.get('report_type', False):
            data.update({
                'report_type': values['report_type'],
            })

        if values.get('date_from', False):
            data.update({
                'date_from': values['date_from'],
            })

        if values.get('date_to', False):
            data.update({
                'date_to': values['date_to'],
            })
        approvals = self.env['approval.request']

        industry = approvals.search(
            [('category_id.name', '=', 'Industrial VPG Request'), ('request_status', '=', 'approved')])
        local = approvals.search([('category_id.name', '=', 'Local VPG Request'), ('request_status', '=', 'approved')])
        export = approvals.search(
            [('category_id.name', '=', 'Export VPG Request'), ('request_status', '=', 'approved')])

        domain = [('state', '=', 'posted')]
        if data.get('date_from', False) and data.get('date_to', False):
            if data['date_from'] > data['date_to']:
                raise UserError(_('Start Date must be greater than End Date'))

        if data.get('date_from', False):
            domain.append(('invoice_date', '>=', data.get('date_from')))

        if data.get('date_to', False):
            domain.append(('invoice_date', '<=', data.get('date_to')))

        invoice_data = self.env['account.move'].search(domain)
        product_cat = self.env['product.category'].search([])

        export_invoice_data_fil = invoice_data.filtered(lambda x: x.customer_type_id == 'export')
        local_invoice_data_fil = invoice_data.filtered(lambda y: y.customer_type_id == 'local')
        industrial_invoice_data_fil = invoice_data.filtered(lambda z: z.customer_type_id == 'industrial')

        loc_vals = []
        exp_vals = []
        ind_vals = []
        total_vals = []

        loc_categ = {}
        exp_categ = {}
        ind_categ = {}
        total_categ = {}

        if local_invoice_data_fil:
            inv_local_product_ids = local_invoice_data_fil.invoice_line_ids.mapped('product_id')
            local_forecast_vals = []
            count = 1
            for loc in inv_local_product_ids:
                inv_local_quantity = local_invoice_data_fil.invoice_line_ids.filtered(
                    lambda x: x.product_id.id == loc.id)
                fore_local_quantity = local.product_line_ids.filtered(lambda x: x.product_id.id == loc.id)
                for fore_loc in fore_local_quantity:
                    if inv_local_quantity:
                        val = {
                            'product': loc.name,
                            'product_cat': loc.categ_id.name,
                            'actual_qty': sum(inv_local_quantity.mapped(lambda x: x.quantity)),
                            'actual_total': sum(inv_local_quantity.mapped(lambda x: x.price_subtotal)),
                            'forecasted': sum(fore_loc.mapped(lambda x: x.quantity)),
                            'forecasted_total': sum(fore_loc.mapped(lambda x: x.price_subtotal))
                        }
                        if fore_loc:
                            local_forecast_vals.append(fore_loc.id)
                        loc_vals.append(val)
                        if loc_categ == {}:
                            loc_categ[loc.categ_id.name] = [val]
                        else:
                            if loc.categ_id.name in loc_categ.keys():
                                loc_categ[loc.categ_id.name].append(val)
                            else:
                                loc_categ[loc.categ_id.name] = [val]

                    count += 1

        if export_invoice_data_fil:
            inv_export_product_ids = export_invoice_data_fil.invoice_line_ids.mapped('product_id')
            export_forecast_vals = []
            count = 1
            for exp in inv_export_product_ids:
                inv_export_quantity = export_invoice_data_fil.invoice_line_ids.filtered(
                    lambda x: x.product_id.id == exp.id)
                fore_export_quantity = export.product_line_ids.filtered(lambda x: x.product_id.id == exp.id)
                for fore_exp in fore_export_quantity:
                    if inv_export_quantity:
                        val = {
                            'product': exp.name,
                            'product_cat': exp.categ_id.name,
                            'actual_qty': sum(inv_export_quantity.mapped(lambda x: x.quantity)),
                            'actual_total': sum(inv_export_quantity.mapped(lambda x: x.price_subtotal)),
                            'forecasted': sum(fore_exp.mapped(lambda x: x.quantity)),
                            'forecasted_total': sum(fore_exp.mapped(lambda x: x.price_subtotal)),
                        }
                        if fore_exp:
                            export_forecast_vals.append(fore_exp.id)
                        exp_vals.append(val)
                        if exp_categ == 0:
                            exp_categ[exp.categ_id.name] = [val]
                        else:
                            if exp.categ_id.id in exp_categ.keys():
                                exp_categ[exp.categ_id.name].append(val)
                            else:
                                exp_categ[exp.categ_id.name] = [val]
                    count += 1

        if industrial_invoice_data_fil:
            inv_industrial_product_ids = industrial_invoice_data_fil.invoice_line_ids.mapped('product_id')
            industrial_forecast_vals = []
            count = 1
            for ind in inv_industrial_product_ids:
                inv_industrial_quantity = industrial_invoice_data_fil.invoice_line_ids.filtered(
                    lambda x: x.product_id.id == ind.id)
                fore_industry_quantity = industry.product_line_ids.filtered(lambda x: x.product_id.id == ind.id)
                for fore_ind in fore_industry_quantity:
                    if inv_industrial_quantity:
                        val = {
                            'product': ind.name,
                            'product_cat': ind.categ_id.name,
                            'actual_qty': sum(inv_industrial_quantity.mapped(lambda x: x.quantity)),
                            'actual_total': sum(inv_industrial_quantity.mapped(lambda x: x.price_subtotal)),
                            'forecasted': sum(fore_ind.mapped(lambda x: x.quantity)),
                            'forecasted_total': sum(fore_ind.mapped(lambda x: x.price_subtotal))
                        }
                        if fore_ind:
                            industrial_forecast_vals.append(fore_ind.id)
                        ind_vals.append(val)
                        if ind_categ == 0:
                            ind_categ[ind.categ_id.name] = [val]
                        else:
                            if ind.categ_id.name in ind_categ.keys():
                                ind_categ[ind.categ_id.name].append(val)
                            else:
                                ind_categ[ind.categ_id.name] = [val]
                        count += 1

        if local_invoice_data_fil:
            inv_local_product_ids = local_invoice_data_fil.invoice_line_ids.mapped('product_id')
            local_forecast_vals = []
            count = 1
            for loc in inv_local_product_ids:
                inv_local_quantity = local_invoice_data_fil.invoice_line_ids.filtered(
                    lambda x: x.product_id.id == loc.id)
                fore_local_quantity = local.product_line_ids.filtered(lambda x: x.product_id.id == loc.id)
                for fore_loc in fore_local_quantity:
                    if inv_local_quantity:
                        val = {
                            'product': loc.name,
                            'product_cat': loc.categ_id.name,
                            'actual_qty': sum(inv_local_quantity.mapped(lambda x: x.quantity)),
                            'actual_total': sum(inv_local_quantity.mapped(lambda x: x.price_subtotal)),
                            'forecasted': sum(fore_loc.mapped(lambda x: x.quantity)),
                            'forecasted_total': sum(fore_loc.mapped(lambda x: x.price_subtotal))
                        }
                        if fore_loc:
                            local_forecast_vals.append(fore_loc.id)
                        total_vals.append(val)
                        if total_categ == 0:
                            total_categ[loc.categ_id.name] = [val]
                        else:
                            if loc.categ_id.name in total_categ.keys():
                                total_categ[loc.categ_id.name].append(val)
                            else:
                                total_categ[loc.categ_id.name] = [val]
                        count += 1
        if export_invoice_data_fil:
            inv_export_product_ids = export_invoice_data_fil.invoice_line_ids.mapped('product_id')
            export_forecast_vals = []
            count = 1
            for exp in inv_export_product_ids:
                inv_export_quantity = export_invoice_data_fil.invoice_line_ids.filtered(
                    lambda x: x.product_id.id == exp.id)
                fore_export_quantity = export.product_line_ids.filtered(lambda x: x.product_id.id == exp.id)
                for fore_exp in fore_export_quantity:
                    if inv_export_quantity:
                        val = {
                            'product': exp.name,
                            'product_cat': exp.categ_id.name,
                            'actual_qty': sum(inv_export_quantity.mapped(lambda x: x.quantity)),
                            'actual_total': sum(inv_export_quantity.mapped(lambda x: x.price_subtotal)),
                            'forecasted': sum(fore_exp.mapped(lambda x: x.quantity)),
                            'forecasted_total': sum(fore_exp.mapped(lambda x: x.price_subtotal)),
                        }
                        if fore_exp:
                            export_forecast_vals.append(fore_exp.id)
                        total_vals.append(val)

                        if total_categ == 0:
                            total_categ[exp.categ_id.name] = [val]
                        else:
                            if exp.categ_id.name in total_categ.keys():
                                total_categ[exp.categ_id.name].append(val)
                            else:
                                total_categ[exp.categ_id.name] = [val]
                        count += 1
        if industrial_invoice_data_fil:
            inv_industrial_product_ids = industrial_invoice_data_fil.invoice_line_ids.mapped('product_id')
            industrial_forecast_vals = []
            count = 1
            for ind in inv_industrial_product_ids:
                inv_industrial_quantity = industrial_invoice_data_fil.invoice_line_ids.filtered(
                    lambda x: x.product_id.id == ind.id)
                fore_industry_quantity = industry.product_line_ids.filtered(lambda x: x.product_id.id == ind.id)
                for fore_ind in fore_industry_quantity:
                    if inv_industrial_quantity:
                        val = {
                            'product': ind.name,
                            'product_cat': ind.categ_id.name,
                            'actual_qty': sum(inv_industrial_quantity.mapped(lambda x: x.quantity)),
                            'actual_total': sum(inv_industrial_quantity.mapped(lambda x: x.price_subtotal)),
                            'forecasted': sum(fore_ind.mapped(lambda x: x.quantity)),
                            'forecasted_total': sum(fore_ind.mapped(lambda x: x.price_subtotal))
                        }
                        if fore_ind:
                            industrial_forecast_vals.append(fore_ind.id)
                        total_vals.append(val)
                        if total_categ == 0:
                            total_categ[ind.categ_id.name] = [val]
                        else:
                            if ind.categ_id.name in total_categ.keys():
                                total_categ[ind.categ_id.name].append(val)
                            else:
                                total_categ[ind.categ_id.name] = [val]
                        count += 1

        return {
            'report_filter': data,
            'loc_categ': loc_categ,
            'loc_keys': list(loc_categ.keys()),
            'exp_categ': exp_categ,
            'exp_keys': list(exp_categ.keys()),
            'ind_categ': ind_categ,
            'ind_keys': list(ind_categ.keys()),
            'total_categ': total_categ,
            'total_keys': list(total_categ.keys()),

        }
