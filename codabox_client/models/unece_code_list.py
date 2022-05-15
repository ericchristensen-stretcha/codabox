# -*- coding: utf-8 -*-
# This file is part of Odoo. The COPYRIGHT file at the top level of
# this module contains the full copyright notices and license terms.

import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class UneceCodeList(models.Model):
    _inherit = "unece.code.list"

    # SOC #
    scheme_id = fields.Char("Scheme ID", size=16)
    # EOC #

    def _auto_init(self):
        _logger.debug("_auto_init incoming self: %s", self)
        res = super(UneceCodeList, self)._auto_init()
        query = """update unece_code_list set scheme_id =%s where type=%s"""
        todos = [
            (
                "UNCL4461",
                "payment_means",
            ),
            (
                "UNCL5153",
                "tax_type",
            ),
            (
                "UNCL5305",
                "tax_categ",
            ),
            (
                "UNTDID2005",
                "date",
            ),
        ]
        for todo in todos:
            self._cr.execute(query, todo)
        return res
