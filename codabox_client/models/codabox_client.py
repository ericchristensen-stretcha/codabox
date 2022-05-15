# -*- coding: utf-8 -*-
# This file is part of Odoo. The COPYRIGHT file at the top level of
# this module contains the full copyright notices and license terms.

import base64
import json
import logging
from cStringIO import StringIO

from odoo import _, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import config

import requests
from requests.auth import HTTPBasicAuth

# prototype usage : config.get_misc('mssql','mssql_driver','Undefined')

_logger = logging.getLogger(__name__)
cbx_getcredentials = "/get-credentials/"
cbx_checkpresence = "/peppol/receiver/check-presence/"
cbx_getlicences = "/peppol/licences/"
cbx_uploadubl = "/peppol/licences/###LID###/upload/"


class CodaboxClient(models.Model):
    _name = "codabox.client"

    # SOC #
    name = fields.Many2one(comodel_name="res.partner", string="License Owner")
    xcompkey = fields.Char("X Company Key")
    licence = fields.Char("Licence")
    token = fields.Char("Token")
    username = fields.Char("Username")
    password = fields.Char("Password")
    # EOC #

    def request_uid_pwd(self):
        if self.username or self.password:
            raise ValidationError(
                _(
                    "Username and password were already retrieved from Codabox environment"
                )
            )
        headers = {"X-Software-Company": self.xcompkey}
        sp = config.get_misc("codabox", "cbx_service_point", "")
        _logger.debug("Service URL: %s", sp + cbx_getcredentials + self.token + "/")
        result = requests.get(
            sp + cbx_getcredentials + self.token + "/", headers=headers, verify=True
        )
        _logger.debug("request_uid_pwd response: %s", result.text)
        if result.status_code == 200:
            json_result = result.json()
            _logger.debug("request_uid_pwd response: %s", json_result)
            self.username = json_result["username"]
            self.password = json_result["password"]
        else:
            raise ValidationError(
                _(
                    "Operation failed with status code: %s\n%s"
                    % (
                        result.status_code,
                        result.text,
                    )
                )
            )

    def request_licence(self):
        headers = {
            "X-Software-Company": self.xcompkey,
            "Content-Type": "application/json",
        }
        sp = config.get_misc("codabox", "cbx_service_point", "")
        _logger.debug("Service URL: %s", sp + cbx_getlicences)
        result = requests.get(
            sp + cbx_getlicences,
            headers=headers,
            auth=HTTPBasicAuth(self.username, self.password),
            verify=True,
        )
        _logger.debug("request_uid_pwd response: %s", result.text)
        if result.status_code == 200:
            json_result = result.json()
            _logger.debug("request_uid_pwd response: %s", json_result)
            self.licence = self.password = json_result[0]["id"]
        else:
            raise ValidationError(
                _(
                    "Operation failed with status code: %s\n%s"
                    % (
                        result.status_code,
                        result.text,
                    )
                )
            )

    def switch_to_form_view(self):
        ir_model_data = self.env["ir.model.data"]
        view = ir_model_data.get_object_reference(
            "codabox_client", "view_codabox_client_form"
        )
        _logger.debug("view: %s", view[1])
        return {
            "view_type": "form",
            "view_mode": "form",
            "view_id": view[1],
            "res_model": "codabox.client",
            "type": "ir.actions.act_window",
            "nodestroy": True,
            "target": "current",
            "res_id": self.id,
        }

    def codabox_post_request(
        self, headers=None, endpoint=None, payload=None, attachment=None
    ):
        if headers is None:
            headers = {"X-Software-Company": self.xcompkey}
            sp = config.get_misc("codabox", "cbx_service_point", "")
            # the next request will create the license and obtain a license id
        if payload is None:
            payload = {}
        else:
            headers.update({"Content-Type": "application/json"})
        files = {}
        if attachment:
            f_content = base64.b64decode(attachment.datas)
            files = {
                "file": (
                    attachment.name,
                    StringIO(f_content),
                    "application/xml",
                    {"Expires": "0"},
                )
            }
            # files = { 'file' : (attachment.name, f_content)}
        _logger.debug(
            "Requested endpoint: %s - %s",
            sp + endpoint,
            json.dumps(payload, separators=(",", ":")),
        )
        if payload:
            result = requests.post(
                sp + endpoint,
                headers=headers,
                data=json.dumps(payload, separators=(",", ":")),
                auth=HTTPBasicAuth(self.username, self.password),
                verify=True,
            )
        if files:
            result = requests.post(
                sp + endpoint,
                headers=headers,
                auth=HTTPBasicAuth(self.username, self.password),
                files=files,
                verify=True,
            )
        _logger.debug("Post result: %s", result)
        return result

    def codabox_check_presence(self, scheme_id="BE:VAT", value=None):
        payload = {
            "scheme_id": scheme_id,
            "value": value,
        }
        result = self.codabox_post_request(
            headers=None, endpoint=cbx_checkpresence, payload=payload
        )
        if result.status_code == 200:
            json_result = result.json()
            return json_result
        else:
            raise ValidationError(
                _(
                    "Operation failed with status code: %s\n%s"
                    % (
                        result.status_code,
                        result.text,
                    )
                )
            )

    def codabox_upload_ubl(self, attachment=None):
        cbx_endpoint = cbx_uploadubl.replace("###LID###", self.licence)
        result = self.codabox_post_request(
            headers=None, endpoint=cbx_endpoint, attachment=attachment
        )
        if result.status_code == 200:
            json_result = result.json()
            return json_result
        else:
            raise ValidationError(
                _(
                    "Operation failed with status code: %s\n%s"
                    % (
                        result.status_code,
                        result.text,
                    )
                )
            )
