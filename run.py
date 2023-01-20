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
    Based on CI_PP3_Connect4
    """
    print("____________________________________________________")
    print("|                                                   |")
    print("|            TRAILERS DEMAND PLANNER                |")
    print("|                                                   |")
    print("|___________________________________________________|")
    print(r" ___    ___    ___                          |")
    print(r"/ _ \  / _ \  / _ \                         |")
    print(r"|(_) | |(_) | |(_) |                        |")
    print(r"\___/  \___/  \___/                         |")


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
    print("5. Add a new lane & exit\n")
    print("6. Delete a lane & exit\n")
    print("7. Clear RECENT non-default data & exit\n")
    print("8. Clear ALL non-default data & exit\n")
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

    return lane_count


planned_lane_count = lane_count(PLANNED)


def get_loaded_data():
    """
    Get used equipment figures input from the user for loaded worksheet.
    Run a while loop to collect a valid string of data from the user
    via the terminal, which must be a string of as many numbers
    equal to the lane count separated by commas.
    The loop will repeatedly request data, until it is valid.
    """
    while True:
        print("Please enter used equipment data from the last operations.")
        print(f"{planned_lane_count} numbers, separated by commas.")
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
                f"{planned_lane_count} values required, provided {len(values)}"
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
    Compare loaded values with planned
    and calculate how many were added or unused for each lane.
    It is defined as the loaded figure subtracted from the planned:
    - Positive number indicates unused trailers
    - Negative number indicates trailers requested on the same day.
    """
    print("Calculating added_unused data...\n")
    planned = PLANNED.get_all_values()
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
    Runs daily trailer forecast update functions.
    Option 9 based on Code Institute's walkthrough project Love Sandwiches.
    """
    data = get_loaded_data()
    loaded_data = [int(num) for num in data]
    update_worksheet(loaded_data, "loaded")
    new_added_unused_data = calculate_added_unused_data(loaded_data)
    update_worksheet(new_added_unused_data, "added_unused")
    loaded_column = get_last_5_entries_loaded()
    planned_data = calculate_planned_data(loaded_column)
    update_worksheet(planned_data, "planned")


def get_last_loaded():
    """
    For Menu option 1.
    Collects columns of data from loaded worksheet, collecting
    the last entry for each lane and returns the data
    as a list of strings.
    """
    column_count = lane_count(LOADED) + 1

    last_loaded_columns = []
    for ind in range(1, column_count):
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
    column_count = lane_count(PLANNED) + 1

    last_planned_columns = []
    for ind in range(1, column_count):
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
    column_count = lane_count(ADDED_UNUSED) + 1

    last_added_unused_columns = []
    for ind in range(1, column_count):
        last_added_unused_column = ADDED_UNUSED.col_values(ind)
        last_added_unused_columns.append(last_added_unused_column[-1:])

    last_added_unused_col_str = [''.join(x) for x in last_added_unused_columns]
    return last_added_unused_col_str


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
    column_count = lane_count(ADDED_UNUSED) + 1

    unsd_haul_cols = []

    for ind in range(1, 8):
        unused_haulage_column = ADDED_UNUSED.col_values(ind)
        unsd_haul_cols.append(unused_haulage_column[1:])

    # code from stackoverflow.com
    int_und_haul_cls = ([[int(float(j)) for j in i] for i in unsd_haul_cols])

    return flatten_list(int_und_haul_cls)


added_unused_values = added_unused_values()


def unused_haulage_costs():
    """
    For Menu option 4.
    Run a while loop to collect a valid data with estimated cancellation charge
    per trailer from the user via the terminal, which must be a number
    or adds 250 as data for cancellation charge value if the input is empty.
    The loop will repeatedly request data, until it is valid.
    Filters data from entire added_unused worksheet
    and only recent row to collect only positive numbers,
    adds all positive numbers, and multiplies the sum by
    the entered/default amount for cancellation charge per trailer
    to calculate the cancellation costs.
    """
    while True:
        canc_char = input("Enter cancellation charge/trailer(EUR): e.g. 250\n")

        if canc_char == "":
            print("No value entered, default value in use\n")
            canc_char = "250"

        if validate_number(canc_char):
            print(f"Cancellation charge per trailer: {canc_char} EUR\n")
            break
        else:
            True

    # From https://www.codespeedy.com/
    und_haul_vals = list(filter(lambda x: (x > 0), added_unused_values))

    und_haul_sum = sum(und_haul_vals)

    und_haul_costs = und_haul_sum * int(canc_char)

    # From https://stackoverflow.com/
    int_last_added_unused_data = list(map(int, last_added_unused_data))
    lt_und_data = list(filter(lambda x: (x > 0), int_last_added_unused_data))
    last_und_sum = sum(lt_und_data)
    last_unused_cost = last_und_sum * int(canc_char)

    print(f"Total {und_haul_sum} cancelled trailers cost: €{und_haul_costs}\n")
    print(f"Recently {last_und_sum} trailer(s) cost: €{last_unused_cost}\n")


def validate_number(number):
    """
    Inside the try, converts string value into integer.
    Raise ValueError if string cannot be converted into int.
    Based on Love Sandwiches by Code Institute:
    https://github.com/Code-Institute-Solutions/love-sandwiches-p5-sourcecode/blob/master/05-deployment/01-deployment-part-1/run.py
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
    print("Recommended format: town, CC->town, CC")
    print("Example: Cork, IE->Dublin, IE")
    print("Please review the lanes above to avoid an unwanted duplicate\n")
    lane = input("Please enter a new lane name:\n")
    return lane


def add_lane(lane):
    """
    For Menu option 5.
    Based on https://stackoverflow.com/
    Adds entered by the user lane to all 3 worksheets.
    """
    def add_heading(wksh):
        """
        Add a new column with the lane name to the worksheet.
        """
        first_row = len(wksh.row_values(1))
        column = first_row+1
        wksh.update_cell(1, column, lane)
    print("Adding headings...")

    add_heading(LOADED)
    add_heading(PLANNED)
    add_heading(ADDED_UNUSED)

    def add_values(wksh):
        """
        Adds values 0 to cells under the heading of the lane to be added.
        """
        row_range = len(wksh.col_values(1)) + 1

        row = len(wksh.row_values(2))
        column = row+1

        for i in range(2, row_range):
            wksh.update_cell(i, column, "0")

    print("updating worksheets...")

    add_values(LOADED)
    add_values(PLANNED)
    add_values(ADDED_UNUSED)

    print(f"Lane '{lane}' has been added successfully.\n")


def lane_names():
    """
    For Menu option 6.
    Prints lane names that are planned for next loading
    """
    headings = PLANNED.get_all_values()[0]
    print("Following lanes are planned for next loading:\n")
    print(headings)
    print("")


def delete_lane():
    """
    For Menu option 6.
    Asks for index number of the lane to be deleted by the user.
    Confirms if the user wants to delete the lane with the chosen index number.
    Deletes the lane from all 3 worksheets if confirmed
    or breaks the loop if the user does not confirm.
    """
    while True:
        print("Choose a lane to be deleted by entering its index.")
        print("From the left the index number of the first one is 1.")
        print(f"Lanes indexes are from 1 to {lane_count(PLANNED)}")
        lane_index = input("Please enter index number, example: 1:\n")

        if validate_index(lane_index):
            print(f"Selected lane index: {lane_index}")
            break
        else:
            True

    while True:
        print(f"Confirm to delete lane index number: {lane_index}?\n")
        confirm_index = input(f"yes(y) / no(n):\n")

        lane_index_int = int(lane_index)

        if confirm_index == "yes" or confirm_index == "y":

            # From https://stackoverflow.com/
            LOADED.delete_columns(lane_index_int)
            PLANNED.delete_columns(lane_index_int)
            ADDED_UNUSED.delete_columns(lane_index_int)

            print(f"Lane index: {lane_index} has been deleted successfully\n")
            print("Closing program...")
            print("Program closed!")
            break
        elif confirm_index == "no" or confirm_index == "n":
            print(f"Deleting lane index number: {lane_index} has been stopped")
            main()
            break
        else:
            print("Invalid input!")
            print("Please input: yes OR y OR no OR n")


def validate_index(index):
    """
    Inside the try, converts all string values into integers.
    Raise ValueError if strings cannot be converted into int,
    or if the input is more than number of indexes.
    """
    try:
        [int(index)]
        if int(index) > planned_lane_count:
            raise ValueError(
                f"Indexes are 1 to {planned_lane_count}, entered {index}"
            )
    except ValueError as e:
        print(f"Invalid data: {e}, please try again. \n")
        return False
    return True


def delete_last_data(wksh, wksh_name):
    """
    For Menu option 7.
    From https://stackoverflow.com/
    Identifies last row index & deletes data from it.
    """
    last_row = len(wksh.col_values(1))

    dflt_rows = 7

    if wksh == PLANNED:
        dflt_rows = 8

    if last_row > dflt_rows:
        print(f"Deleting from {wksh_name} worksheet...")
        wksh.delete_rows(last_row)
        print(f"Deleting from {wksh_name} worksheet has been completed!\n")
    else:
        print(f"All non-default data from {wksh_name} already deleted.\n")


def delete_all_data(wksh, wksh_name):
    """
    For Menu option 8.
    From https://stackoverflow.com
    Deletes all data from whsh and adds blank rows.
    """
    last_row = len(wksh.col_values(1))

    dflt_rows = 7

    if wksh == PLANNED:
        dflt_rows = 8

    if last_row > dflt_rows:
        wksh.delete_rows(dflt_rows + 1, last_row)
        print(f"Deleting ALL non-default data from {wksh_name}...")
        print(f"ALL non-default data deleted from {wksh_name} now")
    else:
        print(f"All non-default data from {wksh_name} already deleted.\n")


def main():
    """
    Runs all program functions
    Loop based on https://www.youtube.com/watch?v=_qHGNgJ1EcI&t=1s
    """
    while True:
        logo()
        menu()

        option = input("Please choose an option:\n")

        if option == "1":
            print("Last time the following numbers of trailers were loaded:")
            print(last_loaded_values)
        elif option == "2":
            print("Please ensure to pre-order trailers for next loading:")
            print(last_planned_values)
        elif option == "3":
            print("For last ops we unused or ordered at the day:\n")
            print("- Positive number: unused trailers.\n")
            print("- 0 indicates that was no trailers addded or unused.\n")
            print("- Negative number: trailers ordered during ops.\n")
            print(last_added_unused_values)
        elif option == "4":
            unused_haulage_costs()
        elif option == "5":
            lane_names()
            lane = request_new_lane()

            if lane != "":
                add_lane(lane)
                print("Closing program...")
                print("Program closed!")
                break
            else:
                print("Input cannot be blank!")
                print("Choose this option again")
                print("Enter at least one character for name/code of the lane")
        elif option == "6":
            # From https://docs.gspread.org/en/latest/user-guide.html
            second_lane = PLANNED.cell(1, 2).value

            if second_lane is not None:
                lane_names()
                delete_lane()
                break
            else:
                lane_names()
                print("At least one lane must remain")
                print("you need to add one more to be able to delete a lane")
        elif option == "7":
            cfrm_del_rec = input("Confirm deleting LAST: yes(y) / no(n)\n")

            if cfrm_del_rec == "yes" or cfrm_del_rec == "y":
                delete_last_data(LOADED, "loaded")
                delete_last_data(PLANNED, "planned")
                delete_last_data(ADDED_UNUSED, "added_unused")
                print("Closing program...")
                print("Program closed!")
                break
            elif cfrm_del_rec == "no" or cfrm_del_rec == "n":
                print("Deleting RECENT data has been stopped!")
                main()
                break
            else:
                print("Invalid input!")
                print("Please input: yes OR y OR no OR n")
        elif option == "8":
            cfm_del_all = input("Confirm deleting ALL: yes(y) / no(n)\n")

            if cfm_del_all == "yes" or cfm_del_all == "y":
                delete_all_data(LOADED, "loaded")
                delete_all_data(PLANNED, "planned")
                delete_all_data(ADDED_UNUSED, "added_unused")
                print("Closing program...")
                print("Program closed!")
                break
            elif cfm_del_all == "no" or cfm_del_all == "n":
                print("Deleting ALL data has been stopped!")
                main()
                break
            else:
                print("Invalid input!")
                print("Please input: yes OR y OR no OR n")
        elif option == "9":
            lane_names()
            daily_trailer_forecast()
            print("Closing program...")
            print("Program closed!")
            break
        elif option == "0":
            print("Closing program...")
            print("Program closed!")
            break
        else:
            print("Invalid Option, please try again")

        input("Press enter to return to the menu\n")


main()
