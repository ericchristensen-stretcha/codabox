# -*- coding: utf-8 -*-
# This file is part of Odoo. The COPYRIGHT file at the top level of
# this module contains the full copyright notices and license terms.

import logging

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

import xmltodict

_logger = logging.getLogger(__name__)


class CodaboxActivateClientLicense(models.TransientModel):
    _name = "codabox.activate_client_license"

    # SOC #
    name = fields.Many2one(comodel_name="res.partner", string="License Owner")
    license_info = fields.Text("License Info")
    # EOC

    @api.multi
    def do_action(self):
        self.ensure_one()
        for formdata in self:
            cdbxclient_obj = self.env["codabox.client"]
            records = cdbxclient_obj.search([("name.id", "=", formdata.name.id)])
            if len(records) > 0:
                raise ValidationError(_("Client record exist, none is expected!"))
            else:
                result = xmltodict.parse(formdata.license_info)
                v = {
                    "name": formdata.name.id,
                    "xcompkey": result["codabox_client"]["x-software-company"],
                    "token": result["codabox_client"]["token"],
                    "licence": result["codabox_client"]["licence"],
                }
                line_id = cdbxclient_obj.create(v)
                line_id.request_uid_pwd()
        return {"type": "ir.actions.act_window_close"}
