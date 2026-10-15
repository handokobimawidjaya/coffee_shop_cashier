/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { ProductCard } from "@point_of_sale/app/generic_components/product_card/product_card";
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";

ProductCard.props = {
    ...ProductCard.props,
    onIncreaseQty: { type: Function, optional: true },
    onDecreaseQty: { type: Function, optional: true },
};

patch(ProductScreen.prototype, {
    increaseProductQty(product) {
        return this.addProductToOrder(product);
    },

    decreaseProductQty(product) {
        const order = this.currentOrder;
        if (!order) {
            return;
        }

        const line = [...order.get_orderlines()]
            .reverse()
            .find((orderline) => orderline.product_id.id === product.id && orderline.qty > 0);
        if (!line) {
            return;
        }

        if (line.qty <= 1) {
            order.removeOrderline(line);
        } else {
            line.set_quantity(line.qty - 1);
        }
    },
});
