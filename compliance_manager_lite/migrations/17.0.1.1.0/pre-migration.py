"""Upgrade 19.0.1.0.x -> 19.0.1.1.0, pre stage.

v1.0 shipped the record rules inside a ``noupdate="1"`` block. Odoo records that
flag on the ir_model_data row when the record is first created, and keeps
honouring the stored flag no matter what later versions of the XML say. So
simply moving the rules into an updatable block is not enough: on an existing
database the old rules would survive while the new ACLs applied, leaving what
ships and what runs out of step.

Clearing the flag here, before the data files load, lets this very upgrade
install the corrected rules.
"""

import logging

_logger = logging.getLogger(__name__)

UPDATABLE_XMLIDS = (
    "rule_compliance_record_user_own",
    "rule_compliance_record_manager_all",
)


def migrate(cr, version):
    cr.execute(
        """
        UPDATE ir_model_data
           SET noupdate = false
         WHERE module = 'compliance_manager_lite'
           AND model = 'ir.rule'
           AND name IN %s
        """,
        (UPDATABLE_XMLIDS,),
    )
    _logger.info(
        "Compliance upgrade: cleared noupdate on %s record rule(s)", cr.rowcount
    )
