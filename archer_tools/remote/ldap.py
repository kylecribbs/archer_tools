"""Ldap Plugin for Archer Tools."""
from typing import Dict, List

from marshmallow import Schema, fields, post_load, validate

from archer_tools.credential_schema import DefaultCredentialSchema
from archer_tools.remote.source import Source
from archer_tools.remote.libraries.ldap_helper import ADLdap, LdapPull


class LdapCredentialSchema(DefaultCredentialSchema):
    """Ldap Credential Schema."""

    username = fields.Str()
    password = fields.Str()
    use_ssl = fields.Bool(
        missing=True,
        default=True
    )
    base_dn = fields.Str()

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


class LdapGroupSchema(Schema):
    """Ldap Query Schema."""
    name = fields.Str(required=True)
    walk_groups = fields.Bool(missing=True, default=True)
    user_attribute = fields.Str(missing="CN", default="CN")


class LdapQuerySchema(Schema):
    """Ldap Query Schema."""

    groups = fields.Nested(LdapGroupSchema, required=True, many=True)
    kind = fields.Str(
        default="Active Directory",
        missing="Active Directory",
        validate=validate.OneOf(
            ["Active Directory", "ad", "OpenLdap", "ldap"]
        ),
    )


class LdapSchema(Schema):
    """Ldap Query Schema."""

    credential = fields.Str(required=True)
    query = fields.Nested(LdapQuerySchema, required=True)


class LdapSource(Source):
    """Ldap Source."""

    __source_schema__ = LdapSchema
    __destination_schema__ = LdapSchema
    __credential_schema__ = LdapCredentialSchema
    __key__: str = "ldap"
    _client = None

    @property
    def client(self):
        """Archer Client Property."""
        if not self._client:
            creds = self.adjust_creds(**self.kwargs)
            kind = self.kwargs['query']['kind'].lower()
            if "ad" in kind or "active" in kind:
                self._client = ADLdap(**creds)
            elif "ldap" in kind:
                self._client = LdapPull(**creds)
        return self._client

    @staticmethod
    def adjust_creds(**kwargs):
        """Adjust creds to the correct format for archer."""
        creds = kwargs['credential'].copy()
        creds['uri'] = creds.pop("hostname")
        return creds

    def query(self, *args, **kwargs) -> List[str]:
        """Query LDAP for OINs per group.

        Returns:
            List[str]: [description]

        """
        self.logger.info("Running query for Ldap")
        self.kwargs = kwargs

        users = []
        for group in self.kwargs['query']['groups']:
            users.extend(self.client.userlist_from_group(
                group['name'],
                attribute=group['user_attribute'],
                walk_groups=group['walk_groups']
            ))
        return users
