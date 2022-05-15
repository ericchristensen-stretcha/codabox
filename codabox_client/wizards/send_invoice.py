# -*- coding: utf-8 -*-
# This file is part of Odoo. The COPYRIGHT file at the top level of
# this module contains the full copyright notices and license terms.

import logging

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

cbx_upload_invoice = "/peppol/receiver/check-presence/"


class CodaboxUploadInvoice(models.TransientModel):
    _name = "codabox.upload_invoice"

    # SOC #
    name = fields.Many2one(comodel_name="codabox.client", string="License Owner")
    ubl_file = fields.Many2one(
        comodel_name="ir.attachment", string="Available attachments"
    )
    active_domain = fields.Many2many(
        comodel_name="ir.attachment", string="Active Domain"
    )
    # EOC

    @api.multi
    def _get_attached_ubls(self):
        _logger.debug(self._context)
        attached_ubls = self.env["ir.attachment"].search(
            [
                ("res_model", "=", "account.invoice"),
                ("res_id", "=", self._context["active_id"]),
            ]
        )
        _logger.debug("List of attached ubls: %s", attached_ubls)
        return attached_ubls

    @api.multi
    def do_action(self):
        self.ensure_one()
        for formdata in self:
            result = formdata.name.codabox_upload_ubl(attachment=formdata.ubl_file)
            _logger.debug("JSON Result: %s", result)
            raise ValidationError(_("Response received:\n%s" % result))
        return {"type": "ir.actions.act_window_close"}

    def default_get(self, fields):
        res = super(CodaboxUploadInvoice, self).default_get(fields or [])
        res = {}
        # select the one and only license owner
        lo = self.env["codabox.client"].search([])
        res["name"] = lo[0].id
        res["active_domain"] = self._get_attached_ubls().ids
        return res
