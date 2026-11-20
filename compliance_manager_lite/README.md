# Compliance Manager Lite - Document Expiry Tracking & Renewal Reminders for Odoo

Document expiry tracking and automatic renewal reminders for Odoo 17, 18, 19
and 20. Compliance Manager Lite is a free, lightweight Odoo app for tracking the
expiration dates of licenses, permits, certificates, contracts, insurance
policies, vehicle documents and employee documents, and for emailing the
responsible person before anything lapses.

Common uses: employee document expiry (passports, visas, work permits, driving
licenses), certificate expiry tracking (ISO, calibration, inspection), contract
renewal reminders, fleet and vehicle insurance renewals, and business license
and permit tracking.

## Overview

Record every document that has an expiry date, group it by category, and let the
app work out whether it is Valid, Expiring Soon or Expired. A daily scheduled
action emails the responsible user on the schedule you configure, and records
every reminder it sends so nobody is mailed twice about the same thing.

## Features

- **Compliance Categories** - organize records by type (Employee Documents,
  Vehicle Insurance, Contracts, Licenses, Certifications, Equipment).
- **Compliance Records** - document name, reference number, category, issue and
  expiry dates, responsible user, department, description and attachments.
- **Expiry Tracking** - automatic `days remaining` and color-coded status:
  Valid (green), Expiring Soon (orange), Expired (red).
- **Custom Reminder Schedules** - default intervals of 90, 60, 30, 15, 7 and 1
  day, configurable globally and overridable per category.
- **Reminder History** - every reminder is logged with its recipient, scheduled
  date, send date and outcome (Pending / Sent / Failed).
- **Dashboard** - clickable KPI cards for Total, Valid, Expiring, Expired,
  Expiring This Month and Expired This Month.
- **My Compliance** - a dedicated view of the documents you are responsible for.
- **Chatter and Activities** - native Odoo messaging, followers and scheduled
  activities on every record.
- **Calendar View** - visualize upcoming expiries by month or week.
- **Search & Filters** - filter and group by category, responsible user,
  department, company, status and expiry date.
- **Reports** - PDF with a summary block and detailed table, plus XLSX export.
- **Multi-company** - records are scoped by company through record rules.

## Installation

1. Copy `compliance_manager_lite` into your Odoo addons path.
2. Restart the Odoo service.
3. Enable developer mode, then *Apps > Update Apps List*.
4. Search for *Compliance Manager Lite* and click Install.

Requires the `hr` app (for Department) and the `xlsxwriter` Python package,
which ships with Odoo by default.

## Configuration

Open *Compliance Manager > Configuration*.

- **Settings > Expiring Soon Threshold** - how many days before expiry a document
  starts counting as Expiring Soon. Default 30. Changing it reprices every
  existing record immediately.
- **Default Reminder Schedule** - the intervals used by categories that do not
  define their own.

## Creating compliance records

*Compliance Manager > Compliance Records > New*. Name, category and expiry date
are required; everything else is optional. The form is organised into General
Information, Responsibility, Validity, and tabs for Description, Documents and
Reminders.

## Reminder configuration

Reminders resolve in one step: if the record's category has its own schedule,
that schedule is used; otherwise the global default applies. Open a category and
use the *Reminder Schedule* tab to give it its own intervals.

A scheduled action (*Compliance: Send Expiry Reminders*) runs once per day. It
refreshes statuses, then for each record sends the most urgent reminder that has
come due. Each reminder slot is identified by record, interval and expiry cycle,
so the cron is safe to run repeatedly and changing an expiry date starts a fresh
cycle. Failed sends are recorded with their error and retried on the next run.

## Dashboard

*Compliance Manager > Dashboard*. Every KPI and category card is clickable and
opens the matching filtered list. Counts are computed from live records.

## My Compliance

*Compliance Manager > My Compliance* shows the records where you are the
responsible user, with the same filters as the main list.

## Reports

- **PDF** - select records in the list, then *Print > Compliance Records*.
  Includes a summary of the selected records and a detailed table.
- **XLSX** - select records, then *Action > Export to XLSX*.

Both respect the records you selected and the access rights you have.

## Security

| Role               | Permissions                                       |
|--------------------|---------------------------------------------------|
| Compliance User    | Create records, view and edit their own           |
| Compliance Manager | Full access to all records, categories and config |

Record rules restrict Compliance Users to records where they are the responsible
user. Managers see everything within the companies they are allowed into.

## Multi-company

Every record carries a `company_id`, and a global record rule limits visibility
to the user's allowed companies. Reminder history inherits the company of its
record.

## FAQ

**Can I use reminder intervals other than the defaults?**
Yes. Any interval you add is honoured, globally or per category.

**Will I get duplicate reminder emails?**
No. Each reminder slot is recorded and sent at most once.

**What happens when I change an expiry date?**
The reminder cycle restarts, so the renewed document is reminded about again.

**Does it need the HR app?**
Yes, for the Department field.

## Technical

- Compatible with Odoo 17.0, 18.0, 19.0 and 20.0 (Community and Enterprise).
- License: LGPL-3.
- Dependencies: `base`, `mail`, `web`, `hr`; Python `xlsxwriter`.

## Changelog

### v1.1.2

* Odoo 20.0 support
* Version 1.1 now available on Odoo 17.0 and 18.0 as well
* Store listing refreshed

### v1.1.0

* Custom reminder schedules, globally and per category
* Reminder history with per-send status and error tracking
* Chatter integration
* Activities
* Improved expiry status with human-readable remaining time
* Configurable expiring-soon threshold
* Dashboard improvements, including Expiring/Expired This Month
* My Compliance
* Improved filters, search fields and group-bys
* Improved PDF report with summary section
* XLSX export with reference and department
* Multi-company improvements

### v1.0.5

* First public release: records, categories, dashboard, reminders, PDF and XLSX
  reports.
