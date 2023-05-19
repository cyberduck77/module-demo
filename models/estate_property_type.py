from odoo import api, models, fields

class EstatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = "Estate property type model"
    _sql_constraints = [('unique_type_name','UNIQUE(name)',"The type name must be unique")]

    name = fields.Char(required=True)
    sequence = fields.Integer()
    property_ids = fields.One2many('estate.property', 'type_id')
    offer_ids = fields.One2many('estate.property.offer', 'type_id')
    offer_count = fields.Integer(compute='_compute_offer_count')

    @api.depends('offer_ids')
    def _compute_offer_count(self):
        for record in self:
            record.offer_count = len(record.offer_ids)
