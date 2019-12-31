"""Default Credentials Schema"""
from marshmallow import Schema, fields


class DefaultCredentialSchema(Schema):
    """Default Credentials Schema"""

    name = fields.Str(required=True)
    hostname = fields.Str(required=True)
