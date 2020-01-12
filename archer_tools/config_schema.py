"""Default Schema for Group Tool."""
from itertools import chain
from typing import Dict, List
from pkg_resources import iter_entry_points, EntryPoint

from marshmallow import Schema, fields, post_load, validate


class CredentialSchema(Schema):
    """Credential Schema, Inherits from Subclasses."""

    def __init__(self, *args, **kwargs):
        """Initialize Credentials Schema.

        Args:
            args: See marshmallow.Schema
            kwargs: See Kwargs

        Kwargs:
            kwargs: See marshmallow.Schema

        """
        super().__init__(*args, **kwargs)

        source = iter_entry_points("plugin_source_types")
        destination = iter_entry_points("plugin_destination_types")

        remotes = map(EntryPoint.load, chain(source, destination))
        additional_fields = {
            remote.__key__: fields.Nested(
                remote.__credential_schema__, many=True
            )
            for remote in remotes
        }

        self.declared_fields.update(additional_fields)
        self.fields.update(additional_fields)
        self.load_fields.update(additional_fields)
        self.dump_fields.update(additional_fields)


class SourceSchema(Schema):
    """Source Schema, Inherits from Subclasses."""

    def __init__(self, *args, **kwargs):
        """Initialize Source Schema.

        Args:
            args: See marshmallow.Schema
            kwargs: See Kwargs

        Kwargs:
            kwargs: See marshmallow.Schema

        """
        super().__init__(*args, **kwargs)

        source = iter_entry_points("plugin_source_types")

        remotes = map(EntryPoint.load, source)
        additional_fields = {
            remote.__key__: fields.Nested(remote.__source_schema__)
            for remote in remotes
        }

        self.declared_fields.update(additional_fields)
        self.fields.update(additional_fields)
        self.load_fields.update(additional_fields)
        self.dump_fields.update(additional_fields)


class DestinationSchema(Schema):
    """Destination Schema, Inherits from Subclasses."""

    def __init__(self, *args, **kwargs):
        """Initialize Destination Schema.

        Args:
            args: See marshmallow.Schema
            kwargs: See Kwargs

        Kwargs:
            kwargs: See marshmallow.Schema

        """
        super().__init__(*args, **kwargs)

        destination = iter_entry_points("plugin_destination_types")

        remotes = map(EntryPoint.load, destination)
        additional_fields = {
            remote.__key__: fields.Nested(remote.__destination_schema__)
            for remote in remotes
        }

        self.declared_fields.update(additional_fields)
        self.fields.update(additional_fields)
        self.load_fields.update(additional_fields)
        self.dump_fields.update(additional_fields)


class ScriptSchema(Schema):
    """Script Schema."""

    source = fields.Nested(SourceSchema, required=True, many=True)
    destination = fields.Nested(DestinationSchema, required=True, many=True)


class StdoutSchema(Schema):
    """Standard Out Schema."""

    log_level = fields.Str(
        validate=validate.OneOf(
            ["debug", "info", "warning", "error", "critical"]
        ),
        default="warning",
        missing="warning"
    )


class OutputSchema(Schema):
    """Output Schema."""

    filepath = fields.Str()
    log_level = fields.Str(
        validate=validate.OneOf(
            ["debug", "info", "warning", "error", "critical"]
        ),
        default="info",
        missing="info"
    )


class LoggingSchema(Schema):
    """Logging Schema."""
    stdout = fields.Nested(
        StdoutSchema,
        missing=StdoutSchema().dump(StdoutSchema()),
        default=StdoutSchema().dump(StdoutSchema())
    )
    output = fields.Nested(
        OutputSchema,
        missing=OutputSchema().dump(OutputSchema()),
        default=OutputSchema().dump(OutputSchema())
    )


class ConfigurationSchema(Schema):
    """Configuration Schema."""
    logging = fields.Nested(
        LoggingSchema,
        missing=LoggingSchema().dump(LoggingSchema()),
        default=LoggingSchema().dump(LoggingSchema())
    )


class ConfigSchema(Schema):
    """Config Schema."""

    credentials = fields.Nested(CredentialSchema, required=True)
    script = fields.Nested(ScriptSchema, required=True, many=True)
    configuration = fields.Nested(
        ConfigurationSchema,
        missing=ConfigurationSchema().dump(ConfigurationSchema())
    )

    @post_load()
    def merge_credentials(self, data: Dict, **kwargs) -> List[Dict]:
        """[summary].

        [description]

        Args:
            data (Dict): [description]
            kwargs: See Kwargs

        Kwargs:
            Kwargs: Catch all from marshmallow.post_load()

        Returns:
            List[Dict]: [description]

        """
        credentials: Dict = dict()
        for credential in data["credentials"]:
            for cred in data["credentials"][credential]:
                credentials.update(cred)
        new_data = []
        for script in data["script"]:
            temp: Dict = dict(source=[], destination=[])
            for source in script["source"]:
                for cred in source:
                    source[cred]["credential"] = credentials[
                        source[cred]["credential"]
                    ]
                temp["source"].append(source)
            for dest in script["destination"]:
                for cred in dest:
                    dest[cred]["credential"] = credentials[
                        dest[cred]["credential"]
                    ]
                temp["destination"].append(dest)
            new_data.append(temp)
        return_data = {
            "configuration": data["configuration"],
            "script": new_data
        }
        return return_data
