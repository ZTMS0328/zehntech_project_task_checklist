# Copyright (C) 2024-2025 Zehntech Technologies Inc. <odoo-support@zehntech.com>
# License OPL-1 (https://www.odoo.com/documentation/user/legal/licenses.html)
from odoo.tests.common import TransactionCase, tagged
from odoo.exceptions import AccessError, ValidationError


@tagged('post_install', '-at_install')
class TestProjectChecklist(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Category = cls.env['checklist.category']
        cls.Checklist = cls.env['project.checklist']
        cls.ItemLine = cls.env['project.checklist.item.line']
        cls.Project = cls.env['project.project']

        cls.group_restricted = cls.env['res.groups'].create({
            'name': 'PTC Test Project Restricted Group',
        })
        cls.category_open = cls.Category.create({'name': 'PTC Test Project Open Category'})
        cls.category_restricted = cls.Category.create({
            'name': 'PTC Test Project Restricted Category',
            'group_permission': cls.group_restricted.id,
        })

        cls.checklist_open = cls.Checklist.create({
            'name': 'PTC Test Project Open Checklist',
            'checklist_category': cls.category_open.id,
            'checklist_ids': [
                (0, 0, {'name': 'Item A'}),
                (0, 0, {'name': 'Item B'}),
            ],
        })
        cls.checklist_restricted = cls.Checklist.create({
            'name': 'PTC Test Project Restricted Checklist',
            'checklist_category': cls.category_restricted.id,
            'checklist_ids': [(0, 0, {'name': 'Restricted Item'})],
        })

        # Creating a project.project record requires project.group_project_manager
        # in stock Odoo ACLs (regular group_project_user can only work within
        # existing projects) — both test users need it so the "create a project"
        # scenarios reflect a realistic caller; the checklist category's own
        # group_permission (group_restricted) is the axis actually under test.
        cls.user_member = cls.env['res.users'].create({
            'name': 'PTC Test Project Member',
            'login': 'ptc_test_project_member',
            'email': 'ptc_test_project_member@example.com',
            'group_ids': [(6, 0, [
                cls.env.ref('base.group_user').id,
                cls.env.ref('project.group_project_manager').id,
                cls.group_restricted.id,
            ])],
        })
        cls.user_outsider = cls.env['res.users'].create({
            'name': 'PTC Test Project Outsider',
            'login': 'ptc_test_project_outsider',
            'email': 'ptc_test_project_outsider@example.com',
            'group_ids': [(6, 0, [
                cls.env.ref('base.group_user').id,
                cls.env.ref('project.group_project_manager').id,
            ])],
        })

    # -- Basic model creation (mirrors task side) ------------------------------

    def test_checklist_creation_with_items(self):
        self.assertEqual(len(self.checklist_open.checklist_ids), 2)

    def test_checklist_requires_at_least_one_item(self):
        with self.assertRaises(ValidationError):
            self.Checklist.create({
                'name': 'PTC Test Project Empty Checklist',
                'checklist_category': self.category_open.id,
                'checklist_ids': [],
            })

    def test_project_id_field_points_at_project_project(self):
        field = self.Checklist._fields['project_id']
        self.assertEqual(field.comodel_name, 'project.project')

    # -- Progress bar -----------------------------------------------------

    def test_progress_bar_computation(self):
        project = self.Project.sudo().create({'name': 'PTC Test Progress Project'})
        item_a, item_b = self.checklist_open.checklist_ids
        line_a = self.ItemLine.create({
            'check_list_item_id': item_a.id, 'projects_id': project.id,
            'checklist_id': self.checklist_open.id, 'state': 'todo',
        })
        self.ItemLine.create({
            'check_list_item_id': item_b.id, 'projects_id': project.id,
            'checklist_id': self.checklist_open.id, 'state': 'todo',
        })
        self.assertEqual(project.checklist_progress, 0.0)
        line_a.write({'state': 'done'})
        self.assertEqual(project.checklist_progress, 50.0)

    # -- Category / group permission enforcement -----------------------------

    def test_create_blocks_restricted_checklist_listed_second(self):
        with self.assertRaises(AccessError):
            self.Project.with_user(self.user_outsider).create({
                'name': 'Outsider Mixed Checklist Project',
                'checklist_id': [(6, 0, [self.checklist_open.id, self.checklist_restricted.id])],
            })

    def test_create_allows_unrestricted_checklist(self):
        project = self.Project.with_user(self.user_outsider).create({
            'name': 'Outsider Open Checklist Project',
            'checklist_id': [(6, 0, [self.checklist_open.id])],
        })
        self.assertTrue(project.exists())

    def test_write_blocks_swapping_in_restricted_checklist(self):
        project = self.Project.with_user(self.user_outsider).create({
            'name': 'Outsider Project For Swap',
            'checklist_id': [(6, 0, [self.checklist_open.id])],
        })
        with self.assertRaises(AccessError):
            project.with_user(self.user_outsider).write(
                {'checklist_id': [(6, 0, [self.checklist_restricted.id])]}
            )

    def test_write_allows_permitted_member_to_set_restricted_checklist(self):
        project = self.Project.with_user(self.user_member).create({
            'name': 'Member Project For Swap',
            'checklist_id': [(6, 0, [self.checklist_open.id])],
        })
        project.with_user(self.user_member).write(
            {'checklist_id': [(6, 0, [self.checklist_restricted.id])]}
        )
        self.assertIn(self.checklist_restricted.id, project.checklist_id.ids)
