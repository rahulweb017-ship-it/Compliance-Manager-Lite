from odoo import fields, models


class ComplianceCategory(models.Model):
    _name = "compliance.category"
    _description = "Compliance Category"
    _order = "name"

    name = fields.Char(string="Category", required=True)
    description = fields.Text(string="Description")
    active = fields.Boolean(string="Active", default=True)
    record_ids = fields.One2many(
        "compliance.record", "category_id", string="Compliance Records"
    )
    record_count = fields.Integer(
        string="Records", compute="_compute_record_count"
    )
    reminder_rule_ids = fields.One2many(
        "compliance.reminder.rule",
        "category_id",
        string="Reminder Schedule",
        help="Reminder intervals for this category. Leave empty to use the global "
             "default schedule configured in Settings.",
    )

    def _compute_record_count(self):
        data = self.env["compliance.record"]._read_group(
            [("category_id", "in", self.ids)],
            groupby=["category_id"],
            aggregates=["__count"],
        )
        mapped = {category.id: count for category, count in data}
        for category in self:
            category.record_count = mapped.get(category.id, 0)

    def _get_reminder_days(self):
        """Reminder intervals for this category, falling back to the global rules."""
        self.ensure_one()
        days = {rule.days for rule in self.reminder_rule_ids if rule.active}
        if days:
            return sorted(days, reverse=True)
        return self.env["compliance.reminder.rule"]._get_global_days()
