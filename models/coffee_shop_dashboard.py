# -*- coding: utf-8 -*-
from odoo import models, fields, api


class CoffeeShopDashboard(models.TransientModel):
    """
    Transient model representing the Coffee Shop Dashboard.
    Computes key performance indicators (KPIs) and lists low stock items dynamically.
    """
    _name = 'coffee.shop.dashboard'
    _description = 'Coffee Shop Dashboard'

    name = fields.Char(string="Dashboard Name", default="Overview")
    company_currency_id = fields.Many2one(
        'res.currency',
        string="Company Currency",
        default=lambda self: self.env.company.currency_id
    )
    total_sales_today = fields.Float(string="Total Sales Today", compute="_compute_dashboard_stats")
    sales_count_today = fields.Integer(string="Total Transactions Today", compute="_compute_dashboard_stats")
    low_stock_items_count = fields.Integer(string="Low Stock Products Count", compute="_compute_dashboard_stats")
    active_sessions_count = fields.Integer(string="Active POS Sessions", compute="_compute_dashboard_stats")
    low_stock_product_ids = fields.Many2many(
        'product.template',
        string="Critical Stock Products",
        compute="_compute_dashboard_stats"
    )

    def _compute_dashboard_stats(self):
        """
        Computes dashboard statistics including today's sales, active sessions, and low stock count.
        """
        pos_order_obj = self.env['pos.order']
        product_obj = self.env['product.template']
        pos_session_obj = self.env['pos.session']

        today = fields.Date.context_today(self)

        # 1. Sales today
        orders_today = pos_order_obj.search([
            ('date_order', '>=', fields.Datetime.to_string(fields.Datetime.now().replace(hour=0, minute=0, second=0, microsecond=0))),
            ('state', 'in', ['paid', 'done', 'invoiced'])
        ])
        
        total_sales = sum(orders_today.mapped('amount_total'))
        sales_count = len(orders_today)

        # 2. Low stock items
        low_stock_products = product_obj.search([
            ('alert_on_low_stock', '=', True),
        ])
        # Filter for actual low stock products
        critical_products = low_stock_products.filtered(lambda p: p.qty_available <= p.low_stock_threshold)
        low_stock_count = len(critical_products)

        # 3. Active sessions
        active_sessions = pos_session_obj.search_count([('state', '=', 'opened')])

        for dashboard in self:
            dashboard.total_sales_today = total_sales
            dashboard.sales_count_today = sales_count
            dashboard.low_stock_items_count = low_stock_count
            dashboard.active_sessions_count = active_sessions
            dashboard.low_stock_product_ids = [(6, 0, critical_products.ids)]

    def action_open_pos(self):
        """
        Action to open the POS kanban/session view.
        """
        return self.env["ir.actions.actions"]._for_xml_id("point_of_sale.action_pos_config_kanban")

    def action_trigger_cron(self):
        """
        Manually trigger the low stock email alert check.
        """
        self.env['product.template']._check_low_stock_alerts()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Stock Check Completed',
                'message': 'Checked low stock products and sent email alerts if configured.',
                'sticky': False,
            }
        }
