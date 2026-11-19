"""Install-time hooks.

The default reminder schedule is seeded here rather than from an XML data file
on purpose. XML data with ``noupdate="1"`` is re-created whenever its record is
missing, so a customer who deleted an interval would silently get it back on the
next module update. ``post_init_hook`` runs on install only, which makes the
defaults a genuine starting point rather than a recurring override.
"""

DEFAULT_REMINDER_DAYS = (90, 60, 30, 15, 7, 1)
DEFAULT_EXPIRING_THRESHOLD = 30


def post_init_hook(env):
    Rule = env["compliance.reminder.rule"]
    if not Rule.search_count([("category_id", "=", False)]):
        Rule.create([{"days": days} for days in DEFAULT_REMINDER_DAYS])

    # Persist the threshold so Settings shows a concrete value rather than
    # relying on the field default alone.
    param = env["ir.config_parameter"].sudo()
    key = "compliance_manager_lite.expiring_soon_threshold"
    if not param.get_int(key):
        param.set_int(key, DEFAULT_EXPIRING_THRESHOLD)
