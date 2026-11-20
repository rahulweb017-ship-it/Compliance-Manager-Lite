from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    compliance_expiring_soon_threshold = fields.Integer(
        string="Expiring Soon Threshold (days)",
        config_parameter="compliance_manager_lite.expiring_soon_threshold",
        default=30,
        help="A document counts as Expiring Soon once it is within this many days "
             "of its expiry date.",
    )

    @api.model
    def get_values(self):
        values = super().get_values()
        # Guard against a blank or zero parameter left behind by an older version.
        if not values.get("compliance_expiring_soon_threshold"):
            values["compliance_expiring_soon_threshold"] = 30
        return values

    def set_values(self):
        previous = self.env["compliance.record"]._get_expiring_threshold()
        super().set_values()
        # The threshold feeds a stored computed field, so a change has to reprice
        # existing records immediately rather than waiting for the nightly cron.
        if self.env["compliance.record"]._get_expiring_threshold() != previous:
            self.env["compliance.record"]._cron_refresh_status()

    def action_open_reminder_rules(self):
        return self.env["ir.actions.actions"]._for_xml_id(
            "compliance_manager_lite.action_compliance_reminder_rule_global"
        )
