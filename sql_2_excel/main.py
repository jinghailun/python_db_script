import os
import time
import configparser
import pandas as pd
from sqlalchemy import create_engine, text
from datetime import datetime
import argparse

config = configparser.ConfigParser()
config.read('config.ini')


def export_summary_data_report(db_config, sql_file_path, output_file, condition=None, replace_area=[]):
    # open sql file
    with open(sql_file_path, 'r', encoding='utf-8') as file:  # Choosing utf 8 encoding
        sql_query = file.read()

    if condition is not None and condition != '':
        sql_query = sql_query.replace('{{condition}}', condition)

    if len(replace_area) > 0:
        for i, area in enumerate(replace_area, start=1):
            sql_query = sql_query.replace(f'{{{{replace{i}}}}}', area)

    # connect db
    connection_str = f"mysql+pymysql://{db_config['user']}:{db_config['password']}@{db_config['host']}/{db_config['database']}"
    engine = create_engine(connection_str)

    # execute sql
    try:
        # df = pd.read_sql_query(text(sql_query), engine, params=query_params)
        df = pd.read_sql_query(text(sql_query), engine)
    except Exception as e:
        # print(f"An error occurred while executing the SQL query: {e}")
        print(f"")
        print(f"An error occurred while executing the SQL query:")
        print(f"{e}")
        return -1

    # generate sql
    # df.to_excel(output_file, index=False, engine='openpyxl')

    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name="Sheet1", index=False)
        # ✅ Adjust column width automatically
        workbook = writer.book
        worksheet = writer.sheets["Sheet1"]

        for col in worksheet.columns:
            max_length = 0
            col_letter = col[0].column_letter
            for cell in col:
                try:
                    if cell.value:
                        max_length = max(max_length, len(str(cell.value)))
                except:
                    pass
            worksheet.column_dimensions[col_letter].width = max_length + 2  # increase padding

    # print(f"✅Create excel file successfully. file  : {output_file}")
    return 0


parser = argparse.ArgumentParser(description='Specify configuration file.')
parser.add_argument('--command', type=str, required=False, help='')
args = parser.parse_args()

print(f"input command: {args.command}")

execution = {
    'input_path': config.get('execution', 'input_path'),
    'output_path': config.get('execution', 'output_path'),
}
command = args.command
if command is None:
    defaultCommand = config.get('execution', 'command', fallback=None)
    # print(defaultCommand)
    # print(type(defaultCommand))
    if defaultCommand is None or defaultCommand == '':
        print(f"")
        print(f"Command is not set in config.ini")
        print(f"")
        exit(-1)

    command = defaultCommand

summary_config = None
database = ''

print(f"current command: {command}")
if command and config.has_section(command):
    summary_config = {
        'excel_file': config.get(command, 'excel_file'),
        'sql_scrip': config.get(command, 'sql_scrip'),
        'condition': config.get(command, 'condition', fallback=None)
    }
    database = config.get(command, 'database', fallback=None)
else:
    print(f"")
    print(f"Command '{command}' is not configured or section [{command}] not found in config.ini.")
    print(f"")
    exit(-1)

db_config = {
    'user': config.get('mysql', 'user'),
    'password': config.get('mysql', 'password'),
    'host': config.get('mysql', 'host'),
    'database': database or config.get('mysql', 'database')
}

if __name__ == "__main__":
    print(f"")
    print(f"-------------------------------------------------")
    print(f"host            :  {db_config['host']} ")
    print(f"db              :  {db_config['database']} ")
    print(f"")
    print(f"command         :  {command} ")
    print(f"sql             :  {summary_config['sql_scrip']} ")
    print(f"excel           :  {summary_config['excel_file']} ")
    print(f"-------------------------------------------------")
    print(f"")

    # Get and format the current time
    # Retrieve and format the current date and time
    current_datetime = datetime.now().strftime("%Y%m%d%H%M%S")

    sql_file_path = f"{execution['input_path']}/{summary_config['sql_scrip']}"
    if not os.path.exists(sql_file_path):
        # print(f"The sql file {sql_file_path} does not exist!")
        print(f"")
        print(f"-------------------------------------------------")
        print(f"Error           :  The sql file {sql_file_path} does not exist!")
        print(f"-------------------------------------------------")
        print(f"")
        exit(-1)

    default_output_file = db_config['database'] + "_" + summary_config['excel_file']
    out_folder = execution['output_path']

    result_file_name = f"{default_output_file}_{current_datetime}.xlsx"
    output_file = f"{out_folder}/{result_file_name}"
    # print(f"The result file will be generated. file :  {default_output_file} ")

    print(f"")

    replace_list = []
    replace_content = config.get(command, 'replace_content', fallback=None)
    if replace_content is not None:
        replace_list = [table.strip() for table in replace_content.split(',') if table.strip()]
        if len(replace_list) == 0:
            print(f"No content need be replaced ")

    try:
        current_dir = os.getcwd()
        output_path = os.path.join(current_dir, out_folder)
        print(f"Start dumping SQL tables from database...")
        print(f"database        :  {db_config['database']} ")
        print(f"output_path     :  {output_path} ")
        print(f"output_file     :  {result_file_name} ")
        os.makedirs(out_folder, exist_ok=True)
        start_time = time.time()
        export_result = export_summary_data_report(db_config, sql_file_path, output_file, summary_config['condition'],
                                                   replace_list)
        end_time = time.time()
        if export_result == 0:
            print(f"")
            print(f"-------------------------------------------------")
            print(f"                 Successfully")
            print(f"-------------------------------------------------")
            print(f"duration        :  {end_time - start_time:.2f} s ")
            print(f"-------------------------------------------------")
            print(f"")
            exit(0)
        else:
            # print(f"The sql script has been generated with error!")

            print(f"")
            print(f"-------------------------------------------------")
            print(f"                 Failed")
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

    print(f"")
    print(f"")
    print(f"")
