# Copyright (C) 2024-2025 Zehntech Technologies Inc. <odoo-support@zehntech.com>
# License OPL-1 (https://www.odoo.com/documentation/user/legal/licenses.html)
from odoo import models, fields, api, _

#Inherit the model project.atsk.type to add the restriction field in stages ceration form
class ProjectTaskStage(models.Model):
    _inherit = 'project.task.type'

    restrict_task_completion = fields.Boolean(
        string='Checklist Task Progress Restriction',
        help='If selected, tasks cannot go to the stage created until all checklist items are either completed or cancelled.'
    )
