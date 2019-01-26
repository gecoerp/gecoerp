# -*- coding: utf-8 -*-

import gecoerp

def migrate(cr, version):
    registry = gecoerp.registry(cr.dbname)
    from gecoerp.addons.account.models.chart_template import migrate_tags_on_taxes
    migrate_tags_on_taxes(cr, registry)
