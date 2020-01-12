"""Orchestrator for Archer Tools."""
import logging
from io import TextIOWrapper
from typing import Dict, List, Union, Set
from pkg_resources import iter_entry_points

import yaml
import coloredlogs

from archer_tools.config_schema import ConfigSchema
from archer_tools.errors import InvalidTypeError


class ArcherTools:
    """[summary].

    [description]

    Raises:
        InvalidTypeError: [description]

    Kwargs:
        _source_types (Dict): Properties.
        _destination_types (Dict): Properties
    Returns:
        [type]: [description]

    """

    _source_types: Dict = dict()
    _destination_types: Dict = dict()

    def __init__(self):
        """[summary].

        [description]
        """
        self.logger = logging.getLogger()

    @property
    def __source_types__(self) -> Dict:
        """Source data types available."""
        if not self._source_types:
            self._source_types = {}
            for entry_point in iter_entry_points("plugin_source_types"):
                remote = entry_point.load()
                self._source_types.update({remote.__key__: remote})

        return self._source_types

    @property
    def __destination_types__(self) -> Dict:
        """Destination data types available."""
        if not self._destination_types:
            self._destination_types = {}
            for entry_point in iter_entry_points("plugin_destination_types"):
                remote = entry_point.load()
                self._destination_types.update({remote.__key__: remote})

        return self._destination_types

    @staticmethod
    def read_config(filepath: Union[str, TextIOWrapper]) -> Dict:
        """[summary].

        [description]

        Args:
            filepath (Union[str, TextIOWrapper]): [description]

        Raises:
            InvalidTypeError: [description]

        Returns:
            Dict: [description]

        """
        if isinstance(filepath, str):
            with open(filepath, "r") as yaml_file:
                json_data = yaml.safe_load(yaml_file.read())
        elif isinstance(filepath, TextIOWrapper):
            json_data = yaml.safe_load(filepath.read())
        else:
            raise InvalidTypeError("Not Str or TextIOWrapper")

        configschema = ConfigSchema()
        config_data = configschema.load(configschema.dump(json_data))
        return config_data

    def setup_logging(self, logging_data):
        """Sets up logging from yaml."""
        self.logger.setLevel(level=getattr(logging, "DEBUG"))
        formatter = coloredlogs.ColoredFormatter(
            '%(asctime)s: %(levelname)s: %(message)s'
        )

        if logging_data.get("stdout"):
            loglevel = logging_data['stdout']['log_level'].upper()
            stream_handler = logging.StreamHandler()
            stream_handler.setLevel(getattr(logging, loglevel))
            stream_handler.setFormatter(formatter)
            self.logger.addHandler(stream_handler)

        if logging_data['output'].get("filepath"):
            loglevel = logging_data['output']['log_level'].upper()
            file_handler = logging.FileHandler(
                logging_data['output']['filepath'],
                mode="a"
            )
            file_handler.setFormatter(formatter)
            file_handler.setLevel(getattr(logging, loglevel))
            self.logger.addHandler(file_handler)

    def run(
        self,
        filepath: Union[str, TextIOWrapper],
        dry_run=False,
        ignore_source_failure=False
    ):
        """[summary].

        [description]

        Args:
            filepath (Union[str, TextIOWrapper]): [description]

        """
        data = self.read_config(filepath)
        self.logger.handlers = []

        logging_config = data['configuration']['logging']
        self.setup_logging(logging_config)

        for index, script in enumerate(data['script']):
            data = self.run_sources(
                script["source"],
                ignore_source_failure=ignore_source_failure
            )
            if dry_run:
                self.logger.info(
                    "Sources %s found the following users %s",
                    index, data
                )
            else:
                self.run_destinations(script["destination"], data=data)

    def run_sources(self, sources: List, ignore_source_failure=False) -> Set:
        """[summary].

        [description]

        Args:
            sources (List): [description]

        Returns:
            List: [description]

        """
        user_data: List[str] = list()
        for src in sources:
            for key in src.keys():
                kwargs = src[key]
                source_obj = self.__source_types__[key]()

                try:
                    source_data = source_obj.query(**kwargs)
                except Exception as e:
                    self.logger.error("Error in source %s", key)
                    self.logger.error("Reason: %s", e)
                    if ignore_source_failure:
                        continue
                    raise Exception("Source Failed!")

                self.logger.info(
                    "'%s' source found %s user(s).",
                    key.capitalize(),
                    len(source_data)
                )
                self.logger.debug("The users are: %s", source_data)
                user_data.extend(source_data)

        data = set(user_data)
        return data

    def run_destinations(self, destinations: List, **kwargs):
        """[summary].

        [description]

        Args:
            destinations (List): [description]
            user_oins (Set): [description]

        """
        for destination in destinations:
            for key in destination.keys():
                new_kwargs = destination[key]
                new_kwargs['from_sources'] = kwargs
                destination_obj = self.__destination_types__[key]()
                destination_obj.submit(**new_kwargs)
