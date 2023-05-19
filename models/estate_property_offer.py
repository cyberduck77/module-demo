from odoo import api, models, fields
from dateutil.relativedelta import relativedelta
from datetime import datetime

class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Estate property offer model"
    _order = "price desc"

    price = fields.Float()
    state = fields.Selection(selection=[('accepted','Accepted'),('refused','Refused')], copy=False, readonly=True)
    partner_id = fields.Many2one('res.partner', string="Partner", required=True)
    property_id = fields.Many2one('estate.property', required=True)
    validity = fields.Integer(default=7, string='Validity (days)')
    date_deadline = fields.Date(compute='_compute_deadline', inverse='_inverse_validity', default=lambda self: fields.Date.today() + relativedelta(days=+7), string='Deadline')

    @api.depends('validity')
    def _compute_deadline(self):
        for record in self:
            if record.create_date:
                record.date_deadline = fields.Date.to_date(record.create_date) + relativedelta(days=+record.validity)
            else:
                record.date_deadline = fields.Date.today() + relativedelta(days=+record.validity)
    
    def _inverse_validity(self):
        for record in self:
            if record.create_date:
                start_date = datetime.strptime(str(fields.Date.to_date(record.create_date)), '%Y-%m-%d')
            else:
                start_date = datetime.strptime(str(fields.Date.today()), '%Y-%m-%d')
            end_date = datetime.strptime(str(record.date_deadline), '%Y-%m-%d')
            record.validity = (end_date - start_date).days


    def accept_offer(self):
        for record in self:
            record.state = 'accepted'
            record.property_id.partner_id = record.partner_id
            record.property_id.selling_price = record.price
            record.property_id.state = 'offer accepted'
        return True

    def refuse_offer(self):
        for record in self:
            if record.state == 'accepted':
                record.property_id.selling_price = 0.0
            record.state = 'refused'
        return True

    _sql_constraints = [('check_price','CHECK(price > 0)',"All the offer price must be strictly positive")]