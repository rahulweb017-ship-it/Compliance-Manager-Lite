from odoo import fields, models


class ComplianceReminderLog(models.Model):
    _name = "compliance.reminder.log"
    _description = "Compliance Reminder History"
    _order = "scheduled_date desc, id desc"
    _rec_name = "record_id"

    record_id = fields.Many2one(
        "compliance.record",
        string="Compliance Record",
        required=True,
        ondelete="cascade",
        index=True,
    )
    category_id = fields.Many2one(
        related="record_id.category_id", string="Category", store=True
    )
    company_id = fields.Many2one(
        related="record_id.company_id", string="Company", store=True, index=True
    )
    days = fields.Integer(
        string="Reminder Days",
        help="Days before expiry this reminder was scheduled for. Zero means the "
             "document had reached its expiry date.",
    )
    scheduled_date = fields.Date(
        string="Scheduled Date",
        required=True,
        help="Expiry date minus the reminder days. Identifies one reminder slot: "
             "changing the expiry date starts a fresh reminder cycle.",
    )
    sent_date = fields.Datetime(string="Sent On", readonly=True)
    recipient_id = fields.Many2one("res.users", string="Recipient")
    recipient_email = fields.Char(string="Recipient Email")
    notification_type = fields.Selection(
        selection=[("email", "Email")],
        string="Notification Type",
        default="email",
        required=True,
    )
    state = fields.Selection(
        selection=[
            ("pending", "Pending"),
            ("sent", "Sent"),
            ("failed", "Failed"),
        ],
        string="Status",
        default="pending",
        required=True,
        index=True,
    )
    error_message = fields.Text(string="Error", readonly=True)

    # One reminder slot per (record, interval, cycle). This is what makes the daily
    # cron idempotent: a slot that is already 'sent' is never sent again, and a new
    # expiry date produces a new scheduled_date and therefore a new slot.
    _sql_constraints = [
        (
            "unique_slot",
            "UNIQUE(record_id, days, scheduled_date)",
            "A reminder for this record, interval and cycle already exists.",
        ),
    ]
