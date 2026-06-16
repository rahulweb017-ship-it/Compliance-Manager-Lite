# Compliance Manager Lite

Track compliance documents and never miss an expiry date again. Compliance
Manager Lite is a free, lightweight Odoo app for managing licenses, contracts,
certifications, insurance and any document that expires.

## Features

- **Compliance Categories** - organize records by type (Employee Documents,
  Vehicle Insurance, Contracts, Licenses, Certifications, Vendor Documents).
- **Compliance Records** - name, category, issue date, expiry date,
  responsible user, description and file attachments.
- **Expiry Tracking** - automatic `days remaining` and color-coded status:
  Valid (green), Expiring Soon (orange), Expired (red).
- **Email Reminders** - daily cron sends reminder emails at configurable
  intervals (default 30, 15, 7 and 1 day before expiry).
- **Dashboard** - clickable KPI cards for Total, Valid, Expiring and Expired.
- **Calendar View** - visualize upcoming expiries by month or week.
- **Search & Filters** - filter and group by category, responsible user,
  status and expiry date.
- **Reports** - export compliance records to PDF and XLSX.

## Configuration

Open *Compliance Manager > Configuration > Settings* to change the four
reminder intervals (in days before expiry).

## Reminder automation

A scheduled action (*Compliance: Send Expiry Reminders*) runs once per day.
It refreshes statuses and emails the responsible user when a record reaches a
configured reminder interval. Reminder flags reset automatically when an
expiry date is updated, so renewals start a fresh reminder cycle.

## Security

| Role               | Permissions                                  |
|--------------------|----------------------------------------------|
| Compliance User    | View records assigned to them                |
| Compliance Manager | Create and edit all records and configuration|

## Technical

- Compatible with Odoo 18.0 and 19.0.
- License: LGPL-3.
- Dependencies: `base`, `mail`, `web` (XLSX uses the bundled `xlsxwriter`).
