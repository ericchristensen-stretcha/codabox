# -*- coding: utf-8 -*-
# This file is part of Odoo. The COPYRIGHT file at the top level of
# this module contains the full copyright notices and license terms.

{
    "name": "Codabox License Manager",
    "summary": "License Manager for the Codabox Environment",
    "version": "10.0.1.0.0",
    "license": "AGPL-3",
    "depends": ["base", "mail"],
    "author": "Noviat, Eric Christensen",
    "category": "Others",
    "website": "http://www.noviat.com",
    "data": [
        "data/email_template.xml",
        "wizards/list_of_licences.xml",
        "views/codabox_master_views.xml",
        "views/codabox_master_menus.xml",
    ],
    "demo": [],
    "images": [],
    "installable": True,
    "auto_install": False,
}
