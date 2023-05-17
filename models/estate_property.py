from odoo import api, models, fields
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta

class EstateProperty(models.Model):
    _name = "estate.property"
    _description = """
    Estate Property Model
    """
    
    name = fields.Char(required=True)
    description = fields.Text()
    postcode = fields.Char()
    date_availability = fields.Date(string='Available Date', default=lambda self: fields.Date.today() + relativedelta(months=+3), copy=False)
    expected_price = fields.Float(required=True)
    selling_price = fields.Float(copy=False, readonly=True)
    bedrooms = fields.Integer(default=2)
    living_area = fields.Integer(string='Living Area (sqm)')
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer(string='Garden Area (sqm)')
    garden_orientation = fields.Selection(
        selection=[('north','North'),('west','West'),('south','South'),('east','East')]
    )

    @api.onchange('garden')
    def _onchange_garden(self):
        if self.garden == True:
            self.garden_area = 10
            self.garden_orientation = 'north'
        else:
            self.garden_area = 0
            self.garden_orientation = ''

    active = fields.Boolean(default=True)
    state = fields.Selection(
        required=True,
        copy=False,
        selection=[('new','New'),('offer received','Offer Received'),('offer accepted','Offer Accepted'),('sold','Sold'),('canceled','Canceled')],
        default='new',
        readonly=True
    )

    total_area = fields.Integer(compute='_compute_total_area')

    @api.depends('living_area', 'garden_area')
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area


    property_type_id = fields.Many2one('estate.property.type', string='Property Type')
    offer_ids = fields.One2many('estate.property.offer', 'property_id')
    tag_ids = fields.Many2many('estate.property.tag')

    best_price = fields.Integer(compute='_find_best_price', string="Best Offer")

    @api.depends("offer_ids.price")
    def _find_best_price(self):
        for record in self:
            if len(record.offer_ids) > 0:
                record.best_price = max(record.mapped('offer_ids.price'))
            if len(record.offer_ids) == 0:
                record.best_price == 0

    user_id = fields.Many2one('res.users', string='Salesman', default=lambda self: self.env.user)
    partner_id = fields.Many2one('res.partner', string='Buyer', copy=False, readonly=True)

    def sell_property(self):
        for record in self:
            if record.state == 'canceled':
                raise UserError("Canceled properties cannot be sold")
            else:
                record.state = 'sold'
        return True

    def cancel_property(self):
        for record in self:
            if record.state == 'sold':
                raise UserError("Sold properties cannot be canceled")
            else:
                record.state = 'canceled'
        return True
    