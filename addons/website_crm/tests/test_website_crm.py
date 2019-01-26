# -*- coding: utf-8 -*-
# Part of UNO, GECOERP. See LICENSE file for full copyright and licensing details.

from gecoerp.api import Environment
import gecoerp.tests


@gecoerp.tests.common.at_install(False)
@gecoerp.tests.common.post_install(True)
class TestWebsiteCrm(gecoerp.tests.HttpCase):

    def test_tour(self):
        self.phantom_js("/", "gecoerp.__DEBUG__.services['web_tour.tour'].run('website_crm_tour')", "gecoerp.__DEBUG__.services['web_tour.tour'].tours.website_crm_tour.ready")

        # need environment using the test cursor as it's not committed
        cr = self.registry.cursor()
        assert cr is self.registry.test_cr
        env = Environment(cr, self.uid, {})
        record = env['crm.lead'].search([('description', '=', '### TOUR DATA ###')])
        assert len(record) == 1
        assert record.contact_name == 'John Smith'
        assert record.email_from == 'john@smith.com'
        assert record.partner_name == 'GECOERP S.A.'
