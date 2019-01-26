# Part of UNO, GECOERP. See LICENSE file for full copyright and licensing details.

import gecoerp.tests


@gecoerp.tests.common.at_install(False)
@gecoerp.tests.common.post_install(True)
class TestUi(gecoerp.tests.HttpCase):
    def test_admin(self):
        self.phantom_js("/", "gecoerp.__DEBUG__.services['web_tour.tour'].run('blog')", "gecoerp.__DEBUG__.services['web_tour.tour'].tours.blog.ready", login='admin')
