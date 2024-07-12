from postings_parser.utils.database_connector import Connector

urls = []
with open("urls.txt", "r") as f:
    for line in f:
        # aline = line.replace("job/", "").replace("\n","")
        urls.append((line, "workday"))


insert_query = """
                    INSERT INTO site_urls(url,
                                        url_domain )
                    VALUES (%s, %s)
                    ON CONFLICT (url) DO NOTHING;
                    """
try:
    conn = Connector()
    connection = conn.get_conn()
    cursor = connection.cursor()
    cursor.executemany(insert_query, urls)
    connection.commit()
except Exception as e:
    print(f"An error occurred: {e}")
    connection.rollback()
finally:
    conn.release_conn(connection)
