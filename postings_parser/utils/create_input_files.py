import os
from postings_parser.utils.database_connector import Connector

PROJ_ROOT = os.getenv('PROJ_POSTINGS_PARSER_PATH')
print(PROJ_ROOT)
BATCH_SIZE = 100
OUT_FILE_PATH = PROJ_ROOT + "/postings_parser/input/"
out_file_name = "urls_batch_"


def main():
    rows = select_query()
    create_files(rows)

def create_files(rows):
    row_counter = 1
    file_counter = 0
    urls_list = []
    for row in rows:
        url = row[0] + "\n"
        urls_list.append(url)
        row_counter += 1
        if row_counter == BATCH_SIZE:
            flush_to_file(urls_list, file_counter)
            urls_list = []
            row_counter = 0
            file_counter += 1

    if row_counter != 0 and urls_list:
        flush_to_file(urls_list, file_counter)



def flush_to_file(urls_list, counter):
    full_path = OUT_FILE_PATH + out_file_name + str(counter) + ".txt"
    with open(full_path, "w") as f:
        f.writelines(urls_list)


def select_query():
    select_query = """
            SELECT url FROM site_urls
            WHERE url_domain='workday';
            """
    try:
        conn = Connector()
        connection = conn.get_conn()
        cursor = connection.cursor()
        cursor.execute(select_query)
        rows = cursor.fetchall()
        
    except Exception as e:
        print(f"An error occurred: {e}")
        connection.rollback()
    finally:
        conn.release_conn(connection)
    
    if rows:
        return rows
    else:
        raise RuntimeError(f"{select_query} did not return any rows")


if __name__ == "__main__":
    main()