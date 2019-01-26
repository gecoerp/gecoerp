gecoerp.define('iap.redirect_gecoerp_credit_widget', function(require) {
"use strict";

var core = require('web.core');
var framework = require('web.framework');
var Widget = require('web.Widget');
var QWeb = core.qweb;


var IapGECOERPCreditRedirect = Widget.extend({
    template: 'iap.redirect_to_gecoerp_credit',
    events : {
        "click .redirect_confirm" : "gecoerp_redirect",
    },
    init: function (parent, action) {
        this._super(parent, action);
        this.url = action.params.url;
    },

    gecoerp_redirect: function () {
        window.open(this.url, '_blank');
        this.do_action({type: 'ir.actions.act_window_close'});
        // framework.redirect(this.url);
    },

});
core.action_registry.add('iap_gecoerp_credit_redirect', IapGECOERPCreditRedirect);
});
