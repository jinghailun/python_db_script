import os
import time
import pymysql
import subprocess
from datetime import datetime
import configparser

config = configparser.ConfigParser()
config.read('config.ini')


def export_specific_tables_data(db_config, tables, output_file, truncateTables=False, close_foreign_key=False):
    conn = pymysql.connect(**db_config)
    cursor = conn.cursor()

    with open(output_file, 'w', encoding='utf-8') as f:
        if close_foreign_key:
            f.write(f"set foreign_key_checks = 0;\n")
        # create table if it not exist
        for table in tables:
            # export structure
            cursor.execute(f"SHOW CREATE TABLE {table}")
            create_table_sql = cursor.fetchone()[1]
            # CREATE TABLE IF NOT EXISTS
            create_table_sql = create_table_sql.replace("CREATE TABLE", "CREATE TABLE IF NOT EXISTS")
            f.write(f"{create_table_sql};\n\n")

        f.write(f"\n")
        f.write(f"\n")

        # truncate table
        if truncateTables:
            for table in tables:
                f.write(f"truncate {table};\n")

            f.write(f"\n")
            f.write(f"\n")

        for table in tables:
            print(f"export  {table} ...")

            cursor.execute(f"SHOW CREATE TABLE {table}")
            # export data
            cursor.execute(f"SELECT * FROM {table}")
            rows = cursor.fetchall()

            # column names
            cursor.execute(f"SHOW COLUMNS FROM {table}")
            columns_info = cursor.fetchall()
            column_names = [col[0] for col in columns_info]
            column_types = {col[0]: col[1] for col in columns_info}

            for row in rows:
                values = []
                for column_name, value in zip(column_names, row):
                    if value is None:
                        values.append('NULL')
                    elif 'bit' in column_types[column_name]:
                        #
                        # values.append(f"{value}")
                        values.append(str(int.from_bytes(value, byteorder='big')))
                    else:
                        #
                        values.append(f"'{str(value).replace('\'', '\'\'')}'")

                insert_sql = f"INSERT INTO {table} ({', '.join(column_names)}) VALUES ({', '.join(values)});"
                f.write(f"{insert_sql}\n")
            f.write(f"\n")
            f.write(f"\n")

        if foreign_key:
            f.write(f"set foreign_key_checks = 1;\n")
    cursor.close()
    conn.close()


execution = {
    'command': config.get('execution', 'command', fallback=None),
    'output_path': config.get('execution', 'output_path'),
}

if execution['command'] is None or len(execution['command']) == 0:
    print(f"")
    print(f"Command is not set in config.ini")
    print(f"")
    exit(-1)

command = execution['command']

out_folder = execution['output_path']
default_output_file = None
truncate_table = None
foreign_key = None
tables_str = None

if command and config.has_section(command):
    default_output_file = config.get(command, 'default_output_file', fallback=None)
    truncate_table = config.getboolean(command, 'truncate_table', fallback=False)
    foreign_key = config.getboolean(command, 'foreign_key', fallback=False)
    tables_str = config.get(command, 'tables_to_export', fallback=None)
else:
    print(f"")
    print(f"Command '{command}' is not configured or section [{command}] not found in config.ini.")
    print(f"")
    exit(-1)

db_config = {
    'user': config.get('mysql', 'user'),
    'password': config.get('mysql', 'password'),
    'host': config.get('mysql', 'host'),
    'database': config.get('mysql', 'database'),
}

mysqldump_path = config.get('execution', 'mysqldump', fallback=None)

if __name__ == "__main__":
    print(f"")
    print(f"-------------------------------------------------")
    print(f"host            :  {db_config['host']} ")
    print(f"name            :  {db_config['database']} ")
    print(f"mysqldump       :  {mysqldump_path} ")
    print(f"truncate_table  :  {truncate_table} ")
    print(f"foreign_key     :  {foreign_key} ")
    print(f"-------------------------------------------------")
    print(f"")

    if tables_str is None:
        print(f"Failed to dump sql file. tables content is empty ")
        exit(-1)

    tables_list = [table.strip() for table in tables_str.split(',') if table.strip()]
    if len(tables_list) == 0:
        print(f"Failed to dump sql file. table list is empty ")
        exit(-1)

    # for table in tables_list:
    #     print(f"Start dumping table {table}")
    # print(f"")

    current_datetime = datetime.now().strftime("%Y%m%d%H%M%S")
    output_file = f"{out_folder}/{default_output_file}_{db_config['database']}_{current_datetime}.sql"
    try:
        print(f"start export tables in database [ {db_config['database']} ]")
        os.makedirs(out_folder, exist_ok=True)
        start_time = time.time()
        print(f"")
        export_specific_tables_data(db_config, tables_list, output_file, truncate_table, foreign_key)
        end_time = time.time()
        print(f"")
        print(f"-------------------------------------------------")
        print(f"                 Successfully")
        print(f"-------------------------------------------------")
        print(f"duration        :  {end_time - start_time:.2f} s ")
        print(f"output_file     :  {output_file} ")
        print(f"-------------------------------------------------")
        print(f"")
    except Exception as e:
        print(f"")
        print(f"-------------------------------------------------")
        print(f"                 Failed")
        print(f"-------------------------------------------------")
        print(f"An error occurred:  {e} ")
        print(f"-------------------------------------------------")
        print(f"")
