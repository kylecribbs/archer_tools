"""Ldap helper."""
import logging
from getpass import getpass
from typing import Iterable, Union, Dict, Optional

from ldap3 import Connection, Server


class LdapHelper:
    """LdapHelper class for common LDAP properities.

    Attributes:
        connection (ldap3.Connection): Yeah...
        server (ldap3.Server): Yeah...

    """

    def __init__(
        self,
        uri: str,
        use_ssl: bool = True,
        base_dn: Optional[str] = None,
        return_attr: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None
    ):
        """Init."""
        self.uri = uri
        self.return_attr = return_attr
        self.base_dn = base_dn
        if not self.base_dn:
            self.base_dn = self._base
            logging.warning("No base DN provided using %s", self.base_dn)
        self.use_ssl = use_ssl
        self.username = username
        self.password = password

        self._conn_args = self._super_conn_args.copy()
        if self.username:
            password = self.password or getpass()
            self._conn_args.update(dict(user=self.username, password=password))
        if self.use_ssl:
            self._server_args = dict(use_ssl=self.use_ssl)
        else:
            logging.warning("You are using an unsecure protocol!")
        self.password = None

    @property
    def _base(self) -> str:
        """Property decorated function: WYSIWYG."""
        return "DC=%s" % ",DC=".join(self.uri.split("."))

    @property
    def connection(self) -> Connection:
        """Property decorated function: WYSIWYG."""
        if not self._connection:
            self._connection = Connection(self.server, **self._conn_args)
        return self._connection

    @property
    def server(self) -> Server:
        """Property decorated function: WYSIWYG."""
        if not self._server:
            self._server = Server(self.uri, **self._server_args)
        return self._server

    def get_group_by_name(self, group_name: str) -> str:
        """Return the full dn for a group.

        Arguments:
            group_name: Group name to match against

        Returns:
            str: Full dn for the group

        """
        self.connection.search(
            self.base_dn, search_filter=f"(cn={group_name})", attributes=["cn"]
        )
        entries = self.connection.entries
        entry_dn = ""
        if len(entries) > 1:
            options = [entry.cn.value for entry in entries]
            logging.warning(
                "Multiple groups returned, please be more specific"
            )
            logging.warning("Options: %s", options)
        elif not entries:
            logging.warning("Unable to find the group by cn: %s", group_name)
        else:
            entry_dn = entries[0].entry_dn
        return entry_dn

    def userlist_from_group(
            self,
            group_name: str,
            attribute: str = "employeeID",
            walk_groups: bool = True,
            object_class: str = "user"
    ) -> list:
        """Return a list of user attributes for all users in a group.

        Arguments:
            group_name: Will be passed to self.get_group_by_name

        Keyword Arguments:
            attribute: The attribute from LDAP to pull
            walk_groups: Walk all users in subgroups

        Returns:
            list: List of users by `attribute` that are in `group`

        """
        group_dn = self.get_group_by_name(group_name)
        if walk_groups:
            all_groups = self._walk_groups(group_dn)
            all_groups.append(group_dn)
            users = []
            for group in all_groups:
                users.extend(
                    self.users_in_group(
                        group,
                        object_class=object_class,
                        attributes=[attribute]
                    )
                )
            del self._covered
        else:
            users = self.users_in_group(group_dn, attributes=[attribute])
        return [getattr(entry, attribute).value for entry in users]

    def users_in_group(
        self,
        group_dn: str,
        base_dn: Union[str, None] = None,
        object_class: str = "user",
        attributes: Iterable = ("employeeID")
    ) -> list:
        """Return a list of user attributes for all users in a group.

        Args:
            group_dn: Full dn of the group to pull users from

        Keyword Arguments:
            base_dn: Base search DN in AD
            attributes: The attrubutes to pull from the users

        Returns:
            list: User objects from AD

        """
        if base_dn is None:
            base_dn = self.base_dn
        search_filter = f"(&(objectClass={object_class})(memberof={group_dn}))"
        self.connection.search(
            base_dn, search_filter=search_filter, attributes=attributes
        )
        return self.connection.entries

    def _walk_groups(self, entry_dn):
        """For Internal use."""
        self.connection.search(
            f"{self._base}",
            search_filter=f"(&(memberOf={entry_dn})(objectClass=group))",
            attributes=["member"],
        )
        entries = self.connection.entries
        self._covered = self._covered if hasattr(self, "_covered") else []
        if entries:
            groups = []
            for entry in entries:
                entry_dn = entry.entry_dn
                entry_dn = entry_dn.replace("(", "\\28")
                entry_dn = entry_dn.replace(")", "\\29")
                if entry not in self._covered:
                    self._covered.append(entry)
                    groups.append(entry_dn)
            for gdn in groups:
                groups.extend(self._walk_groups(gdn))
            return groups
        else:
            return []

    _super_conn_args: Dict = dict(auto_bind=True)
    _connection: Optional[Connection] = None
    _server_args: Dict = {}
    _server: Optional[Server] = None
