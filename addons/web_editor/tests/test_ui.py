# -*- coding: utf-8 -*-
# Part of Odoo, GECOERP. See LICENSE file for full copyright and licensing details.

import gecoerp.tests

@gecoerp.tests.common.at_install(False)
@gecoerp.tests.common.post_install(True)
class TestUi(gecoerp.tests.HttpCase):

    post_install = True
    at_install = False

    def test_01_admin_rte(self):
        self.phantom_js("/web", "gecoerp.__DEBUG__.services['web_tour.tour'].run('rte')", "gecoerp.__DEBUG__.services['web_tour.tour'].tours.rte.ready", login='admin')

    def test_02_admin_rte_inline(self):
        self.phantom_js("/web", "gecoerp.__DEBUG__.services['web_tour.tour'].run('rte_inline')", "gecoerp.__DEBUG__.services['web_tour.tour'].tours.rte_inline.ready", login='admin')
