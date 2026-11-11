{
    'name': "Checklist for Projects and Tasks",
    'version': "20.0.1.1.0",
    'description': """The Checklist for Projects and Tasks for Odoo 20 streamlines project and task management by allowing users to attach multiple customizable checklists to tasks and projects. Key features include the ability to mark checklist items as completed, canceled, in progress, or reset as needed. A dynamic progress bar visually tracks completion, enhancing workflow efficiency. The app provides an intuitive interface for easy checklist management and supports improved organization and timely task completion, making it a valuable tool for boosting productivity and accountability in project workflows.""",
    "category": "Project",
    'summary': "Streamline project and task management with the Odoo Checklist App. Attach multiple customizable checklists, track progress with a dynamic bar, and improve efficiency with features like marking items as completed, canceled, or in progress.",
    "author": "Zehntech Technologies Inc.",
    "company": "Zehntech Technologies Inc.",
    "maintainer": "Zehntech Technologies Inc.",
    "contributor": "Zehntech Technologies Inc.",
    "website": "https://www.zehntech.com/",
    "support": "odoo-support@zehntech.com",
    "live_test_url": "https://zehntechodoo.com/app_name=zehntech_project_task_checklist/app_version=20.0",
    'depends': ['project'],
    'data': [
        "views/task_menu_action_views.xml",
        "views/checklist_add_task.xml",
        "views/project_menu_action_views.xml",
        "views/checklist_add_project.xml",
        "views/task_stage_restriction.xml",
        "views/checklist_category_views.xml",
        'security/ir.access.csv',
    ],
    'demo': [
        "data/checklist_demo_data.xml"
    ],
    'i18n': [
        'i18n/es.po',
        'i18n/fr.po',
        'i18n/de.po',
        'i18n/ja_JP.po'
    ], 
    'assets': {
        'web.assets_backend': [
            'zehntech_project_task_checklist/static/src/css/style.css'    
        ]
    },
    'images': ['static/description/banner.gif'],
    'license': 'OPL-1',
    'installable': True,
    'application': True,
    'auto_install': False,
    "price": 15.00,
    "currency": "USD",
}