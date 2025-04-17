import os
import time
import configparser
import subprocess
import argparse

config = configparser.ConfigParser()
config.read('config.ini')

def import_sql_file_2_database(mysql_path, db_config, backup_file, execute_sql_file):
    try:
        host = db_config['host']
        user = db_config['user']
        password = db_config['password']
        db_name = db_config['database']

        create_db_command = [
            mysql_path,
            '-h', host,
            '-u', user,
            f'-p{password}',
            '-e', f'CREATE DATABASE IF NOT EXISTS {db_name};'
        ]
        result = subprocess.run(create_db_command, stderr=subprocess.PIPE, text=True)
        if result.returncode != 0:
            print(f"Error creating database {db_name}: {result.stderr}")
            return -1

        restore_command = [
            mysql_path,
            '-h', host,
            '-u', user,
            f'-p{password}',
            db_name
        ]
        with open(backup_file, 'r') as f:
            result = subprocess.run(restore_command, stdin=f, stderr=subprocess.PIPE, text=True)
            if result.returncode != 0:
                print(f"Error restoring database {db_name}: {result.stderr}")
            else:
                print(f"Database {db_name} restored successfully from {backup_file}")

        if execute_sql_file and db_config['host'] != '':
            execute_sql_command = [
                mysql_path,
                '-h', host,
                '-u', user,
                f'-p{password}',
                db_name
            ]
            with open(execute_sql_file, 'r') as f:
                result = subprocess.run(execute_sql_command, stdin=f, stderr=subprocess.PIPE, text=True)
                if result.returncode != 0:
                    print(f"Error executing SQL file {execute_sql_file} on database {db_name}: {result.stderr}")
                else:
                    print(f"SQL file [ {execute_sql_file} ] executed successfully on database {db_name}")
    except Exception as e:
        print(f"An error occurred: {e}")
        return -2

    return 0


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Specify configuration file.')
    parser.add_argument('--database', type=str, required=False, help='')
    parser.add_argument('--backup_file', type=str, required=False, help='')
    parser.add_argument('--sql_script', type=str, required=False, help='')
    args = parser.parse_args()

    print(f"database            :  {args.database} ")
    print(f"backup_file         :  {args.backup_file} ")
    print(f"sql_script          :  {args.sql_script} ")

    db_config = {
        'user': config.get('mysql', 'user'),
        'password': config.get('mysql', 'password'),
        'host': config.get('mysql', 'host'),
        'database': args.database,
        'mysql_path': config.get('mysql', 'mysql')
    }

    backup_file = args.backup_file
    sql_script = args.sql_script
    if backup_file is None or backup_file == '':
        execution = {
            'command': config.get('execution', 'command', fallback=None),
        }

        if execution['command'] is None or execution['command'] == '':
            print(f"")
            print(f"Command is not set in config.ini")
            print(f"")
            exit(-1)

        command = execution['command']
        if command and config.has_section(command):
            backup_file = config.get(command, 'backup_file')
            sql_script = config.get(command, 'sql_script')
        else:
            print(f"")
            print(f"Command '{command}' is not configured or section [{command}] not found in config.ini.")
            print(f"")
            exit(-1)

    print(f"")
    print(f"-------------------------------------------------")
    print(f"host            :  {db_config['host']} ")
    print(f"db              :  {db_config['database']} ")
    print(f"")
    print(f"backup_file     :  {backup_file} ")
    print(f"sql_script      :  {sql_script} ")
    print(f"-------------------------------------------------")
    print(f"")

    print(f"")
    try:
        current_dir = os.getcwd()
        print(f"Start importing SQL File : {backup_file} ...")
        if os.path.exists(backup_file):
            print(f"Missing file : {backup_file} ")
            exit(-1)

        start_time = time.time()
        export_result = import_sql_file_2_database(db_config['mysql_path'], db_config, backup_file, sql_script)
        end_time = time.time()
        if export_result == 0:
            print(f"")
            print(f"-------------------------------------------------")
            print(f"                 Successfully")
            print(f"-------------------------------------------------")
            print(f"database        :  {args.database} ")
            print(f"duration        :  {end_time - start_time:.2f} s ")
            print(f"-------------------------------------------------")
            print(f"")
            exit(0)
        else:
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
