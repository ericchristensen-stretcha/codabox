# -*- coding: utf-8 -*-
# This file is part of Odoo. The COPYRIGHT file at the top level of
# this module contains the full copyright notices and license terms.

import json
import logging

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import config

import requests
from requests.auth import HTTPBasicAuth

# prototype usage : config.get_misc('mssql','mssql_driver','Undefined')

_logger = logging.getLogger(__name__)
cbx_getcredentials = "/get-credentials/"
cbx_getlicences = "/peppol/licences/"
cbx_requesttoken = "/request-token/"


class CodaboxMaster(models.Model):
    _name = "codabox.master"

    # SOC #
    name = fields.Many2one(comodel_name="res.partner", string="License Owner")
    xcompkey = fields.Char("X Company Key")
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

    def switch_to_form_view(self):
        ir_model_data = self.env["ir.model.data"]
        view = ir_model_data.get_object_reference(
            "codabox_master", "view_codabox_master_form"
        )
        _logger.debug("view: %s", view[1])
        return {
            "view_type": "form",
            "view_mode": "form",
            "view_id": view[1],
            "res_model": "codabox.master",
            "type": "ir.actions.act_window",
            "nodestroy": True,
            "target": "current",
            "res_id": self.id,
        }

    def request_list_licences(self):
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


class CodaboxClients(models.Model):
    _name = "codabox.clients"

    # SOC #
    name = fields.Many2one(comodel_name="res.partner", string="License Owner")
    master = fields.Many2one(comodel_name="codabox.master", string="Master Owner")
    email = fields.Char("Email")
    qty_invoice = fields.Integer("Invoice quantity")
    license_id = fields.Char("License ID")
    status = fields.Char("Codabox Status")
    date_status = fields.Datetime("Codabox Status date")
    active = fields.Boolean("Active", default=True)
    token = fields.Char("Sender Token")
    # EOC #

    @api.onchange("name")
    def onchange_name(self):
        self.email = self.name.email
        self.qty_invoice = 100

    def switch_to_form_view(self):
        ir_model_data = self.env["ir.model.data"]
        view = ir_model_data.get_object_reference(
            "codabox_master", "view_codabox_client_licenses_form"
        )
        _logger.debug("view: %s", view[1])
        return {
            "view_type": "form",
            "view_mode": "form",
            "view_id": view[1],
            "res_model": "codabox.clients",
            "type": "ir.actions.act_window",
            "nodestroy": True,
            "target": "current",
            "res_id": self.id,
        }

    def request_update_invoice_qty(self):
        payload = {
            "invoice_quantity": self.qty_invoice,
        }
        self.request_update_license(payload)

    def request_deactivate_license(self):
        payload = {
            "state": "inactive",
        }
        self.request_update_license(payload)

    def request_reactivate_license(self):
        payload = {
            "state": "active",
        }
        self.request_update_license(payload)

    def request_update_license(self, payload):
        headers = {
            "X-Software-Company": self.master.xcompkey,
            "Content-Type": "application/json",
        }
        sp = config.get_misc("codabox", "cbx_service_point", "")
        _logger.debug(
            "Requested endpoint: %s", sp + cbx_getlicences + self.license_id + "/"
        )
        result = requests.put(
            sp + cbx_getlicences + self.license_id + "/",
            headers=headers,
            data=json.dumps(payload, separators=(",", ":")),
            auth=HTTPBasicAuth(self.master.username, self.master.password),
            verify=True,
        )
        if result.status_code == 200:
            json_result = result.json()
            _logger.debug("request_update_invoice_qty response: %s", json_result)
            if self.qty_invoice != json_result["invoice_quantity"]:
                raise ValidationError(
                    _(
                        "Operation failed with status code: %s\n%s"
                        % (
                            result.status_code,
                            result.text,
                        )
                    )
                )
            self.status = json_result["state"]
            self.date_status = (
                json_result["state_date"][0:10] + " " + json_result["state_date"][11:]
            )
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

    def request_get_license(self):
        headers = {
            "X-Software-Company": self.master.xcompkey,
            "Content-Type": "application/json",
        }
        sp = config.get_misc("codabox", "cbx_service_point", "")
        # the next request will create the license and obtain a license id
        payload = {
            "email": self.email,
            "invoice_quantity": self.qty_invoice,
        }
        _logger.debug(
            "Requested endpoint: %s - %s",
            sp + cbx_getlicences,
            json.dumps(payload, separators=(",", ":")),
        )
        result = requests.post(
            sp + cbx_getlicences,
            headers=headers,
            data=json.dumps(payload, separators=(",", ":")),
            auth=HTTPBasicAuth(self.master.username, self.master.password),
            verify=True,
        )
        if result.status_code == 201:
            json_result = result.json()
            _logger.debug("request_get_license response: %s", json_result)
            self.status = json_result["state"]
            self.date_status = (
                json_result["state_date"][0:10] + " " + json_result["state_date"][11:]
            )
            self.license_id = json_result["id"]
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
        # also request a token if the previous operation was successful
        self.request_get_license_token()

    def request_get_license_token(self):
        headers = {
            "X-Software-Company": self.master.xcompkey,
            "Content-Type": "application/json",
        }
        sp = config.get_misc("codabox", "cbx_service_point", "")
        # the next request will obtain a token for the given license
        _logger.debug(
            "Requested endpoint: %s",
            sp + cbx_getlicences + self.license_id + cbx_requesttoken,
        )
        result = requests.post(
            sp + cbx_getlicences + self.license_id + cbx_requesttoken,
            headers=headers,
            auth=HTTPBasicAuth(self.master.username, self.master.password),
            verify=True,
        )
        if result.status_code == 201:
            json_result = result.json()
            _logger.debug("request_get_license_token response: %s", json_result)
            self.token = json_result["token"]
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
