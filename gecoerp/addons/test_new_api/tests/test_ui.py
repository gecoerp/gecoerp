import gecoerp.tests

class TestUi(gecoerp.tests.HttpCase):
    post_install = True
    at_install = False

    def test_01_admin_widget_x2many(self):
        self.phantom_js("/web#action=test_new_api.action_discussions",
                        "gecoerp.__DEBUG__.services['web_tour.tour'].run('widget_x2many', 100)",
                        "gecoerp.__DEBUG__.services['web_tour.tour'].tours.widget_x2many.ready",
                        login="admin", timeout=120)
