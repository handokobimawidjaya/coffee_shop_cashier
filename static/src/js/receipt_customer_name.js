/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { PosOrder } from "@point_of_sale/app/models/pos_order";

patch(PosOrder.prototype, {
    export_for_printing(baseUrl, headerData) {
        const receiptData = super.export_for_printing(...arguments);
        receiptData.headerData.customerName = this.customer_name || "";
        return receiptData;
    },
});
