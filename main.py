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
    max_depth = 4
    if os.path.exists(f"./{creds_file}"):
        return f"./{creds_file}"
    for i in range(max_depth):
        upper = '../' * i
        if os.path.exists(f"{upper}/{creds_file}"):
            return f"../{creds_file}"
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
    returns who is the active logged in usern
    """
    creds = get_credentials()
    if "username" in creds:
        print(creds["username"])
    else:
        print("Username not found in credentials, please log-in")

@arguably.command
def login(username : str | None = None, password : str | None = None, rootLink : str | None = None):
    """
    logins the user, takes credentials such as username, password, contesturl and creates persistant session file
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
    returns ranking of all users in current chosen contest
    :return:
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
    returns latest submission for chosen contest
    :return:
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
    '''
    returns a list of errors for chosen submission
    :param subUrl:
    :return:
    '''
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
    '''
    returns list of tasks from a given contest
    :param only_not_completed:
    :return:
    '''
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
    '''
    :param: subUrl - link do wysłania zadania na szkopule (jeden z elementow zwrotu zadan)
    :param: file - plik do wyslania
    :param: filetype - typ pliku do wyboru : C, C++ , Pascal , python
    :return:
    '''
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
