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


