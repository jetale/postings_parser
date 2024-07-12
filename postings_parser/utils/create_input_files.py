import argparse
import math
import os

from postings_parser.utils.database_connector import Connector

PROJ_ROOT = os.getenv("PROJ_POSTINGS_PARSER_PATH")
print(PROJ_ROOT)

OUT_FILE_PATH = PROJ_ROOT + "/postings_parser/input/"
out_file_name = "urls_batch_"


def main(max_files):
    rows = select_query()
    url_count = len(rows)
    batch_size = math.ceil(url_count / max_files)
    create_files(rows, batch_size)


def create_files(rows, batch_size):
    row_counter = 1
    file_counter = 0
    urls_list = []
    for row in rows:
        url = row[0] + "\n"
        urls_list.append(url)
        row_counter += 1
        if row_counter == batch_size:
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
    rows = Connector().execute_select_query(select_query)

    if rows:
        return rows
    else:
        raise RuntimeError(f"{select_query} did not return any rows")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="File Generator")
    parser.add_argument(
        "--num_files", type=int, help="Max number of files to be generated"
    )
    args = parser.parse_args()

    if args.num_files:
        main(max_files=args.num_files)
    else:
        print("Please specify the number of files to process using --num_file option.")
