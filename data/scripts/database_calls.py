import os
import psycopg2
import time
import datetime
import pandas as pd


def connect_to_database():
    """Connect to the diversity-corp database.

    :return: Tuple with a connection object and a cursor object
    :rtype: (psycopg2.connection, psycopg2.cursor)

    """

    DATABASE_URL = os.environ['DATABASE_URL']

    conn = psycopg2.connect(DATABASE_URL, sslmode='require')

    # Open a cursor to perform database operations
    cur = conn.cursor()

    return conn, cur


def disconnect_from_database(connection_object, cursor_object, save):
    """lose the connection to a Postgres database.

    :param connection_object: Connection to the database.
    :type connection_object: psycopg2.connection
    :param cursor_object: Cursor to the database.
    :type cursor_object: psycopg2.cursor
    :param connection_object: Saving changes to database or rollingback.
    :type connection_object: bool

    """

    if save:
        connection_object.commit()
        print("SAVING CHANGES")
    else:
        connection_object.rollback()
        print("REVERTING CHANGES")

    # Close communication with the database
    cursor_object.close()
    connection_object.close()


def download_database(directory, cursor_object):
    """Save the content of the database to CSV files.

    :param directory: Path to the folder where the files should be saved.
    :type directory: str
    :param cursor_object: Cursor to the database.
    :type cursor_object: psycopg2.cursor

    """

    table_names = ["companies", "hr", "executive_teams",
                   "fortune_rankings", "financials", "notable_events"]

    # Create the directory if it does not exist
    if not os.path.exists(directory):
        os.makedirs(directory)

    # For each table in the database
    for t in table_names:
        try:
            # Define the path of the CSV file
            file_name = t + ".csv"
            file_path = os.path.join(directory, file_name)
            # Define the COPY query
            copy_query = "COPY (SELECT * FROM {}) TO STDOUT WITH (FORMAT CSV, HEADER TRUE, FORCE_QUOTE *);".format(t)
            # Copy content of table to csv file
            with open(file_path, 'w+') as csv_file:
                cursor_object.copy_expert(copy_query, csv_file)
        except psycopg2.Error as e:
            print("Postgres error on copying table {}".format(t))
            print(e)
        except Exception as e:
            print("Unknown error on copying table {}".format(t))
            print(e)


def header_to_list(header_string):
    """Tranform the header string from a CSV into a list of column names.

    :param header_string: The string header.
    :type header_string: str
    :return: The list of column names.
    :rtype: list(str)

    """

    return header_string.replace(" ", "").replace("\n", "").split(",")



def update_companies(source_file, cursor_object):
    """Update the companies table using data from a CSV file.

    :param source_file: Path to the CSV source file.
    :type source_file: str
    :param cursor_object: Cursor to the database.
    :type cursor_object: psycopg2.cursor

    """

    header = ["full_name", "usual_name", "created_at", "country", "category", "detailed_category", "sector", "logo_url", "last_full_update"]

    # Open file
    try:
        with open(source_file, 'r') as data:

            # Get header and transform into a list
            data_header = header_to_list(data.readline())
            # Validate header
            if data_header != header:
                raise ValueError(
                    "Incorrect header for companies table. Please refer to the DATA_SOURCING doc.")

            # Load data to temporary table without id column
            temp_table_query = "DROP TABLE IF EXISTS temp_companies; CREATE TEMP TABLE temp_companies ( like companies including all); ALTER TABLE temp_companies DROP COLUMN id"
            cursor_object.execute(temp_table_query)
            cursor_object.copy_from(data, 'temp_companies', sep=',', null='null')

            # Insert new rows and update existing rows into companies table
            insert_query = "INSERT INTO companies ({0}, usual_name, {1}, {2}, {3}, {4}, {5}, {6}, {7}) SELECT DISTINCT ON (usual_name) * FROM temp_companies ON CONFLICT (usual_name) DO UPDATE SET {0} = COALESCE(excluded.{0}, companies.{0}), {1} = COALESCE(excluded.{1}, companies.{1}), {2} = COALESCE(excluded.{2}, companies.{2}), {3} = COALESCE(excluded.{3}, companies.{3}), {4} = COALESCE(excluded.{4}, companies.{4}), {5} = COALESCE(excluded.{5}, companies.{5}), {6} = COALESCE(excluded.{6}, companies.{6}), {7} = COALESCE(excluded.{7}, companies.{7});".format("full_name", "created_at", "country", "category", "detailed_category", "sector", "logo_url", "last_full_update")
            cursor_object.execute(insert_query)

    except psycopg2.Error as e:
        print("Could not upload {} to database.".format(source_file))
        raise psycopg2.Error(e)


def update_hr(source_file, cursor_object):
    """Update the hr and executive_teams tables using data from a CSV file.

    :param source_file: Path to the CSV source file.
    :type source_file: str
    :param cursor_object: Cursor to the database.
    :type cursor_object: psycopg2.cursor

    """

    return



def confirm(file_path):
    """Utility function to confirm the table type of a file.

    :param file_path: File to upload.
    :type file_path: str
    :return: Confirmed type.
    :rtype: str

    """
    table_type = None
    available_tables = ["companies", "hr", "rankings", "financials", "events"]

    # Deduce table to upload
    file_name = os.path.basename(file_path)
    if file_name.find("companies") >= 0:
        table_type = "companies"
    elif file_name.find("hr") >= 0:
        table_type = "hr"
    elif file_name.find("rankings") >= 0:
        table_type = "rankings"
    elif file_name.find("financials") >= 0:
        table_type = "financials"
    elif file_name.find("events") >= 0:
        table_type = "events"

    # Confirm deduced type or get real one
    if table_type == None:
        # If no type was deduced
        i = "n"
    else:
        print("Do you want to update the '{}' table(s)? (y/n)".format(table_type))
        i = input().lower()
    while i != "y" and i != "n":
        # Invalid input loop
        print("Invalid input. Please enter 'y' for yes and 'n' for no.")
        i = input().lower()
    if i == "n":
        # Get real type
        print("What table(s) do you want to update with this file?")
        print("Available values: 'companies', 'hr' (covers 'hr' and 'executive_teams' tables), 'rankings' ('fortune_rankings' table), 'financials', 'events' ('notable_events' table).")
        type = input()
        while type not in available_tables:
            # Invalid input loop
            print("Invalid input. Please enter one of the following: companies, hr, rankings, financials, events.")
            type = input()
        # Save new type
        table_type = type
    return table_type


# Create connexion
connection_object, cursor_object = connect_to_database()
save = False

# Main input loop
while True:

    # Get user input
    print("\n\nPlease provide the path to the file you want to upload, or 'download' to download the database, or 'quit':")
    user_input = input()

    if user_input == "quit":
        # Save changes only if specified by user
        print("Do you want to save your changes to the database? (yes/no)")
        save_decision = input().lower()
        if save_decision == "yes" or save_decision == "y":
            save = True
        # Exit script
        break

    elif user_input == "download":
        # Dowload the database as CSVs
        print("Please enter the path to the local folder you want to save the database in:")
        path = input()
        download_database(path, cursor_object)

    else:
        # Skip if file does not exist
        if not os.path.isfile(user_input):
            continue

        # Get table type
        table_type = confirm(user_input)

        # Send queries
        if table_type == "companies":
            try:
                update_companies(user_input, cursor_object)
            except Exception as e:
                print("Could not upload company table.")
                print(e)
        elif table_type == "hr":
            update_hr(user_input, cursor_object)


disconnect_from_database(connection_object, cursor_object, save)
print("DONE")
