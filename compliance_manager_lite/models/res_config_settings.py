from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    compliance_reminder_days_1 = fields.Integer(
        string="First Reminder (days before expiry)",
        config_parameter="compliance_manager_lite.reminder_days_1",
        default=30,
    )
    compliance_reminder_days_2 = fields.Integer(
        string="Second Reminder (days before expiry)",
        config_parameter="compliance_manager_lite.reminder_days_2",
        default=15,
    )
    compliance_reminder_days_3 = fields.Integer(
        string="Third Reminder (days before expiry)",
        config_parameter="compliance_manager_lite.reminder_days_3",
        default=7,
    )
    compliance_reminder_days_4 = fields.Integer(
        string="Final Reminder (days before expiry)",
        config_parameter="compliance_manager_lite.reminder_days_4",
        default=1,
    )
