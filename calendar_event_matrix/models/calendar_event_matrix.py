from datetime import datetime, timedelta
from odoo import _, api, fields, models


class CalendarEventMatrix(models.Model):
    _name = 'calendar.event.matrix'
    _description = 'Calendar Event Matrix'

    name = fields.Char()
    date_from = fields.Date("Show From Date", default=datetime.now().date())
    date_action = fields.Date("Add Date", default=datetime.now().date())
    row_ids = fields.One2many('calendar.event.matrix.row', 'matrix_id', string="Types")
    event_ids = fields.Many2many('calendar.event')
    matrix_partner_id = fields.Many2one(
        "res.partner",
        "Matrix Partner",
        required=True,
        default=lambda self: self.env.user.partner_id,
        help="Attend/unattend calendar events for this partner.",
    )

    def add_date(self):
        self.event_ids = self._default_event_ids(add_date=self.date_action)

    def remove_date(self):
        self.write({'event_ids': [
            (2, calendar_event.id) for calendar_event in self.event_ids if calendar_event.start_date == self.date_action
        ]})

    def show_matrix(self):
        datetime_from_day_before = datetime.combine(self.date_from, datetime.min.time()) + timedelta(days=-1)
        self.event_ids = self._default_event_ids(show_from_date=datetime_from_day_before.date())
        view_ref = self.env.context.get("view_ref")
        view = self.env.ref(view_ref)
        return {
            "type": "ir.actions.act_window",
            "res_model": "calendar.event.matrix",
            "views": [[view.id, "form"]],
            # "res_id": self.env.context["active_id"],
            "res_id": self.id,
        }

    # def reload(self):
    #     self.event_ids = self._default_event_ids()

    def _default_event_ids(self, add_date=None, show_from_date=None):
        """take care that the widget gets records passed for every combination
        of calendar.event.matrix.row and start/start_date involved"""

        # required: name, privacy, show_as, start, stop

        if not show_from_date:
            show_from_date = datetime(2000, 1, 1).date()
        calendar_events = self.env['calendar.event'].search(
            [
                ('matrix_row_id', 'in', self.row_ids.ids),
                '|', 
                ('start', '>', show_from_date),
                ('start_date', '>', show_from_date),
            ]
        )
        calendar_event_dates_str = calendar_events.mapped('start_date_str')
        calendar_event_dates = [datetime.strptime(s, '%Y-%m-%d').date() for s in calendar_event_dates_str]

        if add_date:
            calendar_event_dates.append(add_date)

        # TODO: exponentinally increasing records!
        result = [(5, 0, 0)] + [
            (0, 0, {
                'name': "{} on {}".format(calendar_event_matrix_row.name, str(calendar_event_date)),
                'matrix_row_id': calendar_event_matrix_row.id,
                'start': calendar_event_date + timedelta(
                    hours=calendar_event_matrix_row.default_start.hour,
                    minutes=calendar_event_matrix_row.default_start.minute,
                    seconds=calendar_event_matrix_row.default_start.second,
                ),
                'stop': calendar_event_date + timedelta(
                    hours=calendar_event_matrix_row.default_stop.hour,
                    minutes=calendar_event_matrix_row.default_stop.minute,
                    seconds=calendar_event_matrix_row.default_stop.second,
                ),
                'privacy': 'public',
                'show_as': 'busy',
                'partner_ids': [],
            })
            # if there isn't a calendar.event record for the calendar.event.matrix_row on the date, create a new one
            if not calendar_events.filtered(lambda x: x.matrix_row_id == calendar_event_matrix_row and x.start == calendar_event_date) else
            # otherwise, return the line
            (4, calendar_events.filtered(lambda x: x.matrix_row_id == calendar_event_matrix_row and x.start == calendar_event_date)[0].id)
            # loop
            for calendar_event_matrix_row in self.row_ids
            for calendar_event_date in calendar_event_dates
            if calendar_event_date >= show_from_date
        ]
        return result