{
    "name": "Compliance Manager Lite",
    "version": "19.0.1.0.3",
    "category": "Services/Compliance",
    "summary": "Track compliance documents, expiry dates and automatic reminders.",
    "description": """
Compliance Manager Lite
========================
Track compliance records such as employee documents, vehicle insurance,
contracts, licenses and certifications. Get automatic expiry status,
scheduled email reminders, a KPI dashboard, calendar view and PDF/XLSX reports.
""",
    "author": "Softdeviser",
    "website": "https://softdeviser.com/",
    "support": "rahul@softdeviser.com",
    "license": "LGPL-3",
    "depends": ["base", "mail", "web"],
    "data": [
        "security/compliance_security.xml",
        "security/ir.model.access.csv",
        "data/mail_template_data.xml",
        "data/ir_cron_data.xml",
        "views/compliance_category_views.xml",
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
