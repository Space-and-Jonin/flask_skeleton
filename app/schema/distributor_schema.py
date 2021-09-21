from marshmallow import Schema, fields


class DistributorEmployeeSchema(Schema):
    id = fields.UUID()
    first_name = fields.Str()
    last_name = fields.Str()
    email_address = fields.Email()
    phone_number = fields.Str()
    create_secondary_user = fields.Boolean()
    create_retailer = fields.Boolean()


class DistributorSchema(Schema):
    id = fields.UUID()
    name = fields.Str()
    tin_number = fields.Str()
    location = fields.Str()
    created = fields.DateTime()
    modified = fields.DateTime()


class DistributorShowSchema(DistributorSchema):
    employees = fields.Nested(DistributorEmployeeSchema(many=True))


class DistributorCreateSchema(Schema):
    name = fields.Str(required=True)
    tin_number = fields.Str(required=True)
    location = fields.Str()

    class Meta:
        fields = ("name", "tin_number", "location")


class DistributorUpdateSchema(Schema):
    name = fields.Str()
    tin_number = fields.Str()

    class Meta:
        fields = ("name", "tin_number")
