"""Archer Plugin for Archer Tools."""
from typing import Dict, List

from marshmallow import (
    Schema, fields, post_load
)

from archer_tools.credential_schema import DefaultCredentialSchema
from archer_tools.remote.source import Source


class ManualCredentialSchema(DefaultCredentialSchema):
    """None"""

    @post_load()
    def transform_credentials(self, data: Dict, **kwargs) -> Dict:
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


class ManualSrcSchema(Schema):
    """Archer Schema."""

    credential = fields.Str(required=True)
    users = fields.List(fields.Str, many=True)


class ManualSource(Source):
    """Archer Remote."""

    __source_schema__ = ManualSrcSchema
    __credential_schema__ = ManualCredentialSchema
    __key__: str = "manual"
    _client = None

    def query(self, *args, **kwargs) -> List[str]:
        """Manual Users to Return.

        Returns:
            List[str]: [description]

        """
        self.logger.info("Returning Manual Users")

        return kwargs['users']
