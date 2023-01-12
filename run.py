import gspread
from google.oauth2.service_account import Credentials

SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
    ]

CREDS = Credentials.from_service_account_file('creds.json')
SCOPED_CREDS = CREDS.with_scopes(SCOPE)
GSPREAD_CLIENT = gspread.authorize(SCOPED_CREDS)
SHEET = GSPREAD_CLIENT.open('trailers_demand_planner')


import heapq

# Python Console Menu based on https://www.youtube.com/watch?v=_qHGNgJ1EcI&t=1s
def menu():
    """
    Prints menu options
    """
    print("TDP - Trailers Demand Planner")
    print("-----------------------------")
    print("Options:\n")
    print("1. Preview last loaded data\n")
    print("2. Preview last planned data\n")
    print("3. Preview last added_unused data\n")
    print("4. Identify lanes generating unused haulage costs\n")
    print("5. Add a new lane\n")
    print("6. Delete a lane\n")
    print("7. Share Worksheet via email\n")
    print("8. Clear last data & exit\n")
    print("9. Run daily trailer forecast & exit\n")
    print("0. Exit")
    print("-----------------------------")

"""
Daily trailer forecast for option 9 based on Code Institute's walkthrough project Love Sandwiches:
"""
def get_loaded_data():
    """
    Get used equipment figures input from the user for loaded worksheet.
    Run a while loop to collect a valid string of data from the user
    via the terminal, which must be a string of 6 numbers separated
    by commas. The loop will repeatedly request data, until it is valid.
    """
    while True:        
        print("Please enter used equipment data from the last operations.")
        print("Data should be six numbers, separated by commas.")
        print("Example: 1,2,3,4,5,6\n")

        data_str = input("Enter your data here:\n")
        
        loaded_data = data_str.split(",")
        validate_data(loaded_data)

        if validate_data(loaded_data):
            print("Data is valid!")
            break

    return loaded_data


def validate_data(values):
    """
    inside the try, coverts all string values into integers.
    Raise ValueError if strings cannot be converted into int,
    or if there aren't exactly 6 values.
    """
    try: 
        [int(value) for value in values]
        if len(values) != 6:
            raise ValueError(
                f"Exactly 6 value required, you provided {len(values)}"
            )
    except ValueError as e:
        print(f"Invalid data: {e}, please try again. \n")
        return False
    
    return True


def update_worksheet(data, worksheet):
    """
    Receives a list of integers to be inserted into a worksheet
    Update the relevant worksheet with the data provided
    """
    print(f"Updating {worksheet} worksheet...\n")
    worksheet_to_update = SHEET.worksheet(worksheet)
    worksheet_to_update.append_row(data)
    print(f"{worksheet} worksheet updated successfully.\n")


def calculate_added_unused_data(loaded_row):
    """
    Compare loaded values with planned and calculate how many were added or unused for each lane.
    It is defined as the loaded figure subtracted from the planned:
    - Positive number indicates unused trailers
    - Negative number indicates trailers requested from haulier on the same day.
    """
    print("Calculating added_unused data...\n")
    planned = SHEET.worksheet("planned").get_all_values()
    planned_row = planned[-1]
    
    added_unused_data = []
    for planned, loaded in zip(planned_row, loaded_row):
        added_unused = int(planned) - loaded
        added_unused_data.append(added_unused)
    
    return added_unused_data


def get_last_5_entries_loaded():
    """
    Collects columns of data from loaded worksheet, collecting
    the last 5 entries for each lane and returns the data
    as a list of lists.
    """
    loaded = SHEET.worksheet("loaded")
    
    columns = []
    for ind in range(1, 7):
        column = loaded.col_values(ind)
        columns.append(column[-5:])
    
    return columns 


def calculate_planned_data(data):
    """
    Calculate the average planned for each lane.
    """
    print("Calculating planned data...\n")
    new_planned_data = []

    for column in data:
        int_column = [int(num) for num in column]
        average = sum(int_column) / len(int_column)
        planned_num = average
        new_planned_data.append(round(planned_num))

    return new_planned_data


def daily_trailer_forecast():
    """
    Run daily trailer forecast update functions
    """
    data = get_loaded_data()
    loaded_data = [int(num) for num in data]
    update_worksheet(loaded_data, "loaded")
    new_added_unused_data = calculate_added_unused_data(loaded_data)
    update_worksheet(new_added_unused_data, "added_unused")
    loaded_column = get_last_5_entries_loaded()
    planned_data = calculate_planned_data(loaded_column)
    update_worksheet(planned_data, "planned")


"""
Remaining menu options 
"""
# Menu option 1
def get_last_loaded():
    """
    Collects columns of data from loaded worksheet, collecting
    the last entry for each lane and returns the data
    as a list os strings.
    """
    loaded = SHEET.worksheet("loaded")
    
    last_loaded_columns = []
    for ind in range(1, 7):
        last_loaded_column = loaded.col_values(ind)
        last_loaded_columns.append(last_loaded_column[-1:])

    last_loaded_columns_str = [''.join(x) for x in last_loaded_columns]
    
    return last_loaded_columns_str


last_loaded_data = get_last_loaded()


def get_last_loaded_values(data):
    """
    Return the last loaded numbers with the heading of each lane.
    """
    headings = SHEET.worksheet("loaded").get_all_values()[0]
   
    return {heading: data for heading, data in zip(headings, data)}

last_loaded_values = get_last_loaded_values(last_loaded_data)


# Menu option 2
def get_last_planned():
    """
    Collects columns of data from planned worksheet, collecting
    the last entry for each lane and returns the data
    as a list os strings.
    """
    planned = SHEET.worksheet("planned")
    
    last_planned_columns = []
    for ind in range(1, 7):
        last_planned_column = planned.col_values(ind)
        last_planned_columns.append(last_planned_column[-1:])

    last_planned_columns_str = [''.join(x) for x in last_planned_columns]

    return last_planned_columns_str


last_planned_data = get_last_planned()


def get_last_planned_values(data):
    """
    Return the last planned numbers with the heading of each lane.
    """
    headings = SHEET.worksheet("planned").get_all_values()[0]
   
    return {heading: data for heading, data in zip(headings, data)}

last_planned_values = get_last_planned_values(last_planned_data)


# Menu option 3
def get_last_added_unused():
    """
    Collects columns of data from planned worksheet, collecting
    the last entry for each lane and returns the data
    as a list os strings.
    """
    added_unused = SHEET.worksheet("added_unused")
    
    last_added_unused_columns = []
    for ind in range(1, 7):
        last_added_unused_column = added_unused.col_values(ind)
        last_added_unused_columns.append(last_added_unused_column[-1:])

    last_added_unused_columns_str = [''.join(x) for x in last_added_unused_columns]
    return last_added_unused_columns_str


last_added_unused_data = get_last_added_unused()


def get_last_added_unused_values(data):
    """
    Return the last added_unused numbers with the heading of each lane.
    """
    headings = SHEET.worksheet("added_unused").get_all_values()[0]
   
    return {heading: data for heading, data in zip(headings, data)}

last_added_unused_values = get_last_added_unused_values(last_added_unused_data)


# Menu option 4
def id_unused_haulage_costs():
    """

    """
    added_unused = SHEET.worksheet("added_unused")

    unused_haulage_columns = []

    for ind in range(1, 7):
        unused_haulage_column = added_unused.col_values(ind) 
        unused_haulage_columns.append(unused_haulage_column[1:])
    
    int_unused_haulage_columns = ([[int(float(j)) for j in i] for i in unused_haulage_columns])

    
"""
Main 
"""
def main():
    """
    Runs all program functions
    """
    # Menu loop based on https://www.youtube.com/watch?v=_qHGNgJ1EcI&t=1s
    while True:
        menu()
        option = input("Please choose an option:\n")
            
        if option == "1":
            print("Last time the following numbers of trailers were loaded:")
            print(last_loaded_values)
        elif option == "2":
            print("If not already done, please remember to pre-order following number of trailers for next loading:")
            print(last_planned_values)
        elif option == "3":
            print("Following numbers of trailer were unused or ordered at the day of loading:\n")
            print("- Positive number indicates unused trailers.\n")
            print("- Negative number indicates trailers requested from haulier(s) on the same day.\n")
            print(last_added_unused_values)
        elif option == "4":
            id_unused_haulage_costs()
        elif option == "9":
            daily_trailer_forecast()
            break
        elif option == "0":
            print("Program closed")
            break
        else:
            print("Invalid Option, please try again")
        
        input("Press enter to return to the menu\n")


main()

# python3 run.py

