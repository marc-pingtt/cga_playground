odoo.define('vpg_vs_actual_report.vpg_sales', function (require){
    'use strict';
	var AbstractAction = require('web.AbstractAction');
	var core = require('web.core');
	var rpc = require('web.rpc');
	var QWeb = core.qweb;
	var _t = core._t;
	var datepicker = require('web.datepicker');
	var time = require('web.time');

    var framework = require('web.framework');
    var session = require('web.session');

    var VpgSaleReport = AbstractAction.extend({
        template: 'VpgSaleReport',
        events: {
			'click #apply_filter_type': 'apply_filter_type',
			'click #pdf': 'print_pdf',
			'click #xlsx': 'print_xlsx',
			'mousedown div.input-group.date[data-target-input="nearest"]': '_onCalendarIconClick',
		},

        init: function(parent, action) {
                this._super(parent, action);
                this.wizard_id = action.context.wizard | null;
        },

        start: function() {
			var self = this;
			self.initial_render = true;
			rpc.query({
				model: 'vpg.actual.sale',
				method: 'create',
				args: [{
				}]
			}).then(function(res) {
				self.wizard_id = res;
				self.load_data(self.initial_render);
			})
		},


        _onCalendarIconClick: function(ev) {
        var $calendarInputGroup = $(ev.currentTarget);

            var calendarOptions = {

            minDate: moment({ y: 1000 }),
                maxDate: moment().add(200, 'y'),
                calendarWeeks: true,
                defaultDate: moment().format(),
                sideBySide: true,
                buttons: {
                    showClear: true,
                    showClose: true,
                    showToday: true,
                },

                icons : {
                    date: 'fa fa-calendar',

                },
                locale : moment.locale(),
                format : time.getLangDateFormat(),
                 widgetParent: 'body',
                 allowInputToggle: true,
            };
            $calendarInputGroup.datetimepicker(calendarOptions);
	    },


		load_data: function(initial_render = true, filter_data_selected) {
		    var r = filter_data_selected
			var self = this;
			self._rpc({
				model: 'vpg.actual.sale',
				method: 'vpg_sale_report',
				args: [
	    			filter_data_selected,[this.wizard_id]
				],

			}).then(function(datas) {
                var test = datas
                self.datas = datas
				if (initial_render) {
					self.$('.filter_view_pr').html(QWeb.render('VPGSaleFilterView', {
						filter_data: datas['filters'],

					}));
					self.$el.find('.report_type').select2({
						placeholder: ' Report Type...',
					});

				if (datas){
					self.$('.table_view_pr').html(QWeb.render('VGPSaleTable', {
                        datas: datas['total_datas'],
                        total_cat_val: datas['total_categ'],
                        total_cat_key:datas['total_keys']
					}));
				}
				}
		    })
		},

		apply_filter_type: function(){
		    var self = this;
		    self.initial_render = false;

		    var filter_data_selected = {};

		    if ($(".report_type").length) {
				var report_res = document.getElementById("report_res")
				filter_data_selected.report_type = $(".report_type")[1].value
				report_res.value = $(".report_type")[1].value
				report_res.innerHTML = report_res.value;
				if ($(".report_type")[1].value == "") {
					report_res.innerHTML = "report_by_order";

				}
			}
            if (this.$el.find('.datetimepicker-input[name="date_from"]').val()) {
                filter_data_selected.date_from = moment(this.$el.find('.datetimepicker-input[name="date_from"]').val(), time.getLangDateFormat()).locale('en').format('YYYY-MM-DD');
			}

			if (this.$el.find('.datetimepicker-input[name="date_to"]').val()) {
				filter_data_selected.date_to = moment(this.$el.find('.datetimepicker-input[name="date_to"]').val(), time.getLangDateFormat()).locale('en').format('YYYY-MM-DD');

			}
			rpc.query({
				model: 'vpg.actual.sale',
				method: 'write',
				args: [
					 filter_data_selected, self.wizard_id
				],
			}).then(function(datas) {
		        self.initial_render = false;
				self.load_data(self.initial_render, filter_data_selected);
				if (datas){
					self.$('.table_view_pr').html(QWeb.render('VGPSaleTable', {
					        datas : datas,
					        loc_cat_val:datas['loc_categ'],
					        loc_cat_key:datas['loc_keys'],
					        exp_cat_val:datas['exp_categ'],
					        exp_cat_key:datas['exp_keys'],
					        ind_cat_val:datas['ind_categ'],
					        ind_cat_key:datas['ind_keys'],
					        total_cat_val:datas['total_categ'],
                            total_cat_key:datas['total_keys'],
                            order:datas['orders'],
                            report_type:filter_data_selected['report_type'],
					}));
				}
			});
		},
		print_pdf: function(e) {
			e.preventDefault();
			var self = this;
			var action_title = self._title;
			var filter_data_selected = {};
			if (this.$el.find('.datetimepicker-input[name="date_from"]').val()) {
				filter_data_selected.date_from = moment(this.$el.find('.datetimepicker-input[name="date_from"]').val(), time.getLangDateFormat()).locale('en').format('YYYY-MM-DD');
			}

			if (this.$el.find('.datetimepicker-input[name="date_to"]').val()) {
				filter_data_selected.date_to = moment(this.$el.find('.datetimepicker-input[name="date_to"]').val(), time.getLangDateFormat()).locale('en').format('YYYY-MM-DD');
			}
			if ($(".report_type").length) {
				var report_res = document.getElementById("report_res")
				filter_data_selected.report_type = $(".report_type")[1].value
				report_res.value = $(".report_type")[1].value
				report_res.innerHTML = report_res.value;
				if ($(".report_type")[1].value == "") {
					report_res.innerHTML = "report_by_order";
				}
			}
			self._rpc({
				model: 'vpg.actual.sale',
				method: 'vpg_report',
				args: [
					filter_data_selected,[this.wizard_id]
				],
			}).then(function(datas) {
				var action = {
					'type': 'ir.actions.report',
					'report_type': 'qweb-pdf',
					'report_name': 'vpg_vs_actual_report.vpg_sale_report',
					'report_file': 'vpg_vs_actual_report.vpg_sale_report',
					'data': {
						'report_data': datas
					},
					'context': {
						'active_model': 'vpg.actual.sale',
                        'landscape': 1,
						'vpg_order_report': true

					},
					'display_name': 'VPG vs SALE REPORT',
				};
				return self.do_action(action);
			});

		},
    });
    core.action_registry.add("vpg_asr", VpgSaleReport);
    return VpgSaleReport;
})