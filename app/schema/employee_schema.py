from marshmallow import Schema, fields, validate

from app import constants


class EmployeeSchema(Schema):
    id = fields.UUID(required=True)
    first_name = fields.Str(required=True, validate=validate.Length(min=2, max=24))
    last_name = fields.Str(required=True, validate=validate.Length(min=2, max=24))
    email_address = fields.Email()
    phone_number = fields.Str(
        validate=validate.Regexp(constants.PHONE_NUMBER_REGEX), required=True
    )
    create_secondary_user = fields.Boolean()
    create_retailer = fields.Boolean()
    distributor_id = fields.UUID()
    created = fields.DateTime(required=True)
    modified = fields.DateTime(required=True)


class EmployeeCreateSchema(EmployeeSchema):
    password = fields.Str(required=True, validate=validate.Length(min=5))

    class Meta:
        fields = [
            "first_name",
            "last_name",
            "email_address",
            "phone_number",
            "password",
            "create_secondary_user",
            "create_retailer",
            "distributor_id",
        ]


class EmployeeUpdateSchema(Schema):
    first_name = fields.Str(validate=validate.Length(min=2, max=24))
    last_name = fields.Str(validate=validate.Length(min=2, max=24))
    email_address = fields.Email()
    phone_number = fields.Str(validate=validate.Regexp(constants.PHONE_NUMBER_REGEX))
    create_secondary_user = fields.Boolean()
    create_retailer = fields.Boolean()

    class Meta:
        fields = [
            "first_name",
            "last_name",
            "email_address",
            "phone_number",
            "create_secondary_user",
            "create_retailer",
        ]
