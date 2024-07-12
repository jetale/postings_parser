from postings_parser.utils.database_connector import Connector


def main():
    conn = Connector()
    insert_daily_stats(conn)


def insert_daily_stats(conn):
    count_query = """
                SELECT insert_today_counts();
                """
    conn.execute_function(count_query)


if __name__ == "__main__":
    main()
