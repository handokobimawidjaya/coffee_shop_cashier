# -*- coding: utf-8 -*-
import logging

from odoo import fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class PosOrder(models.Model):
    _inherit = 'pos.order'

    coffee_beans_consumed = fields.Boolean(
        string='Coffee Beans Consumed',
        copy=False,
        help="Technical field to avoid consuming recipe beans more than once."
    )
    customer_name = fields.Char(string='Nama Pelanggan', index=True)

    def action_pos_order_paid(self):
        missing_names = self.filtered(lambda order: not order.customer_name or not order.customer_name.strip())
        if missing_names:
            raise UserError("Nama Pelanggan wajib diisi sebelum memvalidasi pesanan.")
        res = super().action_pos_order_paid()
        self._consume_coffee_beans()
        return res

    def _consume_coffee_beans(self):
        Quant = self.env['stock.quant'].sudo()
        beans_to_check = self.env['product.template']

        for order in self.filtered(lambda pos_order: not pos_order.coffee_beans_consumed):
            source_location = (
                order.config_id.picking_type_id.default_location_src_id
                or order.session_id.config_id.picking_type_id.default_location_src_id
                or self.env.ref('stock.stock_location_stock', raise_if_not_found=False)
            )
            if not source_location:
                _logger.warning("Cannot consume coffee beans for POS order %s: no stock source location.", order.name)
                continue

            consumption_by_product = {}
            for line in order.lines:
                recipe_product = line.product_id.product_tmpl_id
                beans_product = recipe_product.coffee_beans_product_id
                beans_qty = recipe_product.coffee_beans_qty_per_cup

                if not beans_product or not beans_qty or line.qty <= 0:
                    continue

                consumption_by_product.setdefault(beans_product, 0.0)
                consumption_by_product[beans_product] += beans_qty * line.qty

            for beans_product, qty in consumption_by_product.items():
                Quant._update_available_quantity(beans_product, source_location, -qty)
                beans_to_check |= beans_product.product_tmpl_id
                _logger.info(
                    "Consumed %.2f %s of %s for POS order %s.",
                    qty,
                    beans_product.uom_id.name,
                    beans_product.display_name,
                    order.name,
                )

            order.coffee_beans_consumed = True

        if beans_to_check:
            beans_to_check._check_low_stock_alerts()
