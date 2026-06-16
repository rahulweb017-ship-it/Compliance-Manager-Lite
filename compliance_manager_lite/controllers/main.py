import io

from odoo import http
from odoo.http import content_disposition, request


class ComplianceExportController(http.Controller):

    @http.route("/compliance/export/xlsx", type="http", auth="user")
    def export_xlsx(self, ids=None, **kwargs):
        import xlsxwriter

        Record = request.env["compliance.record"]
        if ids:
            record_ids = [int(i) for i in ids.split(",") if i.strip().isdigit()]
            records = Record.browse(record_ids).exists()
        else:
            records = Record.search([])

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {"in_memory": True})
        sheet = workbook.add_worksheet("Compliance Records")

        bold = workbook.add_format({"bold": True, "bg_color": "#D9E1F2", "border": 1})
        cell = workbook.add_format({"border": 1})
        date_fmt = workbook.add_format({"border": 1, "num_format": "yyyy-mm-dd"})

        headers = [
            "Name",
            "Category",
            "Responsible",
            "Issue Date",
            "Expiry Date",
            "Days Remaining",
            "Status",
        ]
        for col, header in enumerate(headers):
            sheet.write(0, col, header, bold)
        widths = [30, 22, 22, 14, 14, 16, 14]
        for col, width in enumerate(widths):
            sheet.set_column(col, col, width)

        status_labels = dict(
            Record._fields["status"]._description_selection(request.env)
        )
        row = 1
        for rec in records:
            sheet.write(row, 0, rec.name or "", cell)
            sheet.write(row, 1, rec.category_id.name or "", cell)
            sheet.write(row, 2, rec.responsible_user_id.name or "", cell)
            if rec.issue_date:
                sheet.write_datetime(row, 3, rec.issue_date, date_fmt)
            else:
                sheet.write(row, 3, "", cell)
            if rec.expiry_date:
                sheet.write_datetime(row, 4, rec.expiry_date, date_fmt)
            else:
                sheet.write(row, 4, "", cell)
            sheet.write_number(row, 5, rec.days_remaining or 0, cell)
            sheet.write(row, 6, status_labels.get(rec.status, ""), cell)
            row += 1

        workbook.close()
        output.seek(0)
        data = output.read()

        return request.make_response(
            data,
            headers=[
                (
                    "Content-Type",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                ),
                ("Content-Disposition", content_disposition("compliance_records.xlsx")),
            ],
        )
