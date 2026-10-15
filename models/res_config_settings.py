# -*- coding: utf-8 -*-
from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    """
    Inherits res.config.settings to add coffee shop specific configurations.
    """
    _inherit = 'res.config.settings'

    coffee_shop_alert_email = fields.Char(
        string='Low Stock Alert Email',
        config_parameter='coffee_shop_cashier.alert_email',
        help="Email address that will receive alerts when stock levels drop below the threshold."
    )
