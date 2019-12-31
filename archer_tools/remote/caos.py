"""Caos Plugin for Archer Tools."""
import re
from typing import Dict, List

from marshmallow import Schema, fields, post_load, validate

from archer_tools.credential_schema import DefaultCredentialSchema
from archer_tools.remote.source import Source
from archer_tools.remote.libraries.caos_client import CaosClient


class CaosQuerySchema(Schema):
    """Caos Query Schema."""

    request_type = fields.Str(
        default="archer", validate=validate.OneOf(["archer"])
    )
    scope = fields.Str(validate=validate.OneOf(["directorate", "enterprise"]))
    status = fields.Str(
        default="approved",
        validate=validate.OneOf(["approved", "denied", "pending"]),
    )


class CaosSchema(Schema):
    """Caos Schema."""

    credential = fields.Str(required=True)
    query = fields.Nested(CaosQuerySchema, required=True)


class CaosProxiesCredentialSchema(Schema):
    """Caos Proxies."""

    http_proxy = fields.Str()
    https_proxy = fields.Str()


class CaosCredentialSchema(DefaultCredentialSchema):
    """Caos Default Credential Schema."""

    cert = fields.Str(required=True)
    key = fields.Str(required=True)
    proxies = fields.Nested(CaosProxiesCredentialSchema)
    verify = fields.Str()

    @post_load()
    @staticmethod
    def transform_credentials(data: Dict) -> Dict:
        """Transform name as the key for the dictionary.

        Args:
            data (Dict): [description]
            kwargs: See Kwargs

        Kwargs:
            Kwargs: Catch all from marshmallow.post_load()

        Returns:
            Dict: [description]

        """
        name = data.pop("name")
        return_data = {name: data}
        return return_data


class CaosSource(Source):
    """Caos Source."""

    __source_schema__ = CaosSchema
    __destination_schema__ = CaosSchema
    __credential_schema__ = CaosCredentialSchema
    __key__: str = "caos"

    def query(self, *args, **kwargs) -> List[str]:
        """Query Caos for OINs per account request.

        Returns:
            List[str]: [description]

        """
        self.logger.error("Running query for CAOS")
        client = CaosClient(**self.data["credential"])
        data = client.accounts(**self.data["query"])

        user_oins = []
        for item in data["results"]:
            check_oin = re.match(r"\w\d{2}\w\d{2}\w{2}", item["requestor"])
            if check_oin:
                user_oins.append(item["requestor"])
        return user_oins
