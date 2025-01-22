import os
from szkopul import SkClient
import json
import arguably
from prettytable.colortable import Theme, ColorTable

tabletheme = Theme()
tabletheme.vertical_char = "│"
tabletheme.horizontal_char = "─"

creds_file = "creds.save"

def look_for_credentials():
    """
    Search for a credentials file within a maximum directory traversal depth.

    This function attempts to locate a credentials file starting from the current
    working directory. It initially checks if the file exists in the current directory.
    If not found, it traverses up to a specified maximum number of parent directories.

    :raises FileNotFoundError: If the system cannot access a directory path or file.
    :raises IOError: In case of I/O errors when interacting with the file system.

    :return: The relative path to the credentials file if found, or ``None`` if no
        credentials file is located within the search depth.
    :rtype: str or None
    """
    max_depth = 4
    if os.path.exists(f"./{creds_file}"):
        return f"./{creds_file}"
    for i in range(max_depth):
        upper = '../' * i
        if os.path.exists(f"{upper}/{creds_file}"):
            return f"{upper}/{creds_file}"
    return None

def create_file(filename):
    with open(filename, "w") as f:
        f.close()
    return True

def get_credentials_path() -> str:
    creds_path = look_for_credentials()
    if creds_path is None:
        _ = create_file(creds_file)
        creds_path = creds_file
    return creds_path

def get_credentials():
    creds_path = get_credentials_path()
    creds = {}
    with open(creds_path) as f:
        raw = f.read()
        f.close()
    try:
        creds = json.loads(raw)
    except json.decoder.JSONDecodeError:
        pass
    return creds


@arguably.command
def whoami():
    """
    Provides a command to display the username of the currently logged-in user.
    If the username is not found in the credentials, it prompts the user to log in.

    :return: None
    :rtype: NoneType

    :raises KeyError: If the "username" key does not exist in the credentials dictionary.
    """
    creds = get_credentials()
    if "username" in creds:
        print(creds["username"])
    else:
        print("Username not found in credentials, please log-in")

@arguably.command
def login(username : str | None = None, password : str | None = None, rootLink : str | None = None):
    """
    Logs in a user to the application with provided credentials and saves the credentials 
    locally for future use. This function initializes a client with provided username, 
    password, and link, attempts the login process, and saves the credentials to a file.

    If the login attempt fails due to incorrect credentials or other reasons, an error 
    message will be printed. This function ensures credentials persistence by storing them 
    locally once login is successful.

    :param username: The username for the login credentials.
    :param password: The password associated with the username.
    :param rootLink: The root link or URL associated with the application for login.
    :return: None
    """
    creds_path = get_credentials_path()
    creds = {
        "username": username,
        "password": password,
        "link": rootLink
    }

    try: SkClient(username, password, rootLink).Login()
    except Exception as e: print(f"Login failed with : {e}, please check credentials")

    with open(creds_path, "w") as f:
        f.write(json.dumps(creds))
        f.close()
    print("Logged in successfully")
    return

@arguably.command
def ranking():
    """
    Retrieves the user credentials and fetches the ranking information from a client service. The command logs into
    the client using provided credentials and retrieves the ranking data sorted by points in descending order. 
    A formatted table is displayed to present the ranking information.

    :raises Exception: If login to client fails or ranking data retrieval is unsuccessful.
    """
    creds = get_credentials()
    client = SkClient(login=creds["username"], password=creds["password"], url=creds["link"])

    try: client.Login()
    except Exception as e: print(f"Login failed with : {e}, please check credentials"); return

    try: ranking = client.Ranking()
    except Exception as e: print(f"Ranking failed with : {e}, please check credentials"); return
    sorted_ranking = sorted(ranking, key=lambda k: k[2], reverse=True)
    table = ColorTable(theme=tabletheme)
    table.title = "Ranking"
    table.field_names = ["Name", "Username", "Points"]
    table.add_rows(sorted_ranking)
    print(table)

    return

@arguably.command
def latest_sub(*, url: bool = False, points: bool = False):
    """
    Provides a command for checking and displaying the latest submission of a user from a specific client.

    This function communicates with a client instance using the provided credentials to retrieve the last submission
    information. It has optional parameters to display specific attributes of the submission, such as the submission URL 
    or points. If none of the options are specified, a formatted table displaying the comprehensive details of the latest 
    submission is printed.

    :param url: If set to True, prints the URL of the latest submission.
    :type url: bool
    :param points: If set to True, prints the points of the latest submission.
    :type points: bool
    :return: None. Outputs are printed directly to the console depending on user input.
    :rtype: None
    """
    creds = get_credentials()
    client = SkClient(login=creds["username"], password=creds["password"], url=creds["link"])

    try: client.Login()
    except Exception as e: print(f"Login failed with : {e}, please check credentials"); return

    try: last_submission = client.CheckLatest()
    except Exception as e: print(f"Latest submission failed with : {e}, please check credentials"); return

    if url is True: print(last_submission[1]); return
    elif points is True: print(last_submission[5]); return

    last_submission = [last_submission[0], last_submission[1], last_submission[2], last_submission[5]]
    table = ColorTable(theme=tabletheme)
    table.title = "Latest Submission"
    table.field_names = ["Timestamp", "Submission url", "Task", "Points"]
    table.add_row(last_submission)
    print(table)

@arguably.command
def errors(subUrl : str):
    """
    Checks errors on a specified sub-url using a client API and displays the results
    in a formatted table. This function handles login and errors gracefully and provides
    feedback to the user in case of failures.

    :param subUrl: The sub-url for which to check errors.
    :type subUrl: str
    :return: None
    :rtype: None
    """
    creds = get_credentials()
    client = SkClient(login=creds["username"], password=creds["password"], url=creds["link"])

    try: client.Login()
    except Exception as e: print(f"Login failed with : {e}, please check credentials"); return

    try: err = client.CheckErrors(subUrl)
    except Exception as e: print(f"Getting errors failed with : {e}, please check credentials"); return

    if len(err) == 0: print("No errors found"); return
    err = err['errors']

    table = ColorTable(theme=tabletheme)
    table.title = "Errors"
    table.field_names = ["Error", "Line", "Message"]
    for i in range(len(err)):
        table.add_row([err[i].split(",")[0].split(":")[0]+err[i].split(",")[0].split(":")[1], err[i].split(",")[0].split(":")[2],err[i].split(",")[1]])
    print(table)

    return

@arguably.command
def get_tasks(*, only_not_completed:bool = False, subUrl:str | None = None , taskUrl:str | None=None):
    """
    Fetches and displays tasks from a server using the provided filtering criteria. Optionally,
    can filter tasks based on associated subtask name or specific task URL. If no filters are provided,
    all tasks are processed and displayed in a formatted table.

    :param only_not_completed: If set to True, only fetches tasks that are not completed.
    :param subUrl: A string used to filter a specific subtask by its URL, if provided.
    :param taskUrl: A string used to filter a specific task by its URL, if provided.
    :return: None. Outputs the requested tasks or corresponding messages to the console.
    """
    creds = get_credentials()
    client = SkClient(login=creds["username"], password=creds["password"], url=creds["link"])

    try: client.Login()
    except Exception as e: print(f"Login failed with : {e}, please check credentials"); return

    try: tasks = client.GetTasks(only_not_completed)
    except Exception as e: print(f"Getting tasks failed with : {e}, please check credentials"); return
    if subUrl is not None:
        for task in tasks:
            if task[2] == subUrl:
                print(task[1])
                return
        print(f"No task found with given name {subUrl}")
        return

    if taskUrl is not None:
        for task in tasks:
            if task[2] == taskUrl:
                print(task[0])
                return
        print(f"No task found with given name {taskUrl}")
        return

    tasks_processed = []
    for task in tasks:
        curr_task = [task[2], task[3], task[5], task[4], task[0], task[1]]
        tasks_processed.append(curr_task)

    table = ColorTable(theme=tabletheme)
    table.title = "Tasks"
    table.field_names = ["Task code", "Task", "Points", "Submissions left", "Task url", "Submit"]
    table.add_rows(tasks_processed)

    print(table)

@arguably.command
def submit(subUrl: str, file: str, filetype: str):
    """
    Submit a file for processing on the specified submission URL with the given filetype. The command
    ensures that the correct filetype is provided, authenticates the user using stored credentials, and 
    attempts to submit the file to the external system using a client.

    If the filetype is invalid, an exception will be raised immediately. The function handles login 
    failures, submission errors, and response code validation to properly report issues during the 
    process. Authentication credentials must be pre-configured for successful execution.

    :param subUrl: A string representing the submission URL where the file will be submitted.
    :param file: A string representing the full path to the file to be submitted.
    :param filetype: A string representing the type of the file, must be one of: "C", "C++", "Pascal", "python".
    :return: None.
    """
    if filetype not in ["C", "C++", "Pascal", "python"]:
        raise Exception("Wrong filetype selected, please choose one of : C, C++, Pascal, python")

    creds = get_credentials()
    client = SkClient(login=creds["username"], password=creds["password"], url=creds["link"])

    try: client.Login()
    except Exception as e: print(f"Login failed with : {e}, please check credentials"); return

    try:
        code = client.SendFile(subUrl, file, filetype)
        if code >= 400: raise Exception(f"wrong response code {code}")
    except Exception as e: print(f"Submit failed with : {e}, please check credentials"); return
    return




if __name__ == '__main__':
    arguably.run()
