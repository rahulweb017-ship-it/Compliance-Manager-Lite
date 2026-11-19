import logging

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models
from odoo.fields import Date, Datetime

_logger = logging.getLogger(__name__)

DEFAULT_EXPIRING_THRESHOLD = 30


class ComplianceRecord(models.Model):
    _name = "compliance.record"
    _description = "Compliance Record"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "expiry_date asc, id desc"

    name = fields.Char(string="Document Name", required=True, tracking=True)
    reference = fields.Char(string="Reference Number", tracking=True, copy=False)
    category_id = fields.Many2one(
        "compliance.category", string="Category", required=True, tracking=True
    )
    issue_date = fields.Date(string="Issue Date")
    expiry_date = fields.Date(string="Expiry Date", required=True, tracking=True)
    responsible_user_id = fields.Many2one(
        "res.users",
        string="Responsible",
        default=lambda self: self.env.user,
        tracking=True,
    )
    department_id = fields.Many2one(
        "hr.department", string="Department", tracking=True
    )
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        index=True,
        default=lambda self: self.env.company,
    )
    description = fields.Text(string="Description")
    attachment_ids = fields.Many2many(
        "ir.attachment",
        "compliance_record_attachment_rel",
        "record_id",
        "attachment_id",
        string="Attachments",
    )
    reminder_log_ids = fields.One2many(
        "compliance.reminder.log", "record_id", string="Reminder History", readonly=True
    )
    active = fields.Boolean(string="Active", default=True)

    days_remaining = fields.Integer(
        string="Days Remaining",
        compute="_compute_status",
        store=True,
    )
    status = fields.Selection(
        selection=[
            ("valid", "Valid"),
            ("expiring", "Expiring Soon"),
            ("expired", "Expired"),
        ],
        string="Status",
        compute="_compute_status",
        store=True,
    )
    expiry_label = fields.Char(string="Expiry", compute="_compute_expiry_label")

    # ------------------------------------------------------------------
    # Status engine
    # ------------------------------------------------------------------

    @api.depends("expiry_date")
    def _compute_status(self):
        today = Date.context_today(self)
        threshold = self._get_expiring_threshold()
        for record in self:
            if not record.expiry_date:
                record.days_remaining = 0
                record.status = "valid"
                continue
            delta = (record.expiry_date - today).days
            record.days_remaining = delta
            if delta < 0:
                record.status = "expired"
            elif delta <= threshold:
                record.status = "expiring"
            else:
                record.status = "valid"

    @api.depends("days_remaining", "expiry_date")
    def _compute_expiry_label(self):
        for record in self:
            days = record.days_remaining
            if not record.expiry_date:
                record.expiry_label = ""
            elif days > 1:
                record.expiry_label = "%s days remaining" % days
            elif days == 1:
                record.expiry_label = "1 day remaining"
            elif days == 0:
                record.expiry_label = "Expires today"
            elif days == -1:
                record.expiry_label = "Expired 1 day ago"
            else:
                record.expiry_label = "Expired %s days ago" % abs(days)

    @api.model
    def _get_expiring_threshold(self):
        """Days before expiry at which a document starts counting as Expiring Soon."""
        # get_int() returns the default for a missing or non-integer value.
        threshold = self.env["ir.config_parameter"].sudo().get_int(
            "compliance_manager_lite.expiring_soon_threshold",
            DEFAULT_EXPIRING_THRESHOLD,
        )
        return threshold if threshold > 0 else DEFAULT_EXPIRING_THRESHOLD

    @api.model
    def _cron_refresh_status(self):
        """Recompute the stored status fields, which go stale as the calendar moves."""
        records = self.with_context(active_test=False).search([])
        records.invalidate_recordset(["days_remaining", "status"])
        records.modified(["expiry_date"])
        records.flush_recordset(["days_remaining", "status"])

    # ------------------------------------------------------------------
    # Reminder engine
    # ------------------------------------------------------------------

    def _get_due_reminder_days(self, today):
        """Return the single most urgent reminder interval that is due today.

        Every interval whose trigger date has passed is a candidate; the smallest
        one wins because it sits closest to the expiry date. That sends one email
        per interval at the right moment, and stops a record created shortly before
        its expiry from firing every interval at once.
        """
        self.ensure_one()
        if not self.expiry_date or self.expiry_date < today:
            return None
        due = [
            days
            for days in self.category_id._get_reminder_days()
            if self.expiry_date - relativedelta(days=days) <= today
        ]
        return min(due) if due else None

    def _get_reminder_slot(self, days, scheduled_date):
        """Find or create the reminder history row for one reminder slot."""
        self.ensure_one()
        Log = self.env["compliance.reminder.log"]
        slot = Log.search(
            [
                ("record_id", "=", self.id),
                ("days", "=", days),
                ("scheduled_date", "=", scheduled_date),
            ],
            limit=1,
        )
        if slot:
            return slot
        return Log.create(
            {
                "record_id": self.id,
                "days": days,
                "scheduled_date": scheduled_date,
                "recipient_id": self.responsible_user_id.id,
                "recipient_email": self.responsible_user_id.email,
                "notification_type": "email",
                "state": "pending",
            }
        )

    def _send_reminder(self, template, slot):
        """Send one reminder and record the outcome. Never raises."""
        self.ensure_one()
        try:
            # Savepoint so one failed send cannot abort the whole cron batch.
            with self.env.cr.savepoint():
                template.send_mail(self.id, force_send=True, raise_exception=True)
        except Exception as error:  # noqa: BLE001 - recorded on the slot, cron continues
            _logger.warning(
                "Compliance reminder failed for record %s (%s days): %s",
                self.id,
                slot.days,
                error,
            )
            slot.write({"state": "failed", "error_message": str(error)})
            return False
        slot.write(
            {
                "state": "sent",
                "sent_date": Datetime.now(),
                "error_message": False,
                "recipient_id": self.responsible_user_id.id,
                "recipient_email": self.responsible_user_id.email,
            }
        )
        return True

    @api.model
    def _cron_send_reminders(self):
        """Daily reminder run.

        Safe to execute repeatedly: the unique constraint on
        (record_id, days, scheduled_date) means each reminder slot fires at most
        once, and a changed expiry date yields a new slot and a fresh cycle.
        """
        self._cron_refresh_status()
        today = Date.context_today(self)

        upcoming_template = self.env.ref(
            "compliance_manager_lite.mail_template_compliance_reminder",
            raise_if_not_found=False,
        )
        expired_template = self.env.ref(
            "compliance_manager_lite.mail_template_compliance_expired",
            raise_if_not_found=False,
        )
        if not upcoming_template and not expired_template:
            return

        records = self.search(
            [
                ("expiry_date", "!=", False),
                ("responsible_user_id.email", "!=", False),
            ]
        )
        for record in records:
            if record.expiry_date < today:
                # Expired: notify once per expiry cycle, using day 0 as the slot.
                if not expired_template:
                    continue
                slot = record._get_reminder_slot(0, record.expiry_date)
                if slot.state != "sent":
                    record._send_reminder(expired_template, slot)
                continue

            if not upcoming_template:
                continue
            days = record._get_due_reminder_days(today)
            if days is None:
                continue
            scheduled_date = record.expiry_date - relativedelta(days=days)
            slot = record._get_reminder_slot(days, scheduled_date)
            if slot.state != "sent":
                record._send_reminder(upcoming_template, slot)

    # ------------------------------------------------------------------
    # Dashboard
    # ------------------------------------------------------------------

    @api.model
    def get_dashboard_data(self):
        today = Date.context_today(self)
        month_start = today.replace(day=1)
        month_end = month_start + relativedelta(months=1, days=-1)

        # One grouped query for the status cards rather than a count per status.
        status_counts = dict.fromkeys(("valid", "expiring", "expired"), 0)
        for status, count in self._read_group(
            [], groupby=["status"], aggregates=["__count"]
        ):
            if status in status_counts:
                status_counts[status] = count
        total = sum(status_counts.values())

        # One grouped query for the entire category breakdown.
        category_map = {}
        for category, status, count in self._read_group(
            [], groupby=["category_id", "status"], aggregates=["__count"]
        ):
            if not category:
                continue
            entry = category_map.setdefault(
                category.id,
                {
                    "id": category.id,
                    "name": category.display_name,
                    "total": 0,
                    "valid": 0,
                    "expiring": 0,
                    "expired": 0,
                },
            )
            entry["total"] += count
            if status in entry:
                entry[status] += count

        expiring_this_month = self.search_count(
            [("expiry_date", ">=", today), ("expiry_date", "<=", month_end)]
        )
        expired_this_month = self.search_count(
            [("expiry_date", ">=", month_start), ("expiry_date", "<", today)]
        )

        def _serialise(records):
            return [
                {
                    "id": rec.id,
                    "name": rec.name,
                    "category_name": rec.category_id.display_name or "",
                    "expiry_date": rec.expiry_date.strftime("%Y-%m-%d")
                    if rec.expiry_date
                    else "",
                    "days_remaining": rec.days_remaining,
                    "status": rec.status,
                    "responsible_name": rec.responsible_user_id.name or "",
                }
                for rec in records
            ]

        upcoming = self.search(
            [("status", "in", ["valid", "expiring"])], limit=5, order="expiry_date asc"
        )
        expired = self.search(
            [("status", "=", "expired")], limit=5, order="expiry_date desc"
        )

        return {
            "total": total,
            "valid": status_counts["valid"],
            "expiring": status_counts["expiring"],
            "expired": status_counts["expired"],
            "expiring_this_month": expiring_this_month,
            "expired_this_month": expired_this_month,
            "categories": sorted(
                category_map.values(), key=lambda entry: entry["name"] or ""
            ),
            "upcoming": _serialise(upcoming),
            "recent_expired": _serialise(expired),
        }
