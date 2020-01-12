"""Archer Plugin for Archer Tools."""
from os import path
from typing import Dict, List

from marshmallow import (
    Schema, ValidationError, fields, post_load, pre_load, validates_schema
)
from pyarcher import Archer

from archer_tools.credential_schema import DefaultCredentialSchema
from archer_tools.remote.destination import Destination
from archer_tools.remote.source import Source


class ArcherCredentialSchema(DefaultCredentialSchema):
    """Archer Credential Schema."""

    username = fields.Str()
    password = fields.Str()
    instance_name = fields.Str(required=True)
    user_domain = fields.Str()
    cert = fields.Str()
    key = fields.Str()

    @pre_load()
    def check_cert(self, data: Dict, **kwargs) -> Dict:
        """Validate Cert and Key have a valid path.

        Args:
            data (Dict): Data from marshmallow
            kwargs: See Kwargs

        Kwargs:
            kwargs: Kwargs from marshmallow.Schema

        Raises:
            ValidationError: When Cert or Key file path do not exist

        Returns:
            Dict: returns data unchanged.

        """
        if data.get("cert") or data.get("key"):
            if not path.exists(data["cert"]):
                raise ValidationError("Certificate path is invalid.")
            if not path.exists(data["key"]):
                raise ValidationError("Key path is invalid.")
        return data

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


class ArcherSrcGroupSchema(Schema):
    """Archer Group Schema."""

    name = fields.Str()
    obj_id = fields.Int()
    recurse_groups = fields.Bool(default=True, missing=True)

    @validates_schema
    def check_required(self, data: Dict, **kwargs) -> Dict:
        """Validate if name or obj_id is present.

        Args:
            data (Dict): Data from marshmallow

        Raises:
            ValidationError: When either both or none of the name/obj_id
            are present

        Returns:
            Dict: returns data unchanged
        """
        if data.get("name") and data.get("obj_id"):
            raise ValidationError(
                "Only name or obj_id need to be specified. Not both!"
            )
        if not data.get("name") and not data.get("obj_id"):
            raise ValidationError(
                "You must specify a group name or an obj_id."
            )
        return data


class ArcherDestGroupSchema(Schema):
    """Archer Group Schema."""

    name = fields.Str()
    obj_id = fields.Int()

    @validates_schema
    def check_required(self, data: Dict, **kwargs) -> Dict:
        """Validate if name or obj_id is present.

        Args:
            data (Dict): Data from marshmallow

        Raises:
            ValidationError: When either both or none of the name/obj_id
            are present

        Returns:
            Dict: returns data unchanged
        """
        if data.get("name") and data.get("obj_id"):
            raise ValidationError(
                "Only name or obj_id need to be specified. Not both!"
            )
        if not data.get("name") and not data.get("obj_id"):
            raise ValidationError(
                "You must specify a group name or an obj_id."
            )
        return data


class ArcherSrcQuerySchema(Schema):
    """Archer Query Schema."""

    group = fields.Nested(ArcherSrcGroupSchema, many=True, required=True)


class ArcherMissingUserSchema(Schema):
    """Archer Missing User Schema."""

    upper = fields.Bool(default=False, missing=False)
    lower = fields.Bool(default=False, missing=False)


class ArcherDestQuerySchema(Schema):
    """Archer Query Schema."""

    group = fields.Nested(ArcherDestGroupSchema, many=True, required=True)
    user_missing = fields.Nested(
        ArcherMissingUserSchema,
        default={},
        missing={}
    )


class ArcherDestSchema(Schema):
    """Archer Schema."""

    credential = fields.Str(required=True)
    query = fields.Nested(ArcherDestQuerySchema, required=True)


class ArcherSrcSchema(Schema):
    """Archer Schema."""

    credential = fields.Str(required=True)
    query = fields.Nested(ArcherSrcQuerySchema, required=True)


class ArcherSourceAndDestination(Destination, Source):
    """Archer Remote."""

    __source_schema__ = ArcherSrcSchema
    __destination_schema__ = ArcherDestSchema
    __credential_schema__ = ArcherCredentialSchema
    __key__: str = "archer"
    _client = None

    @staticmethod
    def adjust_creds(**kwargs):
        """Adjust creds to the correct format for archer."""
        creds = kwargs['credential'].copy()
        creds['url'] = creds.pop("hostname")
        return creds

    @property
    def client(self):
        """Archer Client Property."""
        if not self._client:
            creds = self.adjust_creds(**self.kwargs)
            self._client = Archer(**creds)
        return self._client

    def query(self, *args, **kwargs) -> List[str]:
        """Query Archer for OINs per group.

        Returns:
            List[str]: [description]

        """
        self.logger.info("Running query for Archer")
        self.kwargs = kwargs

        resp = self.client.login().json()
        if not resp['IsSuccessful']:
            self.logger.error("Unable to login to Archer")
            return []

        for groups in kwargs['query']['group']:
            try:
                groups = [self.client.get_group(groups['obj_id'])]

            except KeyError:
                groups = self.client.query_groups(params={
                    "filter": f"Name eq '{groups['name']}'"
                })
            users = list()
            for group in groups:
                # TODO: Change to check if recurse or not
                for member in group.all_members:
                    users.append(member.metadata['UserName'])
        return users

    def submit_groups(self):
        """Submit Group Logic."""
        groups = []
        for group in self.kwargs['query']['group']:
            group_name = group.get("name")
            group_id = group.get("obj_id")
            group_obj = None

            if group_id:
                group_obj = self.client.get_group(group_id)

            if group_name:
                params = {"filter": f"Name eq '{group_name}'"}
                query = self.client.query_groups(params)
                try:
                    group_obj = query[0]
                    group_id = query[0].obj_id
                    if len(query) > 1:
                        self.logger.info(
                            "Found %s Users that match %s,",
                            len(query),
                            group_name
                        )
                        self.logger.info(
                            "Getting first one with the obj id of %s.",
                            group_id
                        )
                except IndexError:
                    self.logger.error(
                        "Group '%s' does not exist!",
                        group_name
                    )
                    continue

            if not group_obj.exists:
                self.logger.error(
                    "Group ID: '%s' does not exist!",
                    group_obj.obj_id
                )
                continue
            groups.append(group_obj)
        return groups

    def submit_users(self, override_user_list=None):
        """Submit user logic."""
        users = []
        failed_users = []

        user_list = self.kwargs['from_sources']['data']
        if override_user_list:
            user_list = override_user_list

        for user in user_list:
            params = {"filter": f"UserName eq '{user}'"}
            query = self.client.query_users(params)
            try:
                user_obj = query[0]
                user_id = query[0].obj_id
                if len(query) > 1:
                    self.logger.info(
                        "Found %s Users that match %s, getting the first one "
                        "with the obj id of %s",
                        len(query),
                        user,
                        user_id
                    )
            except IndexError:
                self.logger.error("User '%s' does not exist!", user)
                failed_users.append(user)
                continue

            if not user_obj.exists:
                self.logger.error(
                    "User ID: '%s' does not exist!", user_obj.obj_id
                )
                continue
            users.append(user_obj)
        return users, failed_users

    def submit(self, *args, **kwargs):
        """Submit OINs to destination.

        Args:
            args: Any optional args.
            kwargs: See Kwargs

        Kwargs:
            kwargs: Any option kwargs.

        """
        self.logger.info("Running submit for Archer")
        self.kwargs = kwargs

        upper = kwargs['query']['user_missing']['upper']
        lower = kwargs['query']['user_missing']['lower']

        resp = self.client.login().json()
        if not resp['IsSuccessful']:
            self.logger.error("Unable to login to Archer")
            return []

        users, failed_users = self.submit_users()

        if upper and failed_users:
            self.logger.info("Running uppercase on failed users")
            failed_users = [user.upper() for user in failed_users]
            more_users, failed_users = self.submit_users(
                override_user_list=failed_users
            )
            users.extend(more_users)

        if lower and failed_users:
            self.logger.info("Running lowercase on failed users")
            failed_users = [user.lower() for user in failed_users]
            more_users, failed_users = self.submit_users(
                override_user_list=failed_users
            )
            users.extend(more_users)

        groups = self.submit_groups()
        for group in groups:
            users_text = [str(user.metadata['UserName']) for user in users]
            resp = group.update_group(child_users=users)
            self.logger.debug(resp.json())

            self.logger.info(
                "Successfully added '%s' to the group '%s'",
                users_text,
                group.metadata['Name']
            )
