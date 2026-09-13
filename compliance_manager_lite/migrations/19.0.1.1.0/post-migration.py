"""Upgrade 19.0.1.0.x -> 19.0.1.1.0.

Three things have to survive the upgrade:

1. Reminder state. v1.0 tracked "already reminded" in four boolean columns on
   compliance_record. v1.1 tracks it in compliance.reminder.log. Without this
   migration every existing record would look as though it had never been
   reminded, and the first cron run after the upgrade would re-send reminders
   that customers already received.
2. The configured reminder intervals, which move from ir.config_parameter to
   compliance.reminder.rule records.
3. company_id, which is new and must not be left NULL.

Odoo does not drop database columns when a field is removed from a model, so the
old boolean columns are still readable here even though the fields are gone.
"""

import logging

from dateutil.relativedelta import relativedelta

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)

LEGACY_FLAGS = {
    30: "reminder_30_sent",
    15: "reminder_15_sent",
    7: "reminder_7_sent",
    1: "reminder_1_sent",
}
LEGACY_PARAMS = (
    "compliance_manager_lite.reminder_days_1",
    "compliance_manager_lite.reminder_days_2",
    "compliance_manager_lite.reminder_days_3",
    "compliance_manager_lite.reminder_days_4",
)


def _existing_columns(cr, table, columns):
    cr.execute(
        """
        SELECT column_name FROM information_schema.columns
         WHERE table_name = %s AND column_name IN %s
        """,
        (table, tuple(columns)),
    )
    return {row[0] for row in cr.fetchall()}


def _backfill_company(env):
    """Give pre-existing records a company before anything reads company_id."""
    cr = env.cr
    cr.execute("SELECT id FROM compliance_record WHERE company_id IS NULL")
    ids = [row[0] for row in cr.fetchall()]
    if not ids:
        return
    company = env.ref("base.main_company", raise_if_not_found=False) or env["res.company"].search(
        [], order="id", limit=1
    )
    if not company:
        _logger.warning("Compliance upgrade: no company found, company_id left unset")
        return
    cr.execute(
        "UPDATE compliance_record SET company_id = %s WHERE company_id IS NULL",
        (company.id,),
    )
    _logger.info(
        "Compliance upgrade: assigned company %s to %s record(s)", company.id, len(ids)
    )


def _migrate_reminder_flags(env):
    """Turn the four legacy boolean flags into reminder history rows."""
    cr = env.cr
    present = _existing_columns(cr, "compliance_record", LEGACY_FLAGS.values())
    if not present:
        _logger.info("Compliance upgrade: no legacy reminder columns, nothing to migrate")
        return

    selected = sorted(present)
    cr.execute(
        """
        SELECT r.id, r.expiry_date, r.category_id, r.company_id,
               r.responsible_user_id, p.email, r.write_date, {columns}
          FROM compliance_record r
          LEFT JOIN res_users u ON u.id = r.responsible_user_id
          LEFT JOIN res_partner p ON p.id = u.partner_id
         WHERE r.expiry_date IS NOT NULL
        """.format(columns=", ".join("r.%s" % name for name in selected))
    )

    days_by_column = {column: days for days, column in LEGACY_FLAGS.items()}
    Log = env["compliance.reminder.log"]
    values = []
    for row in cr.fetchall():
        (
            record_id,
            expiry_date,
            category_id,
            company_id,
            user_id,
            email,
            write_date,
            *flags
        ) = row
        for column, was_sent in zip(selected, flags):
            if not was_sent:
                continue
            days = days_by_column[column]
            values.append(
                {
                    "record_id": record_id,
                    "category_id": category_id,
                    "company_id": company_id,
                    "days": days,
                    "scheduled_date": expiry_date - relativedelta(days=days),
                    # The exact send time was never stored in v1.0; the record's
                    # last write is the closest honest approximation.
                    "sent_date": write_date,
                    "recipient_id": user_id,
                    "recipient_email": email,
                    "notification_type": "email",
                    "state": "sent",
                }
            )

    if values:
        Log.create(values)
    _logger.info(
        "Compliance upgrade: migrated %s reminder flag(s) into history", len(values)
    )


def _migrate_reminder_intervals(env):
    """Carry the configured intervals over from config parameters to rules."""
    Param = env["ir.config_parameter"].sudo()
    Rule = env["compliance.reminder.rule"]

    configured = set()
    for key in LEGACY_PARAMS:
        raw = Param.get_param(key)
        if raw in (None, False, ""):
            continue
        try:
            days = int(raw)
        except (TypeError, ValueError):
            continue
        if days > 0:
            configured.add(days)

    if not configured:
        _logger.info("Compliance upgrade: no legacy intervals found, keeping defaults")
        return

    existing = Rule.search([("category_id", "=", False)])
    missing = configured - {rule.days for rule in existing}
    if missing:
        Rule.create([{"days": days} for days in sorted(missing, reverse=True)])

    # Anything the customer had not configured must not start firing now.
    surplus = existing.filtered(lambda rule: rule.days not in configured)
    if surplus:
        surplus.unlink()

    _logger.info(
        "Compliance upgrade: global reminder schedule set to %s",
        sorted(configured, reverse=True),
    )


def _seed_expiring_threshold(env):
    """v1.0 derived the threshold from the intervals; v1.1 stores it explicitly."""
    Param = env["ir.config_parameter"].sudo()
    key = "compliance_manager_lite.expiring_soon_threshold"
    if Param.get_param(key):
        return
    days = env["compliance.reminder.rule"]._get_global_days()
    Param.set_param(key, str(max(days) if days else 30))


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _backfill_company(env)
    _migrate_reminder_flags(env)
    _migrate_reminder_intervals(env)
    _seed_expiring_threshold(env)
    # Stored status fields depend on the threshold, so reprice everything once.
    env["compliance.record"]._cron_refresh_status()
