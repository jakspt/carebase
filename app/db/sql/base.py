import mariadb


class SQLBase:
    def _get_connection(self):
        try:
            connection = mariadb.connect(
                user="root",
                password="1234",
                host="mariadb",
                port=3306,
                database="carebase",
            )
            connection.enable_auto_commit = False
            return connection
        except mariadb.Error as e:
            raise Exception(f"Error connecting to MariaDB, Reason: {e}")
