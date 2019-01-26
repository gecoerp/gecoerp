import gecoerp.tests
# Part of UNO, GECOERP. See LICENSE file for full copyright and licensing details.

@gecoerp.tests.common.at_install(False)
@gecoerp.tests.common.post_install(True)
class TestUi(gecoerp.tests.HttpCase):

    def test_01_sale_tour(self):
        self.phantom_js("/web", "gecoerp.__DEBUG__.services['web_tour.tour'].run('sale_tour')", "gecoerp.__DEBUG__.services['web_tour.tour'].tours.sale_tour.ready", login="admin")
