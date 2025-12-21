import mariadb


class SQLBase:

    # TODO: Change credentials
    # TODO: Make sure name hospital_db is correct

    def _get_connection(self):
        try:
            connection = mariadb.connect(
                user='admin',
                password='1234',
                host='mariadb',
                port=3306,
                database='hospital_db'
            )
            return connection
        except mariadb.Error as e:
            print(f"Error connecting to MariaDB: {e}")
