# -*- coding: utf-8 -*-
# This file is part of Odoo. The COPYRIGHT file at the top level of
# this module contains the full copyright notices and license terms.

import logging

from lxml import etree

from odoo import models

logger = logging.getLogger(__name__)


class AccountInvoice(models.Model):
    _name = "account.invoice"
    _inherit = ["account.invoice", "base.ubl"]

    def _ubl_add_header(self, parent_node, ns, version="2.1"):
        ubl_version = etree.SubElement(parent_node, ns["cbc"] + "UBLVersionID")
        ubl_version.text = version
        # Peppol CustomizationID & Profile
        if self.type == "out_invoice":
            customization_id = (
                "urn:www.cenbii.eu:transaction:biitrns010:"
                "ver2.0:extended:urn:www.peppol.eu:bis:peppol4a:ver2.0::2.1"
            )
            profile_id = "urn:www.cenbii.eu:profile:bii04:ver2.0"
        if self.type == "out_refund":
            customization_id = (
                "urn:www.cenbii.eu:transaction:biitrns014:"
                "ver2.0:extended:urn:www.peppol.eu:bis:peppol5a:ver2.0::2.1"
            )
            profile_id = "urn:www.cenbii.eu:profile:bii04:ver2.0"
        customizationid = etree.SubElement(parent_node, ns["cbc"] + "CustomizationID")
        customizationid.text = customization_id
        profileid = etree.SubElement(parent_node, ns["cbc"] + "ProfileID")
        profileid.text = profile_id
        doc_id = etree.SubElement(parent_node, ns["cbc"] + "ID")
        doc_id.text = self.number
        issue_date = etree.SubElement(parent_node, ns["cbc"] + "IssueDate")
        issue_date.text = self.date_invoice
        type_code = etree.SubElement(parent_node, ns["cbc"] + "InvoiceTypeCode")
        if self.type == "out_invoice":
            type_code.text = "380"
        elif self.type == "out_refund":
            type_code.text = "381"
        if self.comment:
            note = etree.SubElement(parent_node, ns["cbc"] + "Note")
            note.text = self.comment
        doc_currency = etree.SubElement(parent_node, ns["cbc"] + "DocumentCurrencyCode")
        doc_currency.text = self.currency_id.name
