# Part of UNO, GECOERP. See LICENSE file for full copyright and licensing details.

import gecoerp.tests


@gecoerp.tests.common.at_install(False)
@gecoerp.tests.common.post_install(True)
class TestUi(gecoerp.tests.HttpCase):
    
    def test_01_main_flow_tour(self):
        self.phantom_js("/web", "gecoerp.__DEBUG__.services['web_tour.tour'].run('main_flow_tour')", "gecoerp.__DEBUG__.services['web_tour.tour'].tours.main_flow_tour.ready", login="admin", timeout=180)
