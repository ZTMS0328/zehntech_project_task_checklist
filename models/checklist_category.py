# Copyright (C) 2024-2025 Zehntech Technologies Inc. <odoo-support@zehntech.com>
# License OPL-1 (https://www.odoo.com/documentation/user/legal/licenses.html)
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ProjectChecklist(models.Model):
    _name = 'checklist.category'
    _description = "Checklist Category"

    name = fields.Char(
        string='Name',
        required=True,
        translate=True, export_string_translation=True,
        help='Enter a unique name for the checklist category. This name will identify the category within the system and should be meaningful.'
    )
    description = fields.Char(
        string='Description',
        translate=True, export_string_translation=True,
        help='Provide a short description of the checklist category. This will help users understand the purpose or scope of this category.'
    )
    group_permission = fields.Many2one(
        'res.groups', 
        string='User Group',
        help='Select a user group that has permission to access and manage this checklist category. Only users in the selected group can modify or view checklists in this category.'
    )

    # A table CONSTRAINT can't reference an expression like lower(name) in
    # PostgreSQL (only a UNIQUE INDEX can) — enforcement is the ORM-level
    # constraint below.
    @api.constrains('name')
    def _check_name_unique(self):
        for record in self:
            existing = self.search([('id', '!=', record.id), ('name', '=ilike', record.name)])
            if existing:
                raise ValidationError(_("The Checklist Category name must be unique."))
