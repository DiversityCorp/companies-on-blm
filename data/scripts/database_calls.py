import os
import psycopg2
import time
import datetime


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
            temp_table_query = "DROP TABLE IF EXISTS temp_companies; CREATE TEMP TABLE temp_companies ( like companies including all); ALTER TABLE temp_companies DROP COLUMN id;"
            cursor_object.execute(temp_table_query)
            cursor_object.copy_expert("COPY temp_companies FROM STDIN WITH (FORMAT CSV, NULL 'null')", data)

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

    header = ["company_name", "employee_count", "part_time_employee_count", "diversity_policy_url", "diversity_report_url", "ice_contract", "mean_wages", "median_wages", "executive_team_size", "executive_team_photo", "executive_team_ceo_wages"]

    # Open file
    try:
        with open(source_file, 'r') as data:

            # Get header and transform into a list
            data_header = header_to_list(data.readline())
            # Validate header
            if data_header != header:
                raise ValueError(
                    "Incorrect header for hr and executive teams tables. Please refer to the DATA_SOURCING doc.")

            # Load data to temporary table
            column_def = "company_name varchar NOT NULL, employee_count int, part_time_employee_count int, diversity_policy_url varchar, diversity_report_url varchar, ice_contract bool, mean_wages int, median_wages int, executive_team_size smallint, executive_team_photo varchar, executive_team_ceo_wages int"
            temp_table_query = "DROP TABLE IF EXISTS temp_hr; CREATE TEMP TABLE temp_hr ({});".format(column_def)
            cursor_object.execute(temp_table_query)
            cursor_object.copy_expert("COPY temp_hr FROM STDIN WITH (FORMAT CSV, NULL 'null')", data)

            # Drop rows for companies that are not in the database and print warning
            detect_companies = "(company_name NOT IN (SELECT usual_name FROM companies))"
            ignore_new_companies_query = "DELETE FROM temp_hr WHERE {} IS TRUE RETURNING company_name;".format(detect_companies)
            cursor_object.execute(ignore_new_companies_query)
            # Display a warning if companies where ignored
            if cursor_object.rowcount > 0:
                print("WARNING: The following companies could not be found in the database, they will be ignored:")
                print(cursor_object.fetchall())

            # Match companies names to ids
            cursor_object.execute("ALTER TABLE temp_hr ADD COLUMN company_id int;")
            match_id_query = "UPDATE temp_hr SET company_id = companies.id FROM companies WHERE temp_hr.company_name = companies.usual_name;"
            cursor_object.execute(match_id_query)

            # Add date column with current date
            cursor_object.execute("ALTER TABLE temp_hr ADD COLUMN last_updated date DEFAULT CURRENT_DATE")

            # Update hr table, expect for executive_teams link
            insert_query = "INSERT INTO hr (company_id, {0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}) SELECT company_id, {0}, {1}, {2}, {3}, {4}, {5}, {6}, {7} FROM temp_hr ON CONFLICT (company_id) DO UPDATE SET {0} = COALESCE(excluded.{0}, hr.{0}), {1} = COALESCE(excluded.{1}, hr.{1}), {2} = COALESCE(excluded.{2}, hr.{2}), {3} = COALESCE(excluded.{3}, hr.{3}), {4} = COALESCE(excluded.{4}, hr.{4}), {5} = COALESCE(excluded.{5}, hr.{5}), {6} = COALESCE(excluded.{6}, hr.{6}), {7} = COALESCE(excluded.{7}, hr.{7});".format("last_updated", "employee_count", "part_time_employee_count", "diversity_policy_url", "diversity_report_url", "ice_contract", "mean_wages", "median_wages")
            cursor_object.execute(insert_query)

            # Update existing executive teams
            cursor_object.execute("ALTER TABLE temp_hr ADD COLUMN exec_team_id int;")
            find_teams_query = "UPDATE temp_hr SET exec_team_id = hr.executive_team FROM hr WHERE temp_hr.company_id = hr.company_id;"
            cursor_object.execute(find_teams_query)
            update_teams_query = "UPDATE executive_teams SET size = temp_hr.executive_team_size, photo_url = temp_hr.executive_team_photo, ceo_wages = temp_hr.executive_team_ceo_wages FROM temp_hr WHERE executive_teams.id = temp_hr.exec_team_id;"
            cursor_object.execute(update_teams_query)

            # Add executive teams and reference in hr table
            cursor_object.execute("SELECT executive_team_size, executive_team_photo, executive_team_ceo_wages, company_id FROM temp_hr WHERE temp_hr.exec_team_id IS NULL;")
            tuples = cursor_object.fetchall()
            new_teams_query = "WITH added AS (INSERT INTO executive_teams (size, photo_url, ceo_wages) VALUES (%s, %s, %s) RETURNING id) UPDATE hr SET executive_team = added.id FROM added WHERE hr.company_id = %s;"
            cursor_object.executemany(new_teams_query, tuples)


    except psycopg2.Error as e:
        print("Could not upload {} to database.".format(source_file))
        raise psycopg2.Error(e)


def update_rankings(source_file, cursor_object):
    """Update the fortune rankings table using data from a CSV file.

    :param source_file: Path to the CSV source file.
    :type source_file: str
    :param cursor_object: Cursor to the database.
    :type cursor_object: psycopg2.cursor

    """

    header = ["ranked_at", "ranking", "company_name", "fortune_summary"]

    # Open file
    try:
        with open(source_file, 'r') as data:

            # Get header and transform into a list
            data_header = header_to_list(data.readline())
            # Validate header
            if data_header != header:
                raise ValueError(
                    "Incorrect header for fortune rankings table. Please refer to the DATA_SOURCING doc.")

            # Load data to temporary table
            column_def = "ranked_at smallint NOT NULL, ranking smallint NOT NULL, company_name varchar NOT NULL, fortune_summary text"
            temp_table_query = "DROP TABLE IF EXISTS temp_rankings; CREATE TEMP TABLE temp_rankings ({});".format(column_def)
            cursor_object.execute(temp_table_query)
            cursor_object.copy_expert("COPY temp_rankings FROM STDIN WITH (FORMAT CSV, NULL 'null')", data)

            # Drop rows for companies that are not in the database and print warning
            detect_companies = "(company_name NOT IN (SELECT usual_name FROM companies))"
            ignore_new_companies_query = "DELETE FROM temp_rankings WHERE {} IS TRUE RETURNING company_name;".format(detect_companies)
            cursor_object.execute(ignore_new_companies_query)
            # Display a warning if companies where ignored
            if cursor_object.rowcount > 0:
                print("WARNING: The following companies could not be found in the database, they will be ignored:")
                print(cursor_object.fetchall())

            # Match companies names to ids
            cursor_object.execute("ALTER TABLE temp_rankings ADD COLUMN company_id int;")
            match_id_query = "UPDATE temp_rankings SET company_id = companies.id FROM companies WHERE temp_rankings.company_name = companies.usual_name;"
            cursor_object.execute(match_id_query)

            # Update fortune rankings table
            insert_query = "INSERT INTO fortune_rankings ({0}, {1}, {2}, {3}) SELECT {0}, {1}, {2}, {3} FROM temp_rankings ON CONFLICT (ranked_at, ranking) DO UPDATE SET {2} = COALESCE(excluded.{2}, fortune_rankings.{2}), {3} = COALESCE(excluded.{3}, fortune_rankings.{3});".format("ranked_at", "ranking", "company_id", "fortune_summary")
            cursor_object.execute(insert_query)

    except psycopg2.Error as e:
        print("Could not upload {} to database.".format(source_file))
        raise psycopg2.Error(e)


def update_financials(source_file, cursor_object):
    """Update the financial table using data from a CSV file.

    :param source_file: Path to the CSV source file.
    :type source_file: str
    :param cursor_object: Cursor to the database.
    :type cursor_object: psycopg2.cursor

    """

    header = ["data_at", "company_name", "revenues", "profits", "market_value", "assets", "total_stockholder_equity", "revenues_increase", "profits_increase", "earnings_per_share", "total_return_for_investors_in_year", "total_annual_return_for_investors_in_ten_years"]

    # Open file
    try:
        with open(source_file, 'r') as data:

            # Get header and transform into a list
            data_header = header_to_list(data.readline())
            # Validate header
            if data_header != header:
                raise ValueError(
                    "Incorrect header for financials table. Please refer to the DATA_SOURCING doc.")

            # Load data to temporary table
            column_def = "data_at smallint NOT NULL, company_name varchar NOT NULL, revenues int, profits int, market_value int, assets int, total_stockholder_equity int, revenues_increase numeric, profits_increase numeric, earnings_per_share smallint, total_return_for_investors_in_year numeric, total_annual_return_for_investors_in_ten_years numeric"
            temp_table_query = "DROP TABLE IF EXISTS temp_financials; CREATE TEMP TABLE temp_financials ({});".format(column_def)
            cursor_object.execute(temp_table_query)
            cursor_object.copy_expert("COPY temp_financials FROM STDIN WITH (FORMAT CSV, NULL 'null')", data)

            # Drop rows for companies that are not in the database and print warning
            detect_companies = "(company_name NOT IN (SELECT usual_name FROM companies))"
            ignore_new_companies_query = "DELETE FROM temp_financials WHERE {} IS TRUE RETURNING company_name;".format(detect_companies)
            cursor_object.execute(ignore_new_companies_query)
            # Display a warning if companies where ignored
            if cursor_object.rowcount > 0:
                print("WARNING: The following companies could not be found in the database, they will be ignored:")
                print(cursor_object.fetchall())

            # Match companies names to ids
            cursor_object.execute("ALTER TABLE temp_financials ADD COLUMN company_id int;")
            match_id_query = "UPDATE temp_financials SET company_id = companies.id FROM companies WHERE temp_financials.company_name = companies.usual_name;"
            cursor_object.execute(match_id_query)

            # Update fortune rankings table
            insert_query = "INSERT INTO financials ({0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}, {8}, {9}, {10}, {11}) SELECT {0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}, {8}, {9}, {10}, {11} FROM temp_financials ON CONFLICT (data_at, company_id) DO UPDATE SET {2} = COALESCE(excluded.{2}, financials.{2}), {3} = COALESCE(excluded.{3}, financials.{3}), {4} = COALESCE(excluded.{4}, financials.{4}), {5} = COALESCE(excluded.{5}, financials.{5}), {6} = COALESCE(excluded.{6}, financials.{6}), {7} = COALESCE(excluded.{7}, financials.{7}), {8} = COALESCE(excluded.{8}, financials.{8}), {9} = COALESCE(excluded.{9}, financials.{9}), {10} = COALESCE(excluded.{10}, financials.{10}), {11} = COALESCE(excluded.{11}, financials.{11});".format("data_at", "company_id", "revenues", "profits", "market_value", "assets", "total_stockholder_equity", "revenues_increase", "profits_increase", "earnings_per_share", "total_return_for_investors_in_year", "total_annual_return_for_investors_in_ten_years")
            cursor_object.execute(insert_query)

    except psycopg2.Error as e:
        print("Could not upload {} to database.".format(source_file))
        raise psycopg2.Error(e)


def update_events(source_file, cursor_object):
    """Update the notable events table using data from a CSV file.

    :param source_file: Path to the CSV source file.
    :type source_file: str
    :param cursor_object: Cursor to the database.
    :type cursor_object: psycopg2.cursor

    """

    header = ["event_at", "company_name", "keywords", "description", "statement_text", "official_url", "analysis_url"]

    # Open file
    try:
        with open(source_file, 'r') as data:

            # Get header and transform into a list
            data_header = header_to_list(data.readline())
            # Validate header
            if data_header != header:
                raise ValueError(
                    "Incorrect header for events table. Please refer to the DATA_SOURCING doc.")

            # Load data to temporary table
            column_def = "event_at timestamp NOT NULL, company_name varchar NOT NULL, keywords varchar, description varchar, statement_text text, official_url varchar, analysis_url varchar"
            temp_table_query = "DROP TABLE IF EXISTS temp_events; CREATE TEMP TABLE temp_events ({});".format(column_def)
            cursor_object.execute(temp_table_query)
            cursor_object.copy_expert("COPY temp_events FROM STDIN WITH (FORMAT CSV, NULL 'null')", data)

            # Drop rows for companies that are not in the database and print warning
            detect_companies = "(company_name NOT IN (SELECT usual_name FROM companies))"
            ignore_new_companies_query = "DELETE FROM temp_events WHERE {} IS TRUE RETURNING company_name;".format(detect_companies)
            cursor_object.execute(ignore_new_companies_query)
            # Display a warning if companies where ignored
            if cursor_object.rowcount > 0:
                print("WARNING: The following companies could not be found in the database, they will be ignored:")
                print(cursor_object.fetchall())

            # Match companies names to ids
            cursor_object.execute("ALTER TABLE temp_events ADD COLUMN company_id int;")
            match_id_query = "UPDATE temp_events SET company_id = companies.id FROM companies WHERE temp_events.company_name = companies.usual_name;"
            cursor_object.execute(match_id_query)

            # Update fortune rankings table
            insert_query = "INSERT INTO notable_events ({0}, {1}, {2}, {3}, {4}, {5}, {6}) SELECT {0}, {1}, {2}, {3}, {4}, {5}, {6} FROM temp_events;".format("event_at", "company_id", "keywords", "description", "statement_text", "official_url", "analysis_url")
            cursor_object.execute(insert_query)

    except psycopg2.Error as e:
        print("Could not upload {} to database.".format(source_file))
        raise psycopg2.Error(e)


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
            try:
                update_hr(user_input, cursor_object)
            except Exception as e:
                print("Could not upload hr or executive_teams table.")
                print(e)
        elif table_type == "rankings":
            try:
                update_rankings(user_input, cursor_object)
            except Exception as e:
                print("Could not upload fortune rankings table.")
                print(e)
        elif table_type == "financials":
            try:
                update_financials(user_input, cursor_object)
            except Exception as e:
                print("Could not upload financial table.")
                print(e)
        elif table_type == "events":
            try:
                update_events(user_input, cursor_object)
            except Exception as e:
                print("Could not upload events table.")
                print(e)



disconnect_from_database(connection_object, cursor_object, save)
print("DONE")
