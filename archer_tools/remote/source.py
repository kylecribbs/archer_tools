"""Base Source Abstract Class."""
import logging
from abc import ABCMeta, abstractmethod
from typing import List


class Source(metaclass=ABCMeta):
    """Generic Source abstract class.

    Attributes:
        __source_schema__ (marshmallow.Schema): Schema for Source yaml config
        __destination_schema__  (marshmallow.Schema): Schema for Destination
            yaml config
        __credential_schema__  (marshmallow.Schema): Schema for Source yaml
            config
        __key__  (str): Specify the unique key name for credentials yaml
            config

    """

    def __init__(self):
        """Initialize Source.

        Args:
            args: the rest of the arguments
            kwargs: See Kwargs

        Kwargs:
            kwargs: the rest of the keyword arguments

        """
        self.logger = logging.getLogger()

    @abstractmethod
    def query(self, *args, **kwargs) -> List[str]:
        """Query Stub.

        Returns:
            List[str]: List of oins.

        """
