# -*- coding: utf-8 -*-
# Part of UNO, GECOERP. See LICENSE file for full copyright and licensing details.
import gecoerp.tests


@gecoerp.tests.common.at_install(False)
@gecoerp.tests.common.post_install(True)
class TestUi(gecoerp.tests.HttpCase):
    def test_01_admin_shop_tour(self):
        self.phantom_js("/", "gecoerp.__DEBUG__.services['web_tour.tour'].run('shop')", "gecoerp.__DEBUG__.services['web_tour.tour'].tours.shop.ready", login="admin")

    def test_02_admin_checkout(self):
        self.phantom_js("/", "gecoerp.__DEBUG__.services['web_tour.tour'].run('shop_buy_product')", "gecoerp.__DEBUG__.services['web_tour.tour'].tours.shop_buy_product.ready", login="admin")

    def test_03_demo_checkout(self):
        self.phantom_js("/", "gecoerp.__DEBUG__.services['web_tour.tour'].run('shop_buy_product')", "gecoerp.__DEBUG__.services['web_tour.tour'].tours.shop_buy_product.ready", login="demo")

    # TO DO - add public test with new address when convert to web.tour format.
