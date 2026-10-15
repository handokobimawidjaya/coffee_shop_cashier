/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";

const IDR_ROUNDING = 1000;
const MEDIUM_ROUNDING = 10000;
const CASH_DENOMINATIONS = [1000, 2000, 5000, 10000, 20000, 50000, 100000];

patch(PaymentScreen.prototype, {
    get cashRecommendationPaymentLine() {
        if (this.selectedPaymentLine?.payment_method_id?.is_cash_count) {
            return this.selectedPaymentLine;
        }
        return this.paymentLines.find((line) => line.payment_method_id?.is_cash_count);
    },

    get isCashPaymentSelected() {
        return Boolean(this.cashRecommendationPaymentLine);
    },

    get cashPaymentRecommendations() {
        if (!this.isCashPaymentSelected) {
            return [];
        }

        const lineAmount = this.cashRecommendationPaymentLine.get_amount();
        const dueBeforeSelectedLine = Math.max(0, this.currentOrder.get_due() + lineAmount);
        const roundUp = (amount, increment) => Math.ceil(amount / increment) * increment;
        const roundedAmount = roundUp(dueBeforeSelectedLine, IDR_ROUNDING);
        const mediumAmount = roundUp(
            roundedAmount + 1,
            MEDIUM_ROUNDING
        );
        const largestDenomination = CASH_DENOMINATIONS[CASH_DENOMINATIONS.length - 1];
        const nextAvailableDenomination = (minimum) =>
            CASH_DENOMINATIONS.find((denomination) => denomination >= minimum) ||
            Math.ceil(minimum / largestDenomination) * largestDenomination;
        const cashDenomination = nextAvailableDenomination(
            Math.max(dueBeforeSelectedLine, mediumAmount + 1)
        );

        return [
            roundedAmount,
            mediumAmount,
            cashDenomination,
        ];
    },

    selectCashPaymentRecommendation(amount) {
        if (!this.cashRecommendationPaymentLine) {
            return;
        }
        this.currentOrder.select_paymentline(this.cashRecommendationPaymentLine);
        this.updateSelectedPaymentline(amount);
        this.numberBuffer.set(amount.toString());
    },
});
