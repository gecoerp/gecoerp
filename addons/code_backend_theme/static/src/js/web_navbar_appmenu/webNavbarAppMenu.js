/** @odoo-module **/

import { NavBar } from '@web/webclient/navbar/navbar';
import { patch } from "@web/core/utils/patch";

import {
    Component,
    onMounted,
    useRef,
    onWillUnmount,
} from "@odoo/owl";

patch(NavBar.prototype, {
    setup() {
        super.setup();
        this.openElement = useRef("openSidebar");
        this.closeElement = useRef("closeSidebar");
        this.topHeading = useRef("top_heading");
        this.mainNavBar = useRef("o_main_navbar");
        this.sidebarLinks = useRef("sidebarLinks");
        const sidebarLinkHandler = this.handleSidebarLinkClick.bind(this);
        const openSidebarHandler = this.openSidebar.bind(this);
        const closeSidebarHandler = this.closeSidebar.bind(this);

        onMounted(() => {
            const openSidebarElement = this.openElement?.el || document.getElementById('openSidebar');
            const closeSidebarElement = this.closeElement?.el || document.getElementById('closeSidebar');
            const sidebarLinksEl = this.sidebarLinks?.el || document.querySelector('.sidebar_menu');
            const sidebarLinkElements = sidebarLinksEl ? sidebarLinksEl.children : [];

            if (sidebarLinkElements && sidebarLinkElements.length) {
                Array.from(sidebarLinkElements).forEach(link => {
                    link.addEventListener('click', sidebarLinkHandler);
                });
            }
            if (openSidebarElement) {
                openSidebarElement.addEventListener('click', openSidebarHandler);
            }
            if (closeSidebarElement) {
                closeSidebarElement.addEventListener('click', closeSidebarHandler);
            }
        });

        onWillUnmount(() => {
            const openSidebarElement = this.openElement?.el || document.getElementById('openSidebar');
            const closeSidebarElement = this.closeElement?.el || document.getElementById('closeSidebar');
            const sidebarLinksEl = this.sidebarLinks?.el || document.querySelector('.sidebar_menu');
            const sidebarLinkElements = sidebarLinksEl ? sidebarLinksEl.children : [];

            if (openSidebarElement) {
                openSidebarElement.removeEventListener('click', openSidebarHandler);
            }
            if (closeSidebarElement) {
                closeSidebarElement.removeEventListener('click', closeSidebarHandler);
            }
            if (sidebarLinkElements && sidebarLinkElements.length) {
                Array.from(sidebarLinkElements).forEach(link => {
                    link.removeEventListener('click', sidebarLinkHandler);
                });
            }
        });
    },

    openSidebar() {
        const nextElem = this.root?.el?.nextElementSibling || document.querySelector('.o_action_manager');
        if (nextElem) {
            nextElem.style.marginLeft = '200px';
            nextElem.style.transition = 'all .15s ease-in-out';
        }
        const openSidebarElement = this.openElement?.el || document.getElementById('openSidebar');
        const closeSidebarElement = this.closeElement?.el || document.getElementById('closeSidebar');
        const sidebarPanel = document.getElementById('sidebar_panel');

        if (openSidebarElement) openSidebarElement.style.display = 'none';
        if (closeSidebarElement) closeSidebarElement.style.display = 'block';
        if (sidebarPanel) sidebarPanel.style.display = 'block';

        if (this.topHeading?.el) {
            this.topHeading.el.style.marginLeft = '200px';
            this.topHeading.el.style.transition = 'all .15s ease-in-out';
            this.topHeading.el.style.width = 'auto';
        }
    },

    closeSidebar() {
        const nextElem = this.root?.el?.nextElementSibling || document.querySelector('.o_action_manager');
        if (nextElem) {
            nextElem.style.marginLeft = '0px';
            nextElem.style.transition = 'all .15s ease-in-out';
        }
        const openSidebarElement = this.openElement?.el || document.getElementById('openSidebar');
        const closeSidebarElement = this.closeElement?.el || document.getElementById('closeSidebar');
        const sidebarPanel = document.getElementById('sidebar_panel');

        if (openSidebarElement) openSidebarElement.style.display = 'block';
        if (closeSidebarElement) closeSidebarElement.style.display = 'none';
        if (sidebarPanel) sidebarPanel.style.display = 'none';

        if (this.topHeading?.el) {
            this.topHeading.el.style.marginLeft = '0px';
            this.topHeading.el.style.width = '100%';
        }
    },

    handleSidebarLinkClick(event) {
        const closeSidebarElement = this.closeElement?.el || document.getElementById('closeSidebar');
        if (closeSidebarElement) closeSidebarElement.style.display = 'none';
        if (this.topHeading?.el) {
            this.topHeading.el.style.marginLeft = '0px';
            this.topHeading.el.style.width = '100%';
        }
        const li = event.currentTarget;
        const a = li.querySelector('a');
        if (a) {
            const id = a.getAttribute('data-id');
            const header = document.querySelector('header');
            if (header && id) header.className = id;
            
            const sidebarLinksEl = this.sidebarLinks?.el || document.querySelector('.sidebar_menu');
            if (sidebarLinksEl) {
                Array.from(sidebarLinksEl.children).forEach(item => {
                    const itemLink = item.querySelector('a');
                    if (itemLink) itemLink.classList.remove('active');
                });
            }
            a.classList.add('active');
        }
        this.closeSidebar();
    }
});