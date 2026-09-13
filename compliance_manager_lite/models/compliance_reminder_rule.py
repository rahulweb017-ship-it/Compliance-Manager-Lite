from odoo import api, fields, models


class ComplianceReminderRule(models.Model):
    _name = "compliance.reminder.rule"
    _description = "Compliance Reminder Rule"
    _order = "days desc, id"

    days = fields.Integer(
        string="Days Before Expiry",
        required=True,
        help="How many days before the expiry date this reminder is sent.",
    )
    category_id = fields.Many2one(
        "compliance.category",
        string="Category",
        ondelete="cascade",
        help="Leave empty to make this a global default applied to every category "
             "that has no rules of its own.",
    )
    active = fields.Boolean(string="Active", default=True)

    display_name = fields.Char(compute="_compute_display_name")

    _days_positive = models.Constraint(
        "CHECK(days >= 0)",
        "Reminder days must be zero or greater.",
    )
    _unique_days_per_category = models.Constraint(
        "UNIQUE(category_id, days)",
        "A reminder for that number of days already exists for this category.",
    )

    @api.depends("days", "category_id")
    def _compute_display_name(self):
        for rule in self:
            if rule.days == 0:
                label = "On expiry date"
            elif rule.days == 1:
                label = "1 day before"
            else:
                label = "%s days before" % rule.days
            rule.display_name = label

    @api.model
    def _get_global_days(self):
        """Reminder intervals used by categories that define no rules of their own."""
        rules = self.search([("category_id", "=", False)])
        return sorted({rule.days for rule in rules}, reverse=True)
