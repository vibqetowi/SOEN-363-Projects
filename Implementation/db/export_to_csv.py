import os
import psycopg2
import csv

def extract_sql_data(csv_directory, db):
    try:
        cur = db.conn.cursor()
    except Exception as e:
        print("Error getting cursor to export to CSV:", e)
        exit()

    # make sure save directory for csvs exists
    os.makedirs(csv_directory, exist_ok=True)

    table_names = get_table_names(cur)

    for table_name in table_names:
        extract_single_table_data(cur, table_name, csv_directory)


def get_table_names(cur):
    try:

        query = """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
        """
        cur.execute(query)

        table_names = [row[0] for row in cur.fetchall()]

        return table_names

    except Exception as e:
        print(f"Error fetching table names: {e}")
        return []

def extract_single_table_data(cur, table_name, csv_directory):
    try:
        output_file = os.path.join(csv_directory, f"{table_name}.csv")

        with open(output_file, 'w') as file:
            copy_query = f"COPY {table_name} TO STDOUT WITH CSV HEADER"
            cur.copy_expert(copy_query, file)

        print(f"{table_name} data exported to {output_file}")

    except Exception as e:
        print(f"Error exporting table {table_name}: {e}")
