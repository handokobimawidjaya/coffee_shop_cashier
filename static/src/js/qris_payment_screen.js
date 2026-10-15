/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";

patch(PaymentScreen.prototype, {

    get isQrisSelected() {
        const paymentLine = this.selectedPaymentLine;

        if (!paymentLine || !paymentLine.payment_method_id) {
            return false;
        }

        const paymentMethodName =
            paymentLine.payment_method_id.name || "";

        return paymentMethodName
            .trim()
            .toLowerCase() === "qris";
    },

    get qrisImageUrl() {
        return "/coffee_shop_cashier/static/src/img/qris_barcode.png";
    },

    async addNewPaymentLine(paymentMethod) {

        const existingLines = [...this.paymentLines];

        /*
         * Jika payment method yang sama diklik lagi,
         * jangan buat line baru.
         */
        if (
            existingLines.length === 1 &&
            existingLines[0].payment_method_id?.id === paymentMethod.id
        ) {
            this.currentOrder.select_paymentline(existingLines[0]);
            this.numberBuffer.reset();
            return true;
        }

        /*
         * Hapus semua payment line sebelumnya.
         * Hanya payment method terakhir yang dipilih yang dipertahankan.
         */
        for (const line of existingLines) {
            this.currentOrder.remove_paymentline(line);
        }

        this.numberBuffer.reset();

        /*
         * Jalankan fungsi asli Odoo.
         * Karena line sebelumnya sudah dihapus,
         * amount otomatis kembali sebesar total yang belum dibayar.
         */
        return await super.addNewPaymentLine(paymentMethod);
    },

});