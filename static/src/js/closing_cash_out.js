/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { rpc } from "@web/core/network/rpc";
import { user } from "@web/core/user";
import { downloadReport } from "@web/webclient/actions/reports/utils";
import { ClosePosPopup } from "@point_of_sale/app/navbar/closing_popup/closing_popup";
import { parseFloat } from "@web/views/fields/parsers";

patch(ClosePosPopup.prototype, {
    setup() {
        super.setup(...arguments);
        this.cashOutPersistedThisPopup = 0;
        this.state.storeCashOut = this.env.utils.formatCurrency(
            0,
            false
        );
    },

    getDifference(paymentId) {
        const difference = super.getDifference(...arguments);
        if (paymentId === this.props.default_cash_details?.id) {
            return (
                difference +
                parseFloat(this.state.storeCashOut || 0)
            );
        }
        return difference;
    },

    canConfirm() {
        return super.canConfirm() && this.env.utils.isValidFloat(this.state.storeCashOut);
    },

    get cashMoveData() {
        const cashMoveData = super.cashMoveData;
        const pendingCashOut =
            parseFloat(this.state.storeCashOut || 0) - this.cashOutPersistedThisPopup;
        if (pendingCashOut) {
            cashMoveData.moves.push({
                id: cashMoveData.moves.length,
                name: `Cash Out ${this.pos.session.name}`,
                amount: -pendingCashOut,
            });
            cashMoveData.total -= pendingCashOut;
        }
        return cashMoveData;
    },

    get displayedStoreCashOut() {
        return (
            (this.pos.session.store_cash_out || 0) +
            parseFloat(this.state.storeCashOut || 0) -
            this.cashOutPersistedThisPopup
        );
    },

    async persistStoreCashOut() {
        const amount = parseFloat(this.state.storeCashOut || 0);
        const adjustment = amount - this.cashOutPersistedThisPopup;
        if (!adjustment) {
            return;
        }
        await this.pos.data.call(
            "pos.session",
            "set_store_cash_out",
            [[this.pos.session.id], adjustment]
        );
        this.cashOutPersistedThisPopup = amount;
        this.pos.session.store_cash_out = (this.pos.session.store_cash_out || 0) + adjustment;
    },

    async downloadSalesReport() {
        const sessionId = this.pos.session.id;
        const reportAction = await rpc("/web/action/load", {
            action_id: "point_of_sale.sale_details_report",
        });
        return downloadReport(
            rpc,
            {
                ...reportAction,
                context: { active_ids: [sessionId] },
                data: {
                    session_ids: [sessionId],
                    cash_out_override:
                        parseFloat(this.state.storeCashOut || 0) - this.cashOutPersistedThisPopup,
                },
            },
            "pdf",
            user.context
        );
    },

    async closeSession() {
        await this.persistStoreCashOut();
        return super.closeSession(...arguments);
    },
});
