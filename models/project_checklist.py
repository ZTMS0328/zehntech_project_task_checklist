# Copyright (C) 2024-2025 Zehntech Technologies Inc. <odoo-support@zehntech.com>
# License OPL-1 (https://www.odoo.com/documentation/user/legal/licenses.html)
from odoo import models, fields, api, _
import logging
from odoo.exceptions import AccessError
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError

#Define the model for the checklist 
class ProjectChecklist(models.Model):
    _name = 'project.checklist'
    _description = "Project Checklist"

    name = fields.Char(
        string='Name',
        required=True,
        translate=True, export_string_translation=True,
        help='Enter the name of the checklist. This will be used to identify the checklist in the system.'
    )
    description = fields.Char(
        string='Description',
        translate=True, export_string_translation=True,
        help='Provide a brief description of the checklist, explaining its purpose or usage.'
    )
    task_ids = fields.Many2one(
        'project.task', 
        string='Task',
        help='Select the task associated with this checklist. The checklist will be linked to this specific task.'
    )
    project_id = fields.Many2one(
        'project.project',
        string='Project',
        help='Select the project associated with this checklist. The checklist will be linked to this project.'
    )
    checklist_ids = fields.One2many(
        'project.checklist.item', 
        'checklist_id', 
        string='Checklist Items',
        help='These are the items that belong to this checklist. You can associate multiple items with a checklist.'
    )
    checklist_category = fields.Many2one(
        'checklist.category', 
        string='Checklist Category',
        required=True,
        help='Choose a category for the checklist. This will help to organize checklists and differentiate them.'
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
            existing_checklists = self.env['project.checklist'].search([
                ('checklist_category', '=', record.checklist_category.id),
                ('name', 'ilike', record.name),  # Use 'ilike' for case-insensitive search
                ('id', '!=', record.id)  # Exclude the current record from the search
            ])
            
            if existing_checklists:
                raise ValidationError(_("A checklist with the same name already exists in this category."))
    

#Define model for the checklist items
class ProjectCheckListItem(models.Model):
    _name = 'project.checklist.item'
    _description = "Project Checklist Item"

    name = fields.Char(
        required=True,
        translate=True, export_string_translation=True,
        help="Enter the name of the checklist item. This will be the label or title of the item."
    )
    sequence = fields.Integer(
        default=1,
        help="Set the order in which the checklist item should appear. The lower the number, the higher the priority."
    )
    description = fields.Char(
        translate=True, export_string_translation=True,
        help="Provide a detailed description of the checklist item. This could include instructions or more details about the task."
    )
    checklist_id = fields.Many2one(
        'project.checklist',
        help="Select the checklist to which this item belongs. This links the item to a specific checklist."
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
class ProjectCheckListItemLine(models.Model):
    _name = 'project.checklist.item.line'
    _description = "Project Checklist Item Line"

    check_list_item_id = fields.Many2one(
        "project.checklist.item", 
        required=True,
        help="Select the checklist item this line represents. It links to a specific item in the checklist."
    )
    projects_id = fields.Many2one(
        'project.project',
        help="Link the checklist item line to a specific project. This helps to identify which project the checklist belongs to."
    )
    description = fields.Char(
        help="Provide a description or additional details for the checklist item. This could be instructions or a more detailed explanation."
    )
    checklist_id = fields.Many2one(
        'project.checklist',
        help="Link this line to a specific checklist. This helps to associate the checklist item with a particular checklist."
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
        help="Indicates the status of the checklist item. You can set the item as To Do, In Progress, Done, or Cancelled."
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


    def approve_and_next(self):
        self.check_user_permission()
        self.state = 'in_progress'

    def mark_completed(self):
        self.check_user_permission()
        self.state = 'done'

    def mark_canceled(self):
        self.check_user_permission()
        self.state = 'cancel'

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

class ProjectChecklistProgress(models.Model):
    _inherit = 'project.project'

    checklist_id = fields.Many2many(
        "project.checklist",
        help="Select one or more checklists for the task. These checklists contain items that need to be completed during the task."
    )
    checklists = fields.One2many(
        "project.checklist.item.line", 
        "projects_id", 
        string="Checklist Items", 
        help="This field contains the list of items associated with the selected checklists. These items track the progress of the checklist."
    )
    checklist_progress = fields.Float(
        compute='_compute_checklist_progress', 
        string='Checklist Progress in %',
        help="This field shows the progress percentage of the checklist items in the task. It is computed based on the completion status of checklist items."
    )
    has_checklist = fields.Boolean(
        string="Has Checklist", 
        compute="_compute_has_checklist", 
        store=True,
        help="Indicates whether the task has any associated checklist. This helps to track tasks with checklists."
    )
    checklist_category = fields.Many2one('checklist.category', 
                                        help="Assign a category to the checklist. This helps to organize the checklists into relevant categories (e.g., 'Bug Fixes', 'Feature Requests').",
                                         string='Checklist Category',
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
        return super(ProjectChecklistProgress, self).copy(default)

   
    @api.depends('user_id')
    def _compute_category_domain(self):
        # Fetch every category once for the whole recordset instead of
        # searching per record (was up to 3 search() calls per record).
        all_categories = self.env['checklist.category'].search([])
        no_group_permission_categories = all_categories.filtered(lambda cat: not cat.group_permission)
        group_scoped_categories = all_categories - no_group_permission_categories

        for record in self:
            if record.user_id:
                # Get all groups of the selected users
                user_groups = set(record.user_id.mapped('group_ids').ids)
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

        checklists = self.env['project.checklist'].browse(checklist_ids)
        if len(checklists.exists()) != len(set(checklist_ids)):
            raise ValueError(_("Invalid checklist_id: %(ids)s") % {'ids': checklist_ids})

        user_groups = self.env.user.group_ids
        for checklist in checklists:
            category = checklist.checklist_category
            if category and category.group_permission:
                if not any(group in user_groups for group in category.group_permission):
                    raise AccessError(_(
                        "You do not have the necessary permissions to create this Project "
                        "based on the checklist category's group permissions."
                    ))

    @api.model_create_multi
    def create(self, vals_list):
        is_admin = self.env.user.has_group('base.group_system')

        if not is_admin:
            for vals in vals_list:
                checklist_ids = self._extract_checklist_ids(vals.get('checklist_id'))
                self._check_checklist_category_permission(checklist_ids)

        # Proceed with the normal task creation process
        return super(ProjectChecklistProgress, self).create(vals_list)
    
       # Override the Project.task model's write method so that the task will not go in the restricted stage untill all the checklist items 
    # are done

    def write(self, vals):
        

        if self.env.user.has_group('base.group_system'):
            return super(ProjectChecklistProgress, self).write(vals)

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
                        "You do not have the necessary permissions to Update this Project "
                        "based on the checklist category's group permissions."
                    ))

        # Proceed with the update if all checks pass
        return super(ProjectChecklistProgress, self).write(vals)
    
    #Onchange method on assignees field as soon as user selects assignee autopopulate the category that assignee have permission
    @api.onchange('user_id')
    def _onchange_user_id(self):
        """
        Auto-populates the category_id field based on the selected user_ids.
        This method will also check if the selected users belong to the same group as the logged-in user.
        """
        current_user_groups = self.env.user.group_ids.ids

        # Check if any of the selected users belong to a different group
        for user in self.user_id:
            
            if not set(user.group_ids.ids).intersection(set(current_user_groups)):
                
                raise ValidationError(_(
                        "You cannot assign this Project/checklist to %(user)s because they are not in the same group as you."
                    ) % {'user': user.name})

        if self.user_id:
            # --- CHANGED: compute group ids of selected users, then search categories by group id ---
            selected_user_group_ids = self.user_id.mapped('group_ids').ids
            # if no groups were found for selected users, search should include categories with no group_permission too
            if selected_user_group_ids:
                categories = self.env['checklist.category'].search([
                    ('group_permission', 'in', selected_user_group_ids)
                ])
            else:
                categories = self.env['checklist.category'].browse()  # empty recordset

            # Include categories that don't have any 'group_permission'
            no_group_permission_categories = self.env['checklist.category'].search([
                ('group_permission', '=', False)
            ])
            all_allowed_categories = categories | no_group_permission_categories

            if len(all_allowed_categories) == 1:
                self.checklist_category = all_allowed_categories[0]
            elif len(all_allowed_categories) > 1:
                self.checklist_category = False
                return
            else:
                # If no categories are found, clear the category
                self.checklist_category = False
        else:
            # Clear the category if no users are selected
            self.checklist_category = False


    #       
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


    #Method to Set domains for `checklist_id` and `user_id` fields based on `checklist_category`.Validate that the selected users have access to the category. 
    @api.onchange('checklist_category')
    def _onchange_checklist_category(self):
        """
        Set domains for `checklist_id` and `user_id` fields based on `checklist_category`.
        Validate that the selected users have access to the category, except for admin users.
        """
        domain = {}

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
            
            # Domain for user_id based on group_permission
            if self.checklist_category.group_permission:
                group_ids = self.checklist_category.group_permission.ids
                group_users = self.env['res.users'].search([('group_ids', 'in', group_ids)])
                domain['user_id'] = [('id', 'in', group_users.ids)]


                # Validation: Check if selected users have access, skipping admins
                if self.user_id:

                    # Check if any user is an admin, and skip validation for them
                    admin_user_ids = self.env.ref('base.group_system').user_ids.ids
                    non_admin_users = [uid for uid in self.user_id.ids if uid not in admin_user_ids]


                    # Compare non-admin user IDs with group_users
                    invalid_user_ids = [user_id for user_id in non_admin_users if user_id not in group_users.ids]
                    
                    if invalid_user_ids:
                        # Get invalid users' names
                        invalid_users = self.env['res.users'].browse(invalid_user_ids)
                        user_names = ', '.join(invalid_users.mapped('name')) if invalid_users else "None"
                        raise UserError(_(
                                "The following users do not have access to the selected category: %(users)s"
                            ) % {'users': user_names})
            else:
                domain['user_id'] = []  # Clear domain if no group permission
        else:
            # Clear domains if no checklist_category is selected
            domain['checklist_id'] = []
            domain['user_id'] = []

        # Return the combined domain
        return {'domain': domain}

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






