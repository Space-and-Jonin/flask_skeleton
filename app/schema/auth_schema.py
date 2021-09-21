from marshmallow import Schema, fields, validate


class ResendTokenSchema(Schema):
    token_id = fields.UUID(required=True)


class PinChangeSchema(Schema):
    old_password = fields.String(required=True)
    new_password = fields.String(required=True)


class PinResetRequestSchema(Schema):
    phone_number = fields.Str(
        validate=validate.Regexp(
            r"^(\+\d{1,2}\s?)?1?\-?\.?\s?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}$"
        )
    )


class PinResetSchema(Schema):
    token = fields.String(required=True, validate=validate.Regexp(r"\b[0-9]{6}\b"))
    new_password = fields.String(required=True, validate=validate.Length(min=6))
    token_id = fields.UUID(required=True)


class LoginSchema(Schema):
    phone_number = fields.Str(
        validate=validate.Regexp(
            r"^(\+\d{1,2}\s?)?1?\-?\.?\s?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}$"
        )
    )
    password = fields.Str(validate=validate.Length(min=4))


class TokenSchema(Schema):
    access_token = fields.Str()
    refresh_token = fields.Str()
