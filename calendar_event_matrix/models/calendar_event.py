from datetime import timedelta

from odoo import fields, models


class CalendarEvent(models.Model):
    _inherit = "calendar.event"

    partner_count = fields.Integer("No of attendees", compute="_compute_partner_count")

    def _compute_partner_count(self):
        for record in self:
            record.partner_count = len(record.partner_ids)

    start_date_str = fields.Char("Start Date (text)", compute="_compute_start_date_str")

    def _compute_start_date_str(self):
        for record in self:
            if record.start:
                # TODO: get hours from timezone
                record.start_date_str = str((record.start + timedelta(hours=+2)).date())
            else:
                record.start_date_str = str(record.start_date)

    matrix_row_id = fields.Many2one(
        "calendar.event.matrix.row", string="Matrix Row", ondelete="cascade"
    )
    matrix_row_sequence = fields.Integer(
        "Matrix Row Sequence", related="matrix_row_id.sequence"
    )
    matrix_available_partner_ids = fields.Many2many(
        "res.partner", compute="_compute_matrix_available_partner_ids"
    )

    def _compute_matrix_available_partner_ids(self):
        for record in self:
            partner_ids = self.env["res.partner"]
            for partner in record.matrix_row_id.matrix_id.partner_ids:
                domain = [
                    ("partner_ids", "in", [partner.id]),
                    ("id", "!=", record.id),
                    "|",
                    "&",
                    ("start", ">", record.start),
                    ("start", "<", record.stop),
                    "&",
                    ("stop", ">", record.start),
                    ("stop", "<", record.stop),
                ]
                overlapping_events = self.env["calendar.event"].search(domain)
                if not overlapping_events:
                    partner_ids += partner
            record.matrix_available_partner_ids = partner_ids

    matrix_partner_attending = fields.Boolean(
        "Matrix Partner Attending",
        compute="_compute_matrix_partner_attending",
        inverse="_inverse_matrix_partner_attending",
    )

    def _compute_matrix_partner_attending(self):
        # partner_id = self.env.context.get("matrix_partner_id")
        # partner_id.ensure_one()
        for record in self:
            partner_id = record.matrix_row_id.matrix_id.matrix_partner_id
            if partner_id in record.partner_ids:
                record.matrix_partner_attending = True
            else:
                record.matrix_partner_attending = False

    def _inverse_matrix_partner_attending(self):
        # partner_id = self.env.context.get("matrix_partner_id")
        # partner_id.ensure_one()
        for record in self:
            partner_id = record.matrix_row_id.matrix_id.matrix_partner_id
            if record.matrix_partner_attending:
                record.write({"partner_ids": [(4, partner_id.id, 0)]})
            else:
                record.write({"partner_ids": [(3, partner_id.id, 0)]})
