"""Base Destination Abstract Class."""
import logging
from abc import ABCMeta, abstractmethod


class Destination(metaclass=ABCMeta):
    """Generic Source abstract class."""

    def __init__(self):
        """Initialize Source.

        Args:
            args: the rest of the arguments
            kwargs: See Kwargs

        Kwargs:
            kwargs: the rest of the keyword arguments

        """
        self.logger = logging.getLogger()
        # self.destination = self.__destination_schema__().dump(kwargs)

    @abstractmethod
    def submit(self, *args, **kwargs):
        """Submit Stub.

        Args:
            args: Any args passed.
            kwargs: Any kwargs passed.

        """
