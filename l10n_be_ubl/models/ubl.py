# -*- coding: utf-8 -*-
# This file is part of Odoo. The COPYRIGHT file at the top level of
# this module contains the full copyright notices and license terms.

import logging

from odoo import api, models

_logger = logging.getLogger(__name__)

cbx_upload_invoice = "/peppol/receiver/check-presence/"


class BaseUbl(models.AbstractModel):
    _inherit = "base.ubl"

    @api.model
    def _ubl_get_party_identification(self, commercial_partner):
        """This method is designed to be inherited in localisation modules
        Should return a dict with key=SchemeName, value=Identifier"""

        if commercial_partner.vat:
            return {"BE:VAT": commercial_partner.vat}
        else:
            # get the KBO code l10n_be_kbo_bce
            id_number_id = commercial_partner.id_numbers.filtered(
                lambda r: r.category_id.code == "l10n_be_kbo_bce"
            )
            if len(id_number_id) == 1:
                value = self.env["res.partner"]._sanitize_vat(id_number_id.name)
                return {"BE:CBE": value}
        _logger.debug("No valid BE:VAT or BE:CBE code could be located!")
        return {}
