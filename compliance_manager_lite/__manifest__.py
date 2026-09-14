{
    "name": "Compliance Manager Lite",
    "version": "19.0.1.1.1",
    "category": "Services/Compliance",
    "summary": "Document expiry tracking with automatic renewal reminders, dashboard and PDF/XLSX reports.",
    "description": """
Compliance Manager Lite
=======================

Document expiry tracking and automatic renewal reminders for Odoo.

Track licences, contracts, certifications, insurance policies, vehicle
documents and employee records in a single register. Every document gets an
automatic colour-coded status (Valid, Expiring Soon, Expired) and a countdown
to its expiry date.

Key features:

* Reminder schedules you define yourself, and a different schedule per category
* Full reminder history with recipient, delivery status and any error
* Configurable Expiring Soon threshold
* KPI dashboard with clickable cards, plus calendar and kanban views
* My Compliance view for each responsible user
* Multi-company support through record rules
* PDF report with summary totals, and XLSX export
* Native Odoo chatter and scheduled activities on every document

Free and open source under LGPL-3.
""",
    "author": "Softdeviser",
    "website": "https://softdeviser.com/",
    "support": "rahul@softdeviser.com",
    "license": "LGPL-3",
    "depends": ["base", "mail", "web", "hr"],
    "external_dependencies": {"python": ["xlsxwriter"]},
    "post_init_hook": "post_init_hook",
    "data": [
        "security/compliance_security.xml",
        "security/ir.model.access.csv",
        "data/mail_template_data.xml",
        "data/ir_cron_data.xml",
        "views/compliance_category_views.xml",
        "views/compliance_reminder_views.xml",
        "views/compliance_record_views.xml",
        "views/res_config_settings_views.xml",
        "views/compliance_dashboard_views.xml",
        "report/compliance_report.xml",
        "views/compliance_menus.xml",
    ],
    "demo": [
        "demo/demo.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "compliance_manager_lite/static/src/scss/dashboard.scss",
            "compliance_manager_lite/static/src/js/dashboard.js",
            "compliance_manager_lite/static/src/xml/dashboard.xml",
        ],
    },
    "images": [
        "static/description/banner.gif",
        "static/description/dashboard.png",
        "static/description/list.png",
        "static/description/calendar.png",
        "static/description/form.png",
    ],
    "installable": True,
    "application": True,
}
