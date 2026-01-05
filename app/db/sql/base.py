import mariadb


class SQLBase:

    def _get_connection(self):
        try:
            connection = mariadb.connect(
                user='root',
                password='1234',
                host='localhost',
                port=3306,
                database='carebase'
            )
            return connection
        except mariadb.Error as e:
            print(f"Error connecting to MariaDB: {e}")
