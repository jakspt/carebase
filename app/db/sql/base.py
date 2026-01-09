import mariadb


class SQLBase:
    def _get_connection(self):
        try:
            connection = mariadb.connect(
                user="root",
                password="1234",
                host="127.0.0.1",
                port=3306,
                database="carebase",
            )
            return connection
        except mariadb.Error as e:
            raise Exception(f"Error connecting to MariaDB, Reason: {e}")
