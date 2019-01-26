# -*- coding: utf-8 -*-

import gecoerp

def migrate(cr, version):
    registry = gecoerp.registry(cr.dbname)
    from gecoerp.addons.account.models.chart_template import migrate_set_tags_and_taxes_updatable
    migrate_set_tags_and_taxes_updatable(cr, registry, 'l10n_de_skr03')
