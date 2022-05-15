# -*- coding: utf-8 -*-
# This file is part of Odoo. The COPYRIGHT file at the top level of
# this module contains the full copyright notices and license terms.

import logging

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

cbx_checkpresense = "/peppol/receiver/check-presence/"


class CodaboxListLicences(models.TransientModel):
    _name = "codabox.list_licences"

    # SOC #
    name = fields.Many2one(comodel_name="codabox.master", string="Master")
    # EOC

    @api.multi
    def do_action(self):
        self.ensure_one()
        for formdata in self:
            result = formdata.name.request_list_licences()
            _logger.debug("JSON Result: %s", result)
            raise ValidationError(_("Response received:\n%s" % result))
        return {"type": "ir.actions.act_window_close"}
