"""Xacta Plugin for Archer Tools."""
from typing import Dict, List

from marshmallow import Schema, fields, post_load, validate

from archer_tools.credential_schema import DefaultCredentialSchema
from archer_tools.remote.source import Source
from archer_tools.remote.libraries.xacta_helper import XactaData


class XactaQueryCredentialSchema(Schema):
    """Xacta Query Credential Schema."""

    driver = fields.Str(required=True)


class XactaCredentialSchema(DefaultCredentialSchema):
    """Xacta Credential Schema."""

    database = fields.Str(required=True)
    username = fields.Str(required=True)
    password = fields.Str(required=True)
    query = fields.Nested(XactaQueryCredentialSchema, required=True)
    drivername = fields.String(default="mssql+pyodbc")
    port = fields.Int(default=1433)

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


class XactaQuerySchema(Schema):
    """Xacta Query Schema."""

    group = fields.List(fields.Str(), required=True, many=True)
    account_status = fields.Str(
        default="active", validate=validate.OneOf(["active", "inactive"])
    )
    is_exe = fields.Bool(default=True)


class XactaSchema(Schema):
    """Xacta Schema."""

    credential = fields.Str(required=True)
    query = fields.Nested(XactaQuerySchema, required=True)


class XactaSource(Source):
    """Xacta Source."""

    __source_schema__ = XactaSchema
    __destination_schema__ = XactaSchema
    __credential_schema__ = XactaCredentialSchema
    __key__: str = "xacta"

    def query(self) -> List[str]:
        """Query XACTA for OINs per TODO - fill in here.

        Returns:
            List[str]: [description]

        """
        self.logger.error("Running query for Xacta")
        self.data["credential"]["host"] = self.data["credential"].pop(
            "hostname"
        )
        group = self.data["query"]["group"]
        client = XactaData(**self.data["credential"])
        data = client.get_stakeholders(group)
        is_exe = self.data["query"]["is_exe"]
        user_dns = [
            user["dn"]
            for user in data
            if user["name"] in group
            and self.is_exe_user(user["login"], is_exe)
        ]

        return user_dns

    def is_exe_user(self, login: str, is_exe: bool) -> bool:
        """Determine if the user is an EXE user and exe is enabled.

        Args:
            login (str): username of the user to check
            is_exe (bool): is exe enabled for the query?

        Returns:
            bool: if the user is an EXE user and exe is enabled in the query

        """
        if is_exe and login.endswith("_EXE"):
            return True
        return False
