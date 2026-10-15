from odoo import http
from odoo.http import request
from werkzeug.exceptions import NotFound


class CoffeeShopPosOrderReceiptController(http.Controller):

    @http.route(
        '/coffee_shop_cashier/pos_order/<int:order_id>/print_receipt',
        type='http',
        auth='user',
        methods=['GET'],
    )
    def print_pos_order_receipt(self, order_id):
        order = request.env['pos.order'].browse(order_id).exists()
        if not order:
            raise NotFound()
        order.check_access('read')

        html, _ = request.env['ir.actions.report']._render_qweb_html(
            'coffee_shop_cashier.report_pos_order_full_receipt',
            order.ids,
        )
        return request.make_response(
            html,
            headers=[('Content-Type', 'text/html; charset=utf-8')],
        )
