# -*- coding: utf-8 -*-
from odoo import _, api, models


class ReportSaleDetails(models.AbstractModel):
    _inherit = 'report.point_of_sale.report_saledetails'

    def _prepare_get_sale_details_args_kwargs(self, data):
        args, kwargs = super()._prepare_get_sale_details_args_kwargs(data)
        if data.get('cash_out_override') is not None:
            kwargs['cash_out_override'] = data['cash_out_override']
        return args, kwargs

    @api.model
    def get_sale_details(self, date_start=False, date_stop=False, config_ids=False, session_ids=False, cash_out_override=0.0, **kwargs):
        report_data = super().get_sale_details(
            date_start=date_start,
            date_stop=date_stop,
            config_ids=config_ids,
            session_ids=session_ids,
            **kwargs,
        )

        if session_ids:
            sessions = self.env['pos.session'].search([('id', 'in', session_ids)])
        elif config_ids:
            date_start, date_stop = self._get_date_start_and_date_stop(date_start, date_stop)
            sessions = self.env['pos.session'].search([
                ('config_id', 'in', config_ids),
                ('start_at', '>=', date_start),
                ('stop_at', '<=', date_stop),
            ])
        else:
            sessions = self.env['pos.session']

        total_cash_out = 0.0

        for session in sessions:
            pending_cash_out = 0.0
            if session_ids and len(session_ids) == 1 and session.id == session_ids[0]:
                pending_cash_out = max(session.currency_id.round(float(cash_out_override or 0.0)), 0.0)
            session_cash_out = session.store_cash_out + pending_cash_out
            if session_cash_out <= 0:
                continue

            cash_name = _('Cash %(session_name)s', session_name=session.name)
            cash_payment = next((
                payment for payment in report_data['payments']
                if payment.get('session') == session.id
                and (payment.get('cash') or payment.get('name') == cash_name)
            ), None)
            if not cash_payment:
                continue

            total_cash_out += session_cash_out
            cash_out_name = f'Cash Out {session.name}'
            report_data['payments'][:] = [
                payment for payment in report_data['payments']
                if payment.get('name') != cash_out_name
            ]
            report_data['payments'].insert(
                report_data['payments'].index(cash_payment) + 1,
                {
                    'name': cash_out_name,
                    'total': -session_cash_out,
                },
            )
            cash_payment['final_count'] = session.currency_id.round(
                (cash_payment.get('total') or 0.0)
                + session.cash_register_balance_start
                + sum(session.sudo().statement_line_ids.mapped('amount'))
                - pending_cash_out
            )
            cash_payment['money_difference'] = (
                cash_payment.get('money_counted', 0.0) - cash_payment['final_count']
            )

        currency = report_data.get('currency', {})
        report_data['payments_net_total'] = currency.get('total_paid', 0.0) - total_cash_out

        return report_data
