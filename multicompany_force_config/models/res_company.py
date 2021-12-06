from odoo import api, fields, models
from odoo.addons.json_field.json import JsonField


class Company(models.Model):
    _inherit = 'res.company'

    @api.model
    def create(self, vals):
        new_company = super(Company, self.sudo()).create(vals)

        # Give access to SUPPORT USER
        get_param = self.env["ir.config_parameter"].sudo().get_param
        user_support_ref = get_param("company_users.user_support", default="base.user_admin")
        support_user = self.env.ref(user_support_ref)
        support_user.sudo().write({'company_ids': [(4, new_company.id)]})

        self.env['multicompany.force.config']._configure(new_company)
        return new_company

    def configure(self):
        companies = self
        self.env['multicompany.force.config']._configure(companies)