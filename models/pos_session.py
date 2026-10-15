# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class PosSession(models.Model):
    _inherit = 'pos.session'

    store_cash_out = fields.Monetary(
        string='Cash Out',
        currency_field='currency_id',
        readonly=True,
        copy=False,
        help='Cash withdrawn from the register for store expenses.',
    )

    @api.model
    def _load_pos_data_fields(self, config_id):
        return super()._load_pos_data_fields(config_id) + ['store_cash_out']

    def set_store_cash_out(self, amount):
        self.ensure_one()
        if not self.env.user.has_group('point_of_sale.group_pos_user'):
            raise UserError(_('You are not allowed to record cash out for this session.'))
        if self.state != 'opened':
            raise UserError(_('Cash out can only be recorded while the POS session is open.'))
        adjustment = self.currency_id.round(float(amount or 0.0))
        if not adjustment:
            return True

        total_cash_out = self.currency_id.round(self.store_cash_out + adjustment)
        if total_cash_out < 0:
            raise UserError(_('Cash out total cannot be negative.'))
        if total_cash_out and not self.cash_journal_id:
            raise UserError(_('There is no cash payment method for this POS session.'))

        payment_ref = f'Cash Out {self.name}'
        cash_line = self.env['account.bank.statement.line'].search([
            ('pos_session_id', '=', self.id),
            ('payment_ref', '=', payment_ref),
        ], limit=1)

        if not total_cash_out:
            cash_line.unlink()
        elif cash_line:
            cash_line.write({'amount': -total_cash_out})
        else:
            self.env['account.bank.statement.line'].create({
                'pos_session_id': self.id,
                'journal_id': self.cash_journal_id.id,
                'amount': -total_cash_out,
                'date': fields.Date.context_today(self),
                'payment_ref': payment_ref,
            })

        self.store_cash_out = total_cash_out
        return True
