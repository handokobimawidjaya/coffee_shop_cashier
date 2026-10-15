# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    """
    Extends product.template to support inventory threshold monitoring
    and automatic low stock notifications for Coffee Shops.
    """
    _inherit = 'product.template'

    low_stock_threshold = fields.Float(
        string='Low Stock Threshold',
        default=5.0,
        help="Alert will trigger if quantity available drops below this value."
    )
    alert_on_low_stock = fields.Boolean(
        string='Alert on Low Stock',
        default=False,
        help="Check this to receive email alerts when stock is running low."
    )
    low_stock_alert_sent = fields.Boolean(
        string='Low Stock Alert Sent',
        default=False,
        copy=False,
        help="Technical field to prevent duplicate email alerts."
    )
    coffee_beans_product_id = fields.Many2one(
        'product.product',
        string='Coffee Beans Ingredient',
        domain="[('is_storable', '=', True), ('categ_id.name', '=', 'Beans')]",
        help="Beans product consumed automatically when this product is sold in POS."
    )
    coffee_beans_qty_per_cup = fields.Float(
        string='Beans per Cup',
        default=0.0,
        help="Quantity of beans consumed for one sold cup, using the beans product unit of measure."
    )

    @api.model
    def _check_low_stock_alerts(self):
        """
        Scheduled action (cron) method to check all product templates.
        Triggers email notifications for products whose stock levels are
        below their thresholds, and resets the sent flag when stock is replenished.
        """
        _logger.info("Starting Coffee Shop Low Stock check...")

        # 1. Fetch recipient email from config parameters
        ir_config = self.env['ir.config_parameter'].sudo()
        recipient_email = ir_config.get_param('coffee_shop_cashier.alert_email', False)
        
        if not recipient_email:
            # Fallback to company email or admin email
            recipient_email = self.env.company.email or self.env.user.email
            _logger.warning("No recipient email configured for low stock alerts. Using fallback: %s", recipient_email)

        # 2. Get mail template
        template = self.env.ref('coffee_shop_cashier.email_template_low_stock', raise_if_not_found=False)
        if not template:
            _logger.error("Low stock email template 'coffee_shop_cashier.email_template_low_stock' not found!")
            return

        # 3. Process products that are low in stock
        # We check both template qty_available or if we want to be more specific, we check the product.product (variants).
        # For simplicity and robust POS integration, checking template level qty_available is standard.
        low_stock_products = self.search([
            ('alert_on_low_stock', '=', True),
            ('low_stock_alert_sent', '=', False),
        ])

        sent_count = 0
        for product in low_stock_products:
            # Check if stock is low
            if product.qty_available <= product.low_stock_threshold:
                try:
                    # Send the mail using the template, overriding the recipient
                    template.send_mail(
                        product.id,
                        force_send=True,
                        email_values={'email_to': recipient_email}
                    )
                    product.write({'low_stock_alert_sent': True})
                    sent_count += 1
                    _logger.info("Sent low stock alert for product %s to %s", product.name, recipient_email)
                except Exception as e:
                    _logger.error("Failed to send low stock email alert for product %s: %s", product.name, str(e))

        # 4. Reset alert flag for replenished products
        replenished_products = self.search([
            ('alert_on_low_stock', '=', True),
            ('low_stock_alert_sent', '=', True),
        ])
        
        reset_count = 0
        for product in replenished_products:
            if product.qty_available > product.low_stock_threshold:
                product.write({'low_stock_alert_sent': False})
                reset_count += 1
                _logger.info("Reset alert flag for replenished product %s", product.name)

        _logger.info("Coffee Shop Low Stock check finished. Alerts sent: %d, Flags reset: %d", sent_count, reset_count)
