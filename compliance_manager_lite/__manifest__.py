{
    "name": "Compliance Manager Lite - Document Expiry Tracking & Renewal Reminders",
    "version": "20.0.1.1.2",
    "category": "Services/Compliance",
    "summary": "Track expiry dates of licenses, certificates, contracts, insurance and employee documents. Automatic email renewal reminders, dashboard, PDF/Excel reports.",
    "description": """
Compliance Manager Lite
=======================

Document expiry tracking and automatic renewal reminders for Odoo 17, 18, 19
and 20 (Community and Enterprise).

Keep every license (licence), permit, certificate, contract, insurance policy,
vehicle document and employee document in one register. Each document gets an
automatic expiration status (Valid, Expiring Soon, Expired) and a countdown to
its expiry date, and the responsible person receives an email renewal reminder
before it lapses.

Typical uses:

* Employee document expiry: passports, visas, work permits, driving licenses,
  medical and training certificates
* Certificate expiry tracking: ISO 9001 / ISO 14001, calibration, inspection
  and safety certificates
* Contract renewal reminders: vendor contracts, leases, subscriptions, NDAs
* Fleet and vehicle documents: insurance, registration, road tax, emissions
* Business licenses and permits

Key features:

* Reminder schedules you define yourself (default 90, 60, 30, 15, 7 and 1 day
  before expiry), with a different schedule per category
* Full reminder history with recipient, delivery status and any error
* Configurable Expiring Soon threshold
* KPI dashboard with clickable cards, plus list, kanban and calendar views
* My Compliance view for each responsible user
* Multi-company support through record rules
* PDF report with summary totals, and Excel (XLSX) export
* Native Odoo chatter, attachments and scheduled activities on every document

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
        "security/ir.access.csv",
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
