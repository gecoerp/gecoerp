/** @odoo-module */
import { NavBar } from "@web/webclient/navbar/navbar";
import { patch } from "@web/core/utils/patch";

patch(NavBar.prototype, {
    setup() {
        super.setup();
        this._checkMobileView = this._checkMobileView.bind(this);
        window.addEventListener('resize', this._checkMobileView);
    },

    _checkMobileView() {
        this.state = this.state || {};
        const wasMobile = this.state.isMobile;
        this.state.isMobile = window.innerWidth <= 768;

        if (wasMobile !== this.state.isMobile) {
            this._adjustLayoutForDevice();
        }
    },

    _adjustLayoutForDevice() {
        const sidebarPanel = document.querySelector('#sidebar_panel');
        const actionManager = document.querySelector('.o_action_manager');

        if (!sidebarPanel || !actionManager) return;

        if (this.state.isMobile) {
            sidebarPanel.classList.add('mobile-view');
            actionManager.style.marginLeft = '0';
            sidebarPanel.style.display = 'none';
        } else {
            sidebarPanel.classList.remove('mobile-view');
            if (document.querySelector('#openSidebar .fa')?.classList.contains('opened')) {
                actionManager.style.marginLeft = '300px';
            }
        }
    },

    openSidebar(ev) {
        if (ev) ev.preventDefault();
        const sidebarPanel = document.querySelector('#sidebar_panel');
        const actionManager = document.querySelector('.o_action_manager');
        const icon = document.querySelector('#openSidebar .fa');

        if (!sidebarPanel) return;

        const isOpening = !sidebarPanel.classList.contains('opened');

        if (isOpening) {
            sidebarPanel.style.display = 'block';
            sidebarPanel.classList.add('opened');
            icon?.classList.add('opened');
            if (!this.state?.isMobile && actionManager) {
                actionManager.style.marginLeft = '300px';
                actionManager.style.transition = 'margin-left 0.25s cubic-bezier(0.4, 0, 0.2, 1)';
            }
        } else {
            sidebarPanel.style.display = 'none';
            sidebarPanel.classList.remove('opened');
            icon?.classList.remove('opened');
            if (actionManager) {
                actionManager.style.marginLeft = '0';
                actionManager.style.transition = 'margin-left 0.25s cubic-bezier(0.4, 0, 0.2, 1)';
            }
        }
    },

    closeSidebar(ev) {
        if (ev) ev.preventDefault();
        this._toggleSidebar(false);
    },

    _toggleSidebar(show) {
        const sidebarPanel = document.querySelector('#sidebar_panel');
        const actionManager = document.querySelector('.o_action_manager');
        const icon = document.querySelector('#openSidebar .fa');

        if (!sidebarPanel) return;

        if (show) {
            sidebarPanel.style.display = 'block';
            sidebarPanel.classList.add('opened');
            icon?.classList.add('opened');
            if (!this.state?.isMobile && actionManager) {
                actionManager.style.marginLeft = '300px';
                actionManager.style.transition = 'margin-left 0.25s cubic-bezier(0.4, 0, 0.2, 1)';
            }
        } else {
            sidebarPanel.style.display = 'none';
            sidebarPanel.classList.remove('opened');
            icon?.classList.remove('opened');
            if (actionManager) {
                actionManager.style.marginLeft = '0';
                actionManager.style.transition = 'margin-left 0.25s cubic-bezier(0.4, 0, 0.2, 1)';
            }
        }
    }
});
