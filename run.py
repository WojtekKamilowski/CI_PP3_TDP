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
LOADED = SHEET.worksheet("loaded")
PLANNED = SHEET.worksheet("planned")
ADDED_UNUSED = SHEET.worksheet("added_unused")

def logo():
    """
    Prints program logo
    Based on https://github.com/aleksandracodes/CI_PP3_Connect4/blob/main/run.py
    """
    print("____________________________________________________")
    print("|                                                   |")
    print("|            TRAILERS DEMAND PLANNER                |")
    print("|                                                   |")
    print("|___________________________________________________|")
    print(" ___    ___    ___                          |")
    print("/ _ \  / _ \  / _ \                         |")
    print("|(_) | |(_) | |(_) |                        |")
    print("\___/  \___/  \___/                         |")

def menu():
    """
    Prints menu options
    Based on https://www.youtube.com/watch?v=_qHGNgJ1EcI&t=1s
    """
    print("-----------------------------")
    print("Options:\n")
    print("1. Preview last loaded data\n")
    print("2. Preview last planned data\n")
    print("3. Preview last added_unused data\n")
    print("4. Run unused haulage costs report\n")
    print("5. Add a new lane\n")
    print("6. Delete a lane\n")
    print("7. Clear LAST data & exit\n")
    print("8. Clear ALL data & exit\n")
    print("9. Run daily trailer forecast & exit\n")
    print("0. Exit")
    print("-----------------------------")

def flatten_list(_2d_list):
        """
        Taken from https://stackabuse.com/python-how-to-flatten-list-of-lists/
        Flattens list of lists to a single list.
        """
        flat_list = []
        
        for element in _2d_list:
            if type(element) is list:
                
                for item in element:
                    flat_list.append(item)
            else:
                flat_list.append(element)
        return flat_list

def lane_count(wksh):
    """
    Counts and returns how many rows with lane names are in use.
    """
    lane_count = len(wksh.row_values(1))
    return(lane_count)

planned_lane_count = lane_count(PLANNED)  

# Daily trailer forecast for option 9 based on Code Institute's walkthrough project Love Sandwiches:
def get_loaded_data():
    """
    Get used equipment figures input from the user for loaded worksheet.
    Run a while loop to collect a valid string of data from the user
    via the terminal, which must be a string of as many numbers equal to the lane count
    separated by commas. The loop will repeatedly request data, until it is valid.
    """
    while True:   
           
        print("Please enter used equipment data from the last operations.")
        print(f"Data should be {planned_lane_count} numbers(as that many lanes were planned last time), separated by commas.")
        print("Example: 1,2,3,4,5,6,(...)\n")

        data_str = input("Enter your data here:\n")
        
        loaded_data = data_str.split(",")
        
        if validate_data(loaded_data):
            print("Data is valid!")
            break

    return loaded_data

def validate_data(values):
    """
    Inside the try, converts all string values into integers.
    Raise ValueError if strings cannot be converted into int,
    or if there aren't exactly as many values as many lanes.
    """
    try: 
        [int(value) for value in values]
        if len(values) != planned_lane_count:
            raise ValueError(
                f"Exactly {planned_lane_count} value required, you provided {len(values)}"
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
    column_count = lane_count(LOADED) + 1
    
    columns = []
    for ind in range(1, column_count):
        column = LOADED.col_values(ind)
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
    For Menu option 9.
    Runs daily trailer forecast update functions
    """
    data = get_loaded_data()
    loaded_data = [int(num) for num in data]
    update_worksheet(loaded_data, "loaded")
    new_added_unused_data = calculate_added_unused_data(loaded_data)
    update_worksheet(new_added_unused_data, "added_unused")
    loaded_column = get_last_5_entries_loaded()
    planned_data = calculate_planned_data(loaded_column)
    update_worksheet(planned_data, "planned")

# Menu options 1 to 8
def get_last_loaded():
    """
    For Menu option 1.
    Collects columns of data from loaded worksheet, collecting
    the last entry for each lane and returns the data
    as a list os strings.
    """  
    last_loaded_columns = []
    for ind in range(1, 7):
        last_loaded_column = LOADED.col_values(ind)
        last_loaded_columns.append(last_loaded_column[-1:])

    last_loaded_columns_str = [''.join(x) for x in last_loaded_columns]
    
    return last_loaded_columns_str


last_loaded_data = get_last_loaded()

def get_last_loaded_values(data):
    """
    For Menu option 1.
    Return the last loaded numbers with the heading of each lane.
    """
    headings = LOADED.get_all_values()[0]
   
    return {heading: data for heading, data in zip(headings, data)}

last_loaded_values = get_last_loaded_values(last_loaded_data)

def get_last_planned():
    """
    For Menu option 2.
    Collects columns of data from planned worksheet, collecting
    the last entry for each lane and returns the data
    as a list os strings.
    """    
    last_planned_columns = []
    for ind in range(1, 7):
        last_planned_column = PLANNED.col_values(ind)
        last_planned_columns.append(last_planned_column[-1:])

    last_planned_columns_str = [''.join(x) for x in last_planned_columns]

    return last_planned_columns_str

last_planned_data = get_last_planned()

def get_last_planned_values(data):
    """
    For Menu option 2.
    Return the last planned numbers with the heading of each lane.
    """
    headings = PLANNED.get_all_values()[0]
   
    return {heading: data for heading, data in zip(headings, data)}

last_planned_values = get_last_planned_values(last_planned_data)

def get_last_added_unused():
    """
    For Menu option 3.
    Collects columns of data from planned worksheet, collecting
    the last entry for each lane and returns the data
    as a list os strings.
    """    
    last_added_unused_columns = []
    for ind in range(1, 7):
        last_added_unused_column = ADDED_UNUSED.col_values(ind)
        last_added_unused_columns.append(last_added_unused_column[-1:])

    last_added_unused_columns_str = [''.join(x) for x in last_added_unused_columns]
    return last_added_unused_columns_str

last_added_unused_data = get_last_added_unused()

def get_last_added_unused_values(data):
    """
    For Menu option 3.
    Return the last added_unused numbers with the heading of each lane.
    """
    headings = ADDED_UNUSED.get_all_values()[0]
   
    return {heading: data for heading, data in zip(headings, data)}

last_added_unused_values = get_last_added_unused_values(last_added_unused_data)

def added_unused_values():
    """
    For Menu option 4.
    Access data from added_unused worksheet, 
    convert it to list of lists of ints,
    flatten the list of lists to one list of ints.
    """

    unused_haulage_columns = []

    for ind in range(1, 7):
        unused_haulage_column = ADDED_UNUSED.col_values(ind) 
        unused_haulage_columns.append(unused_haulage_column[1:])
    
    # code from https://stackoverflow.com/questions/2166577/casting-from-a-list-of-lists-of-strings-to-list-of-lists-of-ints-in-python 
    int_unused_haulage_columns = ([[int(float(j)) for j in i] for i in unused_haulage_columns])
    
    return flatten_list(int_unused_haulage_columns)

added_unused_values = added_unused_values()

def unused_haulage_costs():
    """
    For Menu option 4.
    Run a while loop to collect a valid data with estimated cancellation charge
    per trailer from the user via the terminal, which must be a number
    or adds 250 as data for cancellation charge value if the input is empty.
    The loop will repeatedly request data, until it is valid.
    Filters data from entire added_unused worksheet and only recent row to collect
    only positive numbers, adds all positive numbers, and multiplies
    the sum by the entered/default amount for cancellation charge per trailer
    to calculate the cancellation costs.
    """
    while True:
        cancellation_charge = input("Please confirm estimated cancellation charge per trailer(EUR), example: 250\n")

        if cancellation_charge == "":
            print("No value enetered, default cancellation charge value in use\n")
            cancellation_charge = "250"          

        if validate_number(cancellation_charge):
            print(f"Cancellation charge per trailer: {cancellation_charge} EUR\n")
            break
        else:
            True

    # From https://www.codespeedy.com/print-all-positive-numbers-from-a-list-in-python/#:~:text=Using%20the%20%E2%80%9Clambda%E2%80%9D%20function%3A,list%20of%20all%20positive%20numbers.
    unused_haulage_values = list(filter(lambda x:(x > 0),added_unused_values)) 

    unused_haulage_sum = sum(unused_haulage_values)

    unused_haulage_costs = unused_haulage_sum * int(cancellation_charge)

    def last_added_unused_data_str():
        str = ""
        for e in last_added_unused_data:
            str += e
        return str

    if validate_number(last_added_unused_data_str()):
        # From https://stackoverflow.com/questions/7368789/convert-all-strings-in-a-list-to-int
        int_last_added_unused_data = list(map(int, last_added_unused_data))
        last_unused_data = list(filter(lambda x:(x > 0),int_last_added_unused_data)) 
        last_unused_sum = sum(last_unused_data)
        last_unused_cost = last_unused_sum * int(cancellation_charge)

        print(f"Until now the total number of {unused_haulage_sum} cancelled trailers generated loss of: {unused_haulage_costs} EUR.\n")
        print(f"For most recent operations we planned {last_unused_sum} trailers that were unused, cancelling them generated costs of: {last_unused_cost} EUR.\n")
    else:
        print("Calculation failed: there is no enough data to calculate from.")
            
def validate_number(number):
    """
    Inside the try, converts string value into integer.
    Raise ValueError if string cannot be converted into int.
    Based on Love Sandwiches by Code Institute: https://github.com/Code-Institute-Solutions/love-sandwiches-p5-sourcecode/blob/master/05-deployment/01-deployment-part-1/run.py
    """
    try: 
        [int(number)]
        
    except ValueError as e:
        print(f"Invalid data: {e}, please try again. \n")
        return False
    
    return True

def request_new_lane():
    """
    For Menu option 5.
    Requests name of a new lane to be added to the sheet by the user.
    """
    print("Lane name should be in following format: loading town, country code->unloading town, country code")
    print("Example: Cork, IE->Dublin, IE")
    lane = input("Please enter a new lane name:\n")    

    return lane

def add_lane(lane):
    """
    For Menu option 5.
    Based on https://stackoverflow.com/questions/60495748/append-value-to-column-in-gspread
    Adds entered by the user lane to all 3 worksheets.
    """
    def add_heading(wksh):
        """
        Add a new column with the lane name to the worksheet.
        """
        first_row = len(wksh.row_values(1))
        column = first_row+1
        wksh.update_cell(1, column, lane)

    add_heading(LOADED)
    add_heading(PLANNED)
    add_heading(ADDED_UNUSED)
    
    print(f"Lane '{lane}' has been added successfully.\n")

def lane_names():
    """
    For Menu option 6.
    Prints lane names that are planned for next loading
    """
    headings = SHEET.worksheet("planned").get_all_values()[0]
    print("Following lanes are planned for next loading:\n")
    print(headings)
    print("")

def delete_lane():
    """
    For Menu option 6.
    Asks for index number of the lane to be deleted by the user.
    Confirms if the user wants to delete the lane with the chosen index number.
    Deletes the lane from all 3 worksheets if confirmed or breaks the loop if the user does not confirm.
    """
    while True:
        print("Review the lanes to choose a lane to be deleted by entering its index (from the left the index number of the first one is 1 :")
        lane_index = input("Please enter index number, example: 1:\n")

        if validate_number(lane_index):
            print(f"Selected lane index: {lane_index}")
            break            
        else:
            True
    while True:
        print(f"Are you sure you want to delete this lane index number: {lane_index}?\n")
        confirm_index = input(f"yes(y) / no(n):\n")   

        lane_index_int = int(lane_index)

        if confirm_index == "yes" or confirm_index == "y":
            # From https://stackoverflow.com/questions/61213417/delete-remove-column-in-google-sheet-over-gspread-python-like-sheet-delete-row#:~:text=There%20is%20no%20method%20in,this%20with%20a%20batch%20update.
            LOADED.delete_columns(lane_index_int)
            PLANNED.delete_columns(lane_index_int)
            ADDED_UNUSED.delete_columns(lane_index_int)
            print(f"Lane index: {lane_index} has been deleted successfully\n") 
            break    
        elif confirm_index == "no" or confirm_index == "n":
            print(f"Deleting lane index number: {lane_index} has been stopped")
            break
        else:
            print("Invalid input, please type one of the following(without quotation marks): 'yes' OR 'y' OR 'no' OR 'n'")

def delete_last_data(wksh):
    """
    For Menu option 7.
    From https://stackoverflow.com/questions/14625617/how-to-delete-remove-row-from-the-google-spreadsheet-using-gspread-lib-in-pytho#:~:text=Since%20gspread%20version%200.5.,a%20row%20with%20delete_row()%20.&text=Save%20this%20answer.,-Show%20activity%20on
    Identifies last row index & deletes data from it.
    """
    last_row = len(wksh.col_values(1))
    wksh.delete_rows(last_row)

def delete_all_data(wksh): 

    """ 
    For Menu option 8. 
    From https://stackoverflow.com/questions/14625617/how-to-delete-remove-row-from-the-google-spreadsheet-using-gspread-lib-in-pytho#:~:text=Since%20gspread%20version%200.5.,a%20row%20with%20delete_row()%20.&text=Save%20this%20answer.,-Show%20activity%20on 
    Deletes all data from whsh and adds blank rows.
    """ 
    last_row = len(wksh.col_values(1)) 
    wksh.delete_rows(2, last_row)

def main():
    """
    Runs all program functions
    """
    # Loop based on https://www.youtube.com/watch?v=_qHGNgJ1EcI&t=1s
    while True:
        logo()
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
            unused_haulage_costs()
        elif option == "5":
            lane = request_new_lane()
            add_lane(lane)
        elif option == "6":
            lane_names()
            delete_lane()
        elif option == "7":
            delete_last_data(LOADED)
            delete_last_data(PLANNED)
            delete_last_data(ADDED_UNUSED)
            print("Last data from all worksheets deleted")
            print("Program closed")
            break
        elif option == "8":
            while True:
                confirm_delete_all = input("Are you sure you want to delete ALL data!?: yes(y) / no(n)\n")

                if confirm_delete_all == "yes" or confirm_delete_all == "y":
                    delete_all_data(LOADED)
                    delete_all_data(PLANNED)
                    delete_all_data(ADDED_UNUSED)
                    print("ALL data deleted!")
                    break
                elif confirm_delete_all == "no" or confirm_delete_all == "n":
                    main()
                    break     
                else:
                    print("Invalid input, please type one of the following(without quotation marks): 'yes' OR 'y' OR 'no' OR 'n'")
            print("Program closed")
            break 
        elif option == "9":
            daily_trailer_forecast()
            print("Program closed")
            break
        elif option == "0":
            print("Program closed")
            break
        else:
            print("Invalid Option, please try again")
        
        input("Press enter to return to the menu\n")

main()
