"""Xacta Helper."""
import logging
from dataclasses import dataclass
from typing import List

from sqlalchemy import create_engine, MetaData, text
from sqlalchemy.engine.url import URL


@dataclass
class XactaData:
    """Class for executing Xacta SQL statements.

    Pass in the table or view you want to query and return results in a pandas
    dataframe.

    Args:
        host (str): The host for the database server.
        username (str): The username to conenct to the database server.
        password (str): The password to connect to the database server.
        database (str): The database name to connect to.
        query (dict): Any additional sql alchemy queries.
        port (int, optional): Defaults to 1433. The port for the database
                              server.
        drivername (str, optional): Defaults to 'mysql+pyodbc'. The driver name
                                    to connect to the database.

    """

    host: str
    username: str
    password: str
    database: str
    query: dict
    drivername: str = "mssql+pyodbc"
    port: int = 1433

    def __post_init__(self):
        """Post Init."""
        url = URL(**self.__dict__.copy())
        self.logger = logging.getLogger(__name__)
        self.logger.info("Attempting to log into Xacta SQL Database")
        self.engine = create_engine(url)
        self.metadata = MetaData(self.engine)

    def get_data(self, select_statement: str) -> List:
        """Get data from a select statement.

        Get data frome a sql select statement and returns as a dataframe.

        Args:
            select_statement (str): Specify the select statement to query.

        Returns:
            data (list): List of dicts. column: value for each row.

        """
        with self.engine.begin() as con:
            result = con.execute(text(select_statement))
            data = [dict(row.items()) for row in result]

        return data

    def get_stakeholders(self, stored_procedure=True):
        """Hardcoded SQL select statement to get all EXE accounts.

        Get all the users and their DNs that are active and tied to an EXE
        account

        Returns:
            data (pd.DataFrame): dataframe of all the users

        """
        select = """
        SELECT [login], fldr.name, REPLACE(REPLACE(acct.activeTill,
        '9223372036854775807', 'active'),'0', 'Inactive') "Account Status",
        [dn] FROM [Account] acct
        JOIN [Folder$SET_Account] fsa on fsa.account = acct.uuid
        JOIN [Folder] fldr on fldr.uuid = fsa.folder
        WHERE (acct.type = 'UserType.3' IR acct.type = 'UserType.2')
        AND (fldr.name NOT like '%-%' OR fldr.name like '1 - In%' OR fldr.name
        LIKE '4 - De%')
        ORDER BY login
        """

        if stored_procedure:
            select = "EXEC [xacta].[sp_USER_FOLDER_ASSIGNMENTS]"

        return self.get_data(select)
