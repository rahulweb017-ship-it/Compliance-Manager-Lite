from odoo import api, fields, models
from odoo.fields import Date


class ComplianceRecord(models.Model):
    _name = "compliance.record"
    _description = "Compliance Record"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "expiry_date asc, id desc"

    name = fields.Char(string="Name", required=True, tracking=True)
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
    description = fields.Text(string="Description")
    attachment_ids = fields.Many2many(
        "ir.attachment",
        "compliance_record_attachment_rel",
        "record_id",
        "attachment_id",
        string="Attachments",
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

    reminder_30_sent = fields.Boolean(default=False, copy=False)
    reminder_15_sent = fields.Boolean(default=False, copy=False)
    reminder_7_sent = fields.Boolean(default=False, copy=False)
    reminder_1_sent = fields.Boolean(default=False, copy=False)

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

    @api.model
    def _get_reminder_intervals(self):
        params = self.env["ir.config_parameter"].sudo()
        return [
            int(params.get_param("compliance_manager_lite.reminder_days_1", 30)),
            int(params.get_param("compliance_manager_lite.reminder_days_2", 15)),
            int(params.get_param("compliance_manager_lite.reminder_days_3", 7)),
            int(params.get_param("compliance_manager_lite.reminder_days_4", 1)),
        ]

    @api.model
    def _get_expiring_threshold(self):
        intervals = [days for days in self._get_reminder_intervals() if days > 0]
        return max(intervals) if intervals else 30

    def write(self, vals):
        if "expiry_date" in vals:
            vals.update(
                {
                    "reminder_30_sent": False,
                    "reminder_15_sent": False,
                    "reminder_7_sent": False,
                    "reminder_1_sent": False,
                }
            )
        return super().write(vals)

    def action_open_records(self):
        self.ensure_one()
        return True

    @api.model
    def get_dashboard_data(self):
        # Card counts
        total = self.search_count([])
        valid = self.search_count([('status', '=', 'valid')])
        expiring = self.search_count([('status', '=', 'expiring')])
        expired = self.search_count([('status', '=', 'expired')])

        # Categories breakdown
        categories = self.env['compliance.category'].search([])
        category_data = []
        for cat in categories:
            cat_total = self.search_count([('category_id', '=', cat.id)])
            if cat_total > 0:
                cat_valid = self.search_count([('category_id', '=', cat.id), ('status', '=', 'valid')])
                cat_expiring = self.search_count([('category_id', '=', cat.id), ('status', '=', 'expiring')])
                cat_expired = self.search_count([('category_id', '=', cat.id), ('status', '=', 'expired')])
                category_data.append({
                    'id': cat.id,
                    'name': cat.name,
                    'total': cat_total,
                    'valid': cat_valid,
                    'expiring': cat_expiring,
                    'expired': cat_expired,
                })

        # Upcoming expiries (next 5 records sorted by expiry_date)
        upcoming_recs = self.search([('status', 'in', ['valid', 'expiring'])], limit=5, order='expiry_date asc')
        upcoming_data = []
        for rec in upcoming_recs:
            upcoming_data.append({
                'id': rec.id,
                'name': rec.name,
                'category_name': rec.category_id.name,
                'expiry_date': rec.expiry_date.strftime('%Y-%m-%d') if rec.expiry_date else '',
                'days_remaining': rec.days_remaining,
                'status': rec.status,
                'responsible_name': rec.responsible_user_id.name or '',
            })

        # Expired documents (next 5 expired records)
        expired_recs = self.search([('status', '=', 'expired')], limit=5, order='expiry_date desc')
        expired_data = []
        for rec in expired_recs:
            expired_data.append({
                'id': rec.id,
                'name': rec.name,
                'category_name': rec.category_id.name,
                'expiry_date': rec.expiry_date.strftime('%Y-%m-%d') if rec.expiry_date else '',
                'days_remaining': rec.days_remaining,
                'status': rec.status,
                'responsible_name': rec.responsible_user_id.name or '',
            })

        return {
            'total': total,
            'valid': valid,
            'expiring': expiring,
            'expired': expired,
            'categories': category_data,
            'upcoming': upcoming_data,
            'recent_expired': expired_data,
        }

    @api.model
    def _cron_refresh_status(self):
        records = self.search([])
        records.invalidate_recordset(["days_remaining", "status"])
        records.modified(["expiry_date"])
        records.flush_recordset(["days_remaining", "status"])

    @api.model
    def _cron_send_reminders(self):
        self._cron_refresh_status()
        intervals = self._get_reminder_intervals()
        template = self.env.ref(
            "compliance_manager_lite.mail_template_compliance_reminder",
            raise_if_not_found=False,
        )
        if not template:
            return
        flag_by_interval = {
            30: "reminder_30_sent",
            15: "reminder_15_sent",
            7: "reminder_7_sent",
            1: "reminder_1_sent",
        }
        for interval, flag in flag_by_interval.items():
            if interval not in intervals:
                continue
            records = self.search(
                [
                    ("expiry_date", "!=", False),
                    ("days_remaining", "<=", interval),
                    ("days_remaining", ">=", 0),
                    (flag, "=", False),
                    ("responsible_user_id.email", "!=", False),
                ]
            )
            for record in records:
                template.send_mail(record.id, force_send=True)
                record.write({flag: True})
