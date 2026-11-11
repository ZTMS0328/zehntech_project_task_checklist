================================================================
Checklist for Projects and Tasks
================================================================

The Checklist for Projects and Tasks for Odoo 20 streamlines project and task management by allowing users to attach multiple customizable checklists to tasks and projects. Key features include the ability to mark checklist items as completed, canceled, in progress, or reset as needed. A dynamic progress bar visually tracks completion, enhancing workflow efficiency. The app provides an intuitive interface for easy checklist management and supports improved organization and timely task completion, making it a valuable tool for boosting productivity and accountability in project workflows.

**Table of contents**
 
.. contents::
   :local:
 
**Key Features**
================================================================

- **Flexible Checklist Management**: User can create and manage multiple checklists and associate them with any project or task. 
- **Multiple Checklist Selection**: Tasks and projects can have more than one checklist attached, allowing for granular tracking and organization of subtasks or steps within each project or task and it also includes the pre-installed sample checklist users can select. 
- **Checklist Item Status Management**: Users can easily update the status( Complete, Cancel, InProgress and Reset) of each checklist item to reflect their progress.
- **Progress Tracking**: Users can easily track the progress of the checklist through the progress bar added in the form view, tree view and kanban view.
- **Category Wise Checklist**: Users can create checklist categories and assign groups to the checklist categories.
- **Security Rights For Checklist Catgories **: Only the groups that have authority to access the checklist category will only access the checklist categories and assign that particular checklists to task and project.

**Summary**
================================================================

Streamline project and task management with the Odoo Checklist App. Attach multiple customizable checklists, track progress with a dynamic bar, and improve efficiency with features like marking items as completed, canceled, or in progress.

**Installation**
================================================================

1. Download the module from the Odoo App Store or clone the repository.
2. Place the module in your Odoo addons directory.
3. Update your Odoo instance to include the new module.
4. Install the module through the Odoo interface.

**How to use this module:**
================================================================

1. Navigate to the Checklist for Projects and Tasks in your Odoo dashboard.
2. **Create Project or Task Checklist**: Go to Project section then in Configuration menu new submenu's will be visible, Task Checklist and Project Checklist, click on new button to create a new checklist and fill the details.
3. **Select checklists**: In the task or Project form a new field will be visible named Checklist, select all the checklists you want to include there are sample checklists available you can use them also.
4. **Update the status**: A new page Checklist will be available, here all the checklist items will be visible and buttons to update the status of the checklist items.
5. **Manage checklist items**: Apart from the checklist items available you can add more checklist items and you can delete the items you dont need.
6. **Progress tracking**: You can also see the progress of checklist from tree view, form view and kanban view by progressbar

Change logs
================================================================

[1.1.0]

* ``Security`` [27-10-2026]- Checklist access restricted to project users; item-line state changes and checklist assignment validated server-side
* ``Fixed`` [27-10-2026]- Crashes on task/project creation and permission check, wrong project link on project checklists, demo data loading on production installs
* ``Improved`` [27-10-2026]- Faster checklist category lookup, translatable messages, automated test suite added

[1.0.0]

* ``Added`` [18-11-2025]- Checklist for Projects and Tasks

Support
================================================================
 
`Zehntech Technologies <https://www.zehntech.com/erp-crm/odoo-services/>`_
