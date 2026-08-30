/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { useService } from "@web/core/utils/hooks";
import { Component, status } from "@odoo/owl";
import { patch } from "@web/core/utils/patch";
import { PhoneField, phoneField, formPhoneField } from "@web/views/fields/phone/phone_field";

export class SendGecoWhatsappButton extends Component {
    setup() {
        this.action = useService("action");
        this.user = useService("user");
        this.title = _t("Enviar por WhatsApp");
    }
    async onClick() {
        await this.props.record.save();
        this.action.doAction(
            {
                type: "ir.actions.act_window",
                target: "new",
                name: this.title,
                res_model: "geco.whatsapp.compose",
                views: [[false, "form"]],
                context: {
                    ...this.user.context,
                    active_model: this.props.record.resModel,
                    active_id: this.props.record.resId,
                    default_phone: this.props.record.data[this.props.name],
                },
            },
            {
                onClose: () => {
                    if (status(this) === "destroyed") {
                        return;
                    }
                    this.props.record.load();
                },
            }
        );
    }
}
SendGecoWhatsappButton.template = "geco_whatsapp.SendGecoWhatsappButton";
SendGecoWhatsappButton.props = ["*"];

patch(PhoneField, {
    components: {
        ...PhoneField.components,
        SendGecoWhatsappButton,
    },
    defaultProps: {
        ...PhoneField.defaultProps,
        enableGecoWhatsapp: true,
    },
    props: {
        ...PhoneField.props,
        enableGecoWhatsapp: { type: Boolean, optional: true },
    },
});

const patchDescr = () => ({
    extractProps({ options }) {
        const props = super.extractProps(...arguments);
        props.enableGecoWhatsapp = options.enable_geco_whatsapp !== false;
        return props;
    },
    supportedOptions: [{
        label: _t("Habilitar botón de WhatsApp"),
        name: "enable_geco_whatsapp",
        type: "boolean",
        default: true,
    }],
});

patch(phoneField, patchDescr());
patch(formPhoneField, patchDescr());
