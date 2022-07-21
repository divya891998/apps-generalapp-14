from odoo import api, fields, models, _
from odoo.release import major_version # 14.0
from datetime import date

import logging
_logger = logging.getLogger(__name__)


class BaseModuleUpdate(models.TransientModel):
    _inherit = "base.module.update"

    def button_get_migration_info(self):
        mig_version = str(float(major_version) + 1.0)
        for module in self.env["ir.module.module"].search([]):
            module.mig_url = "https://github.com/OCA/OpenUpgrade/pull/3265"
            module.mig_state = "merged"
            module.mig_opened = date(2022, 6, 14)
            module.mig_merged = date(2022, 6, 16)
            module.mig_last_commented = date(2022, 6, 16)