# Copyright (C) 2024-2025 Zehntech Technologies Inc. <odoo-support@zehntech.com>
# License OPL-1 (https://www.odoo.com/documentation/user/legal/licenses.html)
from odoo import models, fields, api, _
import logging
from odoo.exceptions import AccessError
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError
from lxml import etree
import logging
_logger = logging.getLogger(__name__)


#Define the model for the checklist 
class TaskChecklist(models.Model):
    _name = 'task.checklist'
    _description = "Task Checklist"

    name = fields.Char(
        string='Name', 
        required=True,
        translate=True, export_string_translation=True,
        help="Enter a unique name for the checklist. This will help identify the checklist for the task or project."
    )
    description = fields.Char(
        string='Description',
        translate=True, export_string_translation=True,
        help="Provide a detailed description of the checklist. This could include the purpose or specific instructions for completing the checklist."
    )
    task_ids = fields.Many2one(
        'project.task', 
        string='Task', 
        help="Link the checklist to a specific task. This defines the task that the checklist will be applied to."
    )
    project_id = fields.Many2one(
        'project.project', 
        string='Project',
        help="Link the checklist to a specific project. This defines the project under which the checklist belongs."
    )
    checklist_ids = fields.One2many(
        'checklist.item', 
        'checklist_id', 
        string='Checklist Items',
        help="This field holds the individual items for the checklist. These are the tasks or steps that need to be completed within the checklist."
    )
    checklist_category = fields.Many2one(
        'checklist.category', 
        string="Checklist Category", 
        required=True,
        help="Select the category of the checklist (e.g., Bug Fixes, Feature Requests). This helps organize checklists into groups for better management."
    )

    @api.constrains('checklist_ids')
    def _check_one2many_required(self):
        for record in self:
            if not record.checklist_ids:
                raise ValidationError(_("You must add at least one item to the checklist."))
            
    @api.constrains('name', 'checklist_category')
    def _check_unique_checklist_name(self):
        for record in self:
            # Search for checklists with the same name (case-insensitive) in the same category, excluding the current record
            existing_checklists = self.env['task.checklist'].search([
                ('checklist_category', '=', record.checklist_category.id),
                ('name', 'ilike', record.name),  # Use 'ilike' for case-insensitive search
                ('id', '!=', record.id)  # Exclude the current record from the search
            ])
            
            if existing_checklists:
                raise ValidationError(_("A checklist with the same name already exists in this category."))

    

#Define model for the checklist items
class CheckListItem(models.Model):
    _name = 'checklist.item'
    _description = "Checklist Item"

    name = fields.Char(
        required=True,
        translate=True, export_string_translation=True,
        help="Enter the name of the checklist item. This should be a brief, descriptive title of the task or step in the checklist."
    )
    sequence = fields.Integer(
        default=1,
        help="Enter the sequence number for the checklist item. This will determine the order of items in the checklist. By default, the first item will have sequence 1."
    )
    description = fields.Char(
        translate=True, export_string_translation=True,
        help="Provide a detailed description of the checklist item. This can explain the task or provide additional instructions on how to complete the item."
    )
    checklist_id = fields.Many2one(
        'task.checklist',
        help="Select the checklist that this item belongs to. This links the checklist item to the overall checklist."
    )

    # Applying api constraint to check the uniqueness of the name
    @api.constrains('name', 'checklist_id')
    def _check_name_unique_within_checklist(self):
        for record in self:
            existing = self.search([
                ('id', '!=', record.id),
                ('name', '=ilike', record.name),
                ('checklist_id', '=', record.checklist_id.id)  # Ensures uniqueness within the same checklist
            ])
            if existing:
                raise ValidationError(_("The Checklist Item name must be unique."))


#Define model for the checklist items line
class CheckListItemLine(models.Model):
    _name = 'checklist.item.line'
    _description = "Checklist Item Line"

    check_list_item_id = fields.Many2one(
        "checklist.item",
        required=True,
        help="Select the checklist item for this line. This links the item to the checklist and helps track its completion status."
    )
    projects_id = fields.Many2one(
        'project.task',
        help="This field is automatically set to the task associated with the checklist item. It indicates which project task this checklist item belongs to."
    )
    description = fields.Char(
        help="Provide a brief description or additional details about this checklist item line, if necessary."
    )
    checklist_id = fields.Many2one(
        'task.checklist',
        help="Select the checklist to which this item line belongs. It links this item to a larger checklist, helping with organization."
    )
    state = fields.Selection(
        string="Status",
        selection=[
            ('todo', 'To Do'),
            ('in_progress', 'In Progress'),
            ('done', 'Done'),
            ('cancel', 'Cancelled'),
        ],
        default='todo',
        readonly=True,
        required=True,
        help="The current status of the checklist item. Choose the appropriate status based on the progress of the item: 'To Do', 'In Progress', 'Done', or 'Cancelled'."
    )

    @api.constrains('check_list_item_id', 'projects_id')
    def _check_unique_item_in_milestone(self):
        """ Ensure checklist items are unique within the same milestone. """
        for record in self:
            duplicate = self.search([
                ('projects_id', '=', record.projects_id.id),
                ('check_list_item_id', '=', record.check_list_item_id.id),
                ('id', '!=', record.id)
            ], limit=1)
            if duplicate:
                raise ValidationError(
                    _("The checklist item '%s' is already added to this checklist.") % record.check_list_item_id.name
                )



    #Method to change the status od checklist items to In progress
    def approve_and_next(self):
        self.check_user_permission()
        self.state = 'in_progress'

    #Method to change the status od checklist items to In progress
    def mark_completed(self):
        self.check_user_permission()
        self.state = 'done'

    #Method to change the status od checklist items to In progress
    def mark_canceled(self):
        self.check_user_permission()
        self.state = 'cancel'

    #Method to change the status od checklist items to In progress
    def reset_stage(self):
        self.check_user_permission()
        self.state = 'todo'

    def write(self, vals):
        if 'state' in vals:
            self.check_user_permission()
        return super().write(vals)

    #Method to check the user permission if the user has permission to change the status of checklist item
    def check_user_permission(self):
        """
        Checks if the user has permission to update the checklist item.
        Admin users have unrestricted access, while other users must be assignees of the task.
        """
        checklist_item = self.check_list_item_id

        checklist = checklist_item.checklist_id
        checklist_category = checklist.checklist_category

        if self.state:
            task = self.projects_id  # Assuming projects_id is the related task
            if task:
                # Allow if the user is an administrator
                if self.env.user.has_group('base.group_system'):
                    return

                # Otherwise, check if the user is an assignee
                user_groups = self.env.user.group_ids
                if not any(group.id in checklist_category.group_permission.ids for group in user_groups):
                    raise UserError(_(
                        "You do not have the necessary permissions to update the checklist item because you are not part of the required group."
                    ))

#Inherit the task model to add necessary fields for checklist
class ChecklistProgress(models.Model):
    _inherit = 'project.task'

    checklist_id = fields.Many2many(
        "task.checklist",
        help="Select the checklists to associate with this task. This links multiple checklists to a task, allowing you to track various aspects of the task's progress."
    )
    checklists = fields.One2many(
        "checklist.item.line", 
        "projects_id", 
        string="Checklist Items", 
        help="The checklist items that are part of this task. Each checklist item corresponds to a specific action or step in the task's completion."
    )
    checklist_progress = fields.Float(
        compute='_compute_checklist_progress', 
        string='Checklist Progress in %',
        help="Displays the percentage of checklist items completed for this task, providing a quick overview of progress."
    )
    has_checklist = fields.Boolean(
        string="Has Checklist", 
        compute="_compute_has_checklist", 
        store=True,
        help="Indicates whether the task has associated checklists. This helps in determining if the task requires checklist tracking."
    )
    checklist_category = fields.Many2one(
        'checklist.category', 
        string="Checklist Category",
        help="Categorize this checklist. The checklist category groups tasks by similar types or classifications, providing better organization and filtering.",
        domain="[('id', 'in', category_domain)]")
    
    category_domain = fields.Many2many('checklist.category',
        string="Allowed Categories",
        compute='_compute_category_domain',
        store=False)
    
    checklist_domain = fields.Char(compute='_compute_checklist_domain')

    @api.depends('checklist_category')
    def _compute_checklist_domain(self):
        for record in self:
            if record.checklist_category:
                record.checklist_domain = str([
                    ('checklist_category', '=', record.checklist_category.id),
                ])
            else:
                record.checklist_domain = []
    
    def copy(self, default=None):
        if default is None:
            default = {}
        
        # Duplicate the checklist relationships
        default['checklist_id'] = [(6, 0, self.checklist_id.ids)]  # Keep the same checklist IDs
        
        # Create new checklist items based on the selected checklists
        checklist_items = []
        for checklist in self.checklist_id:
            checklist_items.extend([
                (0, 0, {
                    'check_list_item_id': item.id,
                    'description': item.description,
                    'state': 'todo',
                    'checklist_id': checklist.id,
                }) for item in checklist.checklist_ids
            ])

        # Assign duplicated checklist items to the `checklists` field
        default['checklists'] = checklist_items

        # Call the super copy method with updated defaults
        return super(ChecklistProgress, self).copy(default)

   
    @api.depends('user_ids')
    def _compute_category_domain(self):
        # Fetch every category once for the whole recordset instead of
        # searching per record (was up to 3 search() calls per record).
        all_categories = self.env['checklist.category'].search([])
        no_group_permission_categories = all_categories.filtered(lambda cat: not cat.group_permission)
        group_scoped_categories = all_categories - no_group_permission_categories

        for record in self:
            if record.user_ids:
                # Get all groups of the selected users
                user_groups = set(record.user_ids.mapped('group_ids').ids)
                # Filter the pre-fetched group-scoped categories in Python
                categories = group_scoped_categories.filtered(
                    lambda cat: cat.group_permission.id in user_groups
                )
                # Combine both filtered categories and categories with no group permission
                record.category_domain = categories | no_group_permission_categories
            else:
                # If no users selected, no restriction on categories
                record.category_domain = all_categories
    
    #Helper to normalize a checklist_id M2M command (or plain id list) into a flat list of ids
    def _extract_checklist_ids(self, checklist_command):
        if not checklist_command:
            return []
        if isinstance(checklist_command, list) and checklist_command[0][0] == 6:
            return checklist_command[0][2]
        return checklist_command  # Fallback in case of unexpected format

    #Helper to validate every checklist id against its category's group permission (used by create() and write())
    def _check_checklist_category_permission(self, checklist_ids):
        if not checklist_ids:
            return

        checklists = self.env['task.checklist'].browse(checklist_ids)
        if len(checklists.exists()) != len(set(checklist_ids)):
            raise ValueError(_("Invalid checklist_id: %(ids)s") % {'ids': checklist_ids})

        user_groups = self.env.user.group_ids
        for checklist in checklists:
            category = checklist.checklist_category
            if category and category.group_permission:
                if not any(group in user_groups for group in category.group_permission):
                    raise AccessError(_(
                        "You do not have the necessary permissions to create this task "
                        "based on the checklist category's group permissions."
                    ))

    @api.model_create_multi
    def create(self, vals_list):
        is_admin = self.env.user.has_group('base.group_system')

        for vals in vals_list:
            # Check if the stage_id is provided
            if 'stage_id' in vals:
                stage = self.env['project.task.type'].browse(vals['stage_id'])

                # Check if the stage has the restriction to prevent task creation
                if stage.restrict_task_completion:
                    raise UserError(_("You cannot create a task in the selected stage as it is restricted."))

            if not is_admin:
                checklist_ids = self._extract_checklist_ids(vals.get('checklist_id'))
                self._check_checklist_category_permission(checklist_ids)

        # Proceed with the normal task creation process
        return super(ChecklistProgress, self).create(vals_list)


    # Override the Project.task model's write method so that the task will not go in the restricted stage untill all the checklist items 
    # are done

    def write(self, vals):

                # 2. Check if the stage is being changed to a restricted stage
        if 'stage_id' in vals:
            stage = self.env['project.task.type'].browse(vals['stage_id'])
            if stage.restrict_task_completion:  # Assuming this field is a Boolean on project.task.type
                for task in self:
                    checklist_items = task.checklists  # Assuming task has a 'checklists' One2many or Many2one field
                    # Filter checklist items that are not 'done' or 'cancel'
                    incomplete_checklist = checklist_items.filtered(lambda item: item.state not in ['done', 'cancel'])
                    if incomplete_checklist:
                        raise ValidationError(_(
                            "You cannot move the task to the stage '%(stage)s' until all checklist items are either completed or canceled."
                        ) % {'stage': stage.name})


        if self.env.user.has_group('base.group_system'):
            return super(ChecklistProgress, self).write(vals)

        if 'checklist_id' in vals:
            incoming_checklist_ids = self._extract_checklist_ids(vals.get('checklist_id'))
            self._check_checklist_category_permission(incoming_checklist_ids)

        for task in self:

            # Check if the user has access based on the checklist category group permissions
            category = task.checklist_id.checklist_category
            if category and category.group_permission:
                # Check if the current user is part of the allowed groups
                user_groups = self.env.user.group_ids
                if not any(group in user_groups for group in category.group_permission):
                    raise AccessError(_(
                        "You do not have the necessary permissions to Update this task "
                        "based on the checklist category's group permissions."
                    ))


        # Proceed with the update if all checks pass
        return super(ChecklistProgress, self).write(vals)

    #Onchange method on assignees field as soon as user selects assignee autopopulate the category that assignee have permission
    @api.onchange('user_ids')
    def _onchange_user_ids(self):
        """
        Auto-populates checklist_category based on selected users.
        Ensures users share groups with current user.
        """
        current_user_groups = self.env.user.group_ids.ids

        # Validate selected users belong to same group as current user
        for user in self.user_ids:
            if not set(user.group_ids.ids).intersection(current_user_groups):
                raise ValidationError(_(
                    "You cannot assign this task/checklist to %(user)s because they are not in the same group as you."
                ) % {'user': user.name})

        if self.user_ids:

            # Get groups of selected users
            selected_user_group_ids = self.user_ids.mapped('group_ids').ids

            # Search categories by matching group IDs (correct for Odoo 19)
            categories = self.env['checklist.category'].search([
                ('group_permission', 'in', selected_user_group_ids)
            ])

            # Also include categories without group_permission set
            categories |= self.env['checklist.category'].search([
                ('group_permission', '=', False)
            ])

            if len(categories) == 1:
                self.checklist_category = categories[0]

            elif len(categories) > 1:
                self.checklist_category = False
                return
            else:
                # If no categories found
                self.checklist_category = False
        else:
            self.checklist_category = False



    # Api oncnage method to check if the category is selected before selecting the checklist      
    @api.onchange('checklist_id')
    def _onchange_checklist_id(self):
        # Check if checklist_category is selected before allowing checklist_id selection
        if self.checklist_id and not self.checklist_category:
            raise UserError(_("Please select a category first before selecting a checklist."))
        if self.checklist_id:
            # Get the category of the first checklist
            category = self.checklist_id[0].checklist_category
            # If all selected checklists share the same category, set it
            if all(checklist.checklist_category == category for checklist in self.checklist_id):
                self.checklist_category = category
            else:
                # Clear the category if multiple checklists from different categories are selected
                self.checklist_category = False
        else:
            # No checklist selected, clear the category
            self.checklist_category = False

    #Method to Set domains for `checklist_id` and `user_ids` fields based on `checklist_category`.Validate that the selected users have access to the category. 
    @api.onchange('checklist_category')
    def _onchange_checklist_category(self):
        """
        Set domains for `checklist_id` and `user_ids` fields based on `checklist_category`.
        Validate that the selected users have access to the category, except for admin users.
        """

        if self.checklist_category:
            # Apply domain for checklist_id

            if self.checklist_id:
                # Collect checklists that do not belong to the selected category
                invalid_checklists = self.checklist_id.filtered(
                    lambda checklist: checklist.checklist_category.id != self.checklist_category.id
                )

                if invalid_checklists:
                    # Create a comma-separated list of checklist names
                    checklist_names = ", ".join(invalid_checklists.mapped('name'))
                    category_name = invalid_checklists[0].checklist_category.name  # Assuming all have the same category
                    
                    # Generate a single error message
                    error_message = _(
                        "The selected checklist(s) '%(checklist_names)s' belong(s) to the category '%(category_name)s', "
                        "which does not match the selected category '%(selected_category)s'."
                    ) % {
                        'checklist_names': checklist_names,
                        'category_name': category_name,
                        'selected_category': self.checklist_category.name
                    }

                    raise UserError(error_message)  # Raise error only once
                
            # Domain for user_ids based on group_permission
            if self.checklist_category.group_permission:
                group_ids = self.checklist_category.group_permission.ids
                group_users = self.env['res.users'].search([('group_ids', 'in', group_ids)])

                # Validation: Check if selected users have access, skipping admins
                if self.user_ids:

                    # Check if any user is an admin, and skip validation for them
                    admin_user_ids = self.env.ref('base.group_system').user_ids.ids
                    non_admin_users = [uid for uid in self.user_ids.ids if uid not in admin_user_ids]

                    # Compare non-admin user IDs with group_users
                    invalid_user_ids = [user_id for user_id in non_admin_users if user_id not in group_users.ids]
                    
                    if invalid_user_ids:
                        # Get invalid users' names
                        invalid_users = self.env['res.users'].browse(invalid_user_ids)
                        user_names = ', '.join(invalid_users.mapped('name')) if invalid_users else "None"
                        raise UserError(_(
                                "The following users do not have access to the selected category: %(user_names)s"
                            ) % {'user_names': user_names})

    #Update the has_checklist field to true when user selects a field so that checklist page will be visible   
    @api.depends('checklist_id')
    def _compute_has_checklist(self):
        for record in self:
            record.has_checklist = bool(record.checklist_id)

    #Onchange method to add the checklist items in the page according to the checklist selected       
    @api.onchange('checklist_id')
    def _onchange_project_id(self):
        # Clear existing checklist items
        self.checklists = False
        checklist_items = []

        # Loop over each selected checklist in checklist_id
        for checklist in self.checklist_id:
            # Add items from each selected checklist to the checklist_items list
            checklist_items.extend([
                (0, 0, {
                    'check_list_item_id': item.id,
                    'description': item.description,
                    'state': 'todo',
                    'checklist_id': checklist.id,
                }) for item in checklist.checklist_ids
            ])

        # Assign the aggregated checklist items to the checklists field
        self.checklists = checklist_items

    #Progress bar computation according to done items
    @api.depends('checklists', 'checklists.state')
    def _compute_checklist_progress(self):
        for rec in self:
            total_completed = 0
            total_checklists = 0

            # Loop through the checklists and count the valid (non-cancelled) ones
            for activity in rec.checklists:
                if activity.state != 'cancel':  # Exclude cancelled items
                    total_checklists += 1
                    if activity.state == 'done':  # Count completed activities
                        total_completed += 1

            if total_checklists == 0:
                rec.checklist_progress = 0.0
            else:
                # Compute progress as a percentage of completed activities
                rec.checklist_progress = (total_completed / total_checklists) * 100





