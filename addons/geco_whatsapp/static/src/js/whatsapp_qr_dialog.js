/** @odoo-module **/

import { Dialog } from "@web/core/dialog/dialog";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Component, useState, onWillStart, onWillUnmount } from "@odoo/owl";

const POLL_INTERVAL_MS = 2000;
const CLOSE_DELAY_MS = 1500;

export class GecoWhatsappQrDialog extends Component {
    setup() {
        this.orm = useService("orm");
        this.state = useState({
            status: "starting",
            qrCode: null,
            phone: null,
        });

        onWillStart(() => this.poll());
        this.timer = setInterval(() => this.poll(), POLL_INTERVAL_MS);
        onWillUnmount(() => clearInterval(this.timer));
    }

    async poll() {
        try {
            const result = await this.orm.call(
                "geco.whatsapp.account", "get_qr_status", [[this.props.accountId]],
            );
            this.state.status = result.status || "starting";
            this.state.qrCode = result.qr_code || null;
            this.state.phone = result.phone || null;
            if (this.state.status === "connected") {
                clearInterval(this.timer);
                setTimeout(() => this.props.close(), CLOSE_DELAY_MS);
            }
        } catch (error) {
            this.state.status = "error";
        }
    }
}
GecoWhatsappQrDialog.components = { Dialog };
GecoWhatsappQrDialog.template = "geco_whatsapp.QrDialog";
GecoWhatsappQrDialog.props = {
    accountId: Number,
    close: Function,
};

function openQrDialog(env, action) {
    const accountId = action.params && action.params.account_id;
    env.services.dialog.add(GecoWhatsappQrDialog, { accountId });
}

registry.category("actions").add("geco_whatsapp_qr_dialog", openQrDialog);
