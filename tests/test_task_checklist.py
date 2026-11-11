# Copyright (C) 2024-2025 Zehntech Technologies Inc. <odoo-support@zehntech.com>
# License OPL-1 (https://www.odoo.com/documentation/user/legal/licenses.html)
from odoo.tests.common import TransactionCase, tagged
from odoo.exceptions import AccessError, UserError, ValidationError


@tagged('post_install', '-at_install')
class TestTaskChecklist(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Category = cls.env['checklist.category']
        cls.Checklist = cls.env['task.checklist']
        cls.Item = cls.env['checklist.item']
        cls.ItemLine = cls.env['checklist.item.line']
        cls.Task = cls.env['project.task']
        cls.Project = cls.env['project.project']
        cls.Stage = cls.env['project.task.type']

        cls.group_restricted = cls.env['res.groups'].create({
            'name': 'PTC Test Restricted Group',
        })
        cls.category_open = cls.Category.create({'name': 'PTC Test Open Category'})
        cls.category_restricted = cls.Category.create({
            'name': 'PTC Test Restricted Category',
            'group_permission': cls.group_restricted.id,
        })

        cls.checklist_open = cls.Checklist.create({
            'name': 'PTC Test Open Checklist',
            'checklist_category': cls.category_open.id,
            'checklist_ids': [
                (0, 0, {'name': 'Item A'}),
                (0, 0, {'name': 'Item B'}),
            ],
        })
        cls.checklist_restricted = cls.Checklist.create({
            'name': 'PTC Test Restricted Checklist',
            'checklist_category': cls.category_restricted.id,
            'checklist_ids': [(0, 0, {'name': 'Restricted Item'})],
        })

        cls.project = cls.Project.create({'name': 'PTC Test Project'})

        cls.stage_open = cls.Stage.create({
            'name': 'PTC Test Stage Open',
            'restrict_task_completion': False,
        })
        cls.stage_restricted = cls.Stage.create({
            'name': 'PTC Test Stage Restricted',
            'restrict_task_completion': True,
        })

        cls.user_member = cls.env['res.users'].create({
            'name': 'PTC Test Member',
            'login': 'ptc_test_member',
            'email': 'ptc_test_member@example.com',
            'group_ids': [(6, 0, [
                cls.env.ref('base.group_user').id,
                cls.env.ref('project.group_project_user').id,
                cls.group_restricted.id,
            ])],
        })
        cls.user_outsider = cls.env['res.users'].create({
            'name': 'PTC Test Outsider',
            'login': 'ptc_test_outsider',
            'email': 'ptc_test_outsider@example.com',
            'group_ids': [(6, 0, [
                cls.env.ref('base.group_user').id,
                cls.env.ref('project.group_project_user').id,
            ])],
        })

    # -- Basic model creation ------------------------------------------------

    def test_checklist_creation_with_items(self):
        self.assertEqual(len(self.checklist_open.checklist_ids), 2)
        self.assertTrue(self.checklist_open.exists())

    def test_checklist_requires_at_least_one_item(self):
        with self.assertRaises(ValidationError):
            self.Checklist.create({
                'name': 'PTC Test Empty Checklist',
                'checklist_category': self.category_open.id,
                'checklist_ids': [],
            })

    def test_duplicate_checklist_name_in_category_blocked(self):
        with self.assertRaises(ValidationError):
            self.Checklist.create({
                'name': self.checklist_open.name,
                'checklist_category': self.category_open.id,
                'checklist_ids': [(0, 0, {'name': 'Another Item'})],
            })

    # -- State transitions ----------------------------------------------------

    def test_state_transition_cycle(self):
        line = self.ItemLine.create({
            'check_list_item_id': self.checklist_open.checklist_ids[0].id,
            'projects_id': self._make_task().id,
            'checklist_id': self.checklist_open.id,
            'state': 'todo',
        })
        line.approve_and_next()
        self.assertEqual(line.state, 'in_progress')
        line.mark_completed()
        self.assertEqual(line.state, 'done')
        line.mark_canceled()
        self.assertEqual(line.state, 'cancel')
        line.reset_stage()
        self.assertEqual(line.state, 'todo')

    def test_direct_write_state_blocked_for_non_permitted_user(self):
        task = self._make_task(user=self.user_member, checklist=self.checklist_restricted,
                                assignees=self.user_member + self.user_outsider)
        line = self.ItemLine.create({
            'check_list_item_id': self.checklist_restricted.checklist_ids[0].id,
            'projects_id': task.id,
            'checklist_id': self.checklist_restricted.id,
            'state': 'todo',
        })
        with self.assertRaises(UserError):
            line.with_user(self.user_outsider).write({'state': 'done'})

    def test_direct_write_state_allowed_for_permitted_member(self):
        task = self._make_task(user=self.user_member, checklist=self.checklist_restricted,
                                assignees=self.user_member)
        line = self.ItemLine.create({
            'check_list_item_id': self.checklist_restricted.checklist_ids[0].id,
            'projects_id': task.id,
            'checklist_id': self.checklist_restricted.id,
            'state': 'todo',
        })
        line.with_user(self.user_member).write({'state': 'done'})
        self.assertEqual(line.state, 'done')

    # -- Progress bar -----------------------------------------------------

    def test_progress_bar_computation(self):
        task = self._make_task(checklist=self.checklist_open)
        item_a, item_b = self.checklist_open.checklist_ids
        line_a = self.ItemLine.create({
            'check_list_item_id': item_a.id, 'projects_id': task.id,
            'checklist_id': self.checklist_open.id, 'state': 'todo',
        })
        self.ItemLine.create({
            'check_list_item_id': item_b.id, 'projects_id': task.id,
            'checklist_id': self.checklist_open.id, 'state': 'todo',
        })
        self.assertEqual(task.checklist_progress, 0.0)
        line_a.write({'state': 'done'})
        self.assertEqual(task.checklist_progress, 50.0)

    def test_progress_bar_zero_items_no_division_error(self):
        task = self._make_task()
        self.assertEqual(task.checklist_progress, 0.0)

    # -- Stage restriction --------------------------------------------------

    def test_stage_restriction_blocks_incomplete_checklist(self):
        task = self._make_task(checklist=self.checklist_open)
        item_a, item_b = self.checklist_open.checklist_ids
        self.ItemLine.create({
            'check_list_item_id': item_a.id, 'projects_id': task.id,
            'checklist_id': self.checklist_open.id, 'state': 'todo',
        })
        with self.assertRaises(ValidationError):
            task.write({'stage_id': self.stage_restricted.id})

    def test_stage_restriction_allows_completed_checklist(self):
        task = self._make_task(checklist=self.checklist_open)
        item_a, item_b = self.checklist_open.checklist_ids
        self.ItemLine.create({
            'check_list_item_id': item_a.id, 'projects_id': task.id,
            'checklist_id': self.checklist_open.id, 'state': 'done',
        })
        self.ItemLine.create({
            'check_list_item_id': item_b.id, 'projects_id': task.id,
            'checklist_id': self.checklist_open.id, 'state': 'cancel',
        })
        task.write({'stage_id': self.stage_restricted.id})
        self.assertEqual(task.stage_id, self.stage_restricted)

    # -- Category / group permission enforcement -----------------------------

    def test_create_blocks_restricted_checklist_listed_second(self):
        with self.assertRaises(AccessError):
            self.Task.with_user(self.user_outsider).create({
                'name': 'Outsider Mixed Checklist Task',
                'project_id': self.project.id,
                'checklist_id': [(6, 0, [self.checklist_open.id, self.checklist_restricted.id])],
            })

    def test_create_allows_unrestricted_checklist(self):
        task = self.Task.with_user(self.user_outsider).create({
            'name': 'Outsider Open Checklist Task',
            'project_id': self.project.id,
            'checklist_id': [(6, 0, [self.checklist_open.id])],
        })
        self.assertTrue(task.exists())

    def test_write_blocks_swapping_in_restricted_checklist(self):
        task = self.Task.with_user(self.user_outsider).create({
            'name': 'Outsider Task For Swap',
            'project_id': self.project.id,
            'checklist_id': [(6, 0, [self.checklist_open.id])],
        })
        with self.assertRaises(AccessError):
            task.with_user(self.user_outsider).write(
                {'checklist_id': [(6, 0, [self.checklist_restricted.id])]}
            )

    def test_write_allows_permitted_member_to_set_restricted_checklist(self):
        task = self.Task.with_user(self.user_member).create({
            'name': 'Member Task For Swap',
            'project_id': self.project.id,
            'checklist_id': [(6, 0, [self.checklist_open.id])],
        })
        task.with_user(self.user_member).write(
            {'checklist_id': [(6, 0, [self.checklist_restricted.id])]}
        )
        self.assertIn(self.checklist_restricted.id, task.checklist_id.ids)

    # -- helpers --------------------------------------------------------------

    def _make_task(self, user=None, checklist=None, assignees=None):
        vals = {'name': 'PTC Helper Task', 'project_id': self.project.id}
        if checklist:
            vals['checklist_id'] = [(6, 0, [checklist.id])]
        if assignees:
            vals['user_ids'] = [(6, 0, assignees.ids)]
        model = self.Task.with_user(user) if user else self.Task.sudo()
        return model.create(vals)
