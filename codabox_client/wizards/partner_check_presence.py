# -*- coding: utf-8 -*-
# This file is part of Odoo. The COPYRIGHT file at the top level of
# this module contains the full copyright notices and license terms.

import logging

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

cbx_checkpresense = "/peppol/receiver/check-presence/"


class CodaboxPartnerCheckPresence(models.TransientModel):
    _name = "codabox.partner_check_presence"

    # SOC #
    name = fields.Many2one(comodel_name="codabox.client", string="License Owner")
    partner_id = fields.Many2one(
        comodel_name="res.partner", string="Check presence for"
    )
    # EOC

    @api.multi
    def do_action(self):
        self.ensure_one()
        for formdata in self:
            # get the KBO code l10n_be_kbo_bce
            id_number_id = formdata.partner_id.id_numbers.filtered(
                lambda r: r.category_id.code == "l10n_be_kbo_bce"
            )
            if len(id_number_id) != 1:
                raise ValidationError(_("No KBO_CBE code could be located!"))
            result = formdata.name.codabox_check_presence(
                scheme_id="BE:CBE", value="%s" % id_number_id.name.replace(".", "")
            )
            _logger.debug("JSON Result: %s", result)
            raise ValidationError(_("Response received:\n%s" % result))
        return {"type": "ir.actions.act_window_close"}
