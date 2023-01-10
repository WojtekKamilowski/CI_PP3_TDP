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
        print("Example: 10,20,30,40,50,60\n")

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
    - Negative surplus indicates trailers requested from haulier on the same day.
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
    Collects columns of data from loaded worksheet, collecging
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
    Calculate the average planned for each lane, 
    """
    print("Calculating planned data...\n")
    new_planned_data = []

    for column in data:
        int_column = [int(num) for num in column]
        average = sum(int_column) / len(int_column)
        planned_num = average
        new_planned_data.append(round(planned_num))

    return new_planned_data


def main():
    """
    Run all program functions
    """
    data = get_loaded_data()
    loaded_data = [int(num) for num in data]
    update_worksheet(loaded_data, "loaded")
    new_added_unused_data = calculate_added_unused_data(loaded_data)
    update_worksheet(new_added_unused_data, "added_unused")
    loaded_column = get_last_5_entries_loaded()
    planned_data = calculate_planned_data(loaded_column)
    update_worksheet(planned_data, "planned")
   

print("Welcome to Trailers Demand Planner")
main()

