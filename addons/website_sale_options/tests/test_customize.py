# Part of UNO, GECOERP. See LICENSE file for full copyright and licensing details.

import gecoerp.tests

class TestUi(gecoerp.tests.HttpCase):

    post_install = True
    at_install = False

    def test_01_admin_shop_customize_tour(self):
        self.phantom_js("/", "gecoerp.__DEBUG__.services['web_tour.tour'].run('shop_customize')", "gecoerp.__DEBUG__.services['web_tour.tour'].tours.shop_customize.ready", login="admin")
