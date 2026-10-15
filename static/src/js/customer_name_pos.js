/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { patch } from "@web/core/utils/patch";
import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";

patch(PaymentScreen.prototype, {
    updateCustomerName(event) {
        this.currentOrder.update({ customer_name: event.target.value });
    },

    async validateOrder(isForceValidate) {
        const customerName = (this.currentOrder.customer_name || "").trim();
        if (!customerName) {
            this.notification.add(_t("Enter the customer name before validating the order."), {
                type: "warning",
            });
            return;
        }
        if (customerName !== this.currentOrder.customer_name) {
            this.currentOrder.update({ customer_name: customerName });
        }
        return super.validateOrder(...arguments);
    },
});
