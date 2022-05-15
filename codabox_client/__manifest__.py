# -*- coding: utf-8 -*-
# This file is part of Odoo. The COPYRIGHT file at the top level of
# this module contains the full copyright notices and license terms.

{
    "name": "Codabox Client Manager",
    "summary": "Client support for codabox",
    "version": "10.0.1.0.0",
    "license": "AGPL-3",
    "depends": ["base", "account", "account_invoice_ubl"],
    "author": "Noviat, Eric Christensen",
    "category": "Others",
    "website": "http://www.noviat.com",
    "data": [
        "wizards/activate_client_license.xml",
        "wizards/partner_check_presence.xml",
        "wizards/send_invoice.xml",
        "views/codabox_client_views.xml",
        "views/codabox_client_menus.xml",
        "views/unece_code_list.xml",
    ],
    "demo": [],
    "images": [],
    "installable": True,
    "auto_install": False,
}
