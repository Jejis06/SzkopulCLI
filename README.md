
# Szkopul Command-Line Tool

This is a Python-based CLI tool for interacting with the [Szkopul](https://szkopul.edu.pl/c/plockie-treningi-olimpijskie/p/) platform. The tool provides various commands to manage credentials, fetch rankings, view tasks, submissions, and handle errors.

## Table of Contents

- [Installation](#installation)
- [Commands](#commands)
  - [whoami](#whoami)
  - [login](#login)
  - [ranking](#ranking)
  - [latest_sub](#latest_sub)
  - [errors](#errors)
  - [get_tasks](#get_tasks)
  - [submit](#submit)

---

## Installation

1. Ensure Python is installed on your machine (Python 3.9 or higher is recommended).
2. Install the required dependencies using pip:
   ```bash
   pip install arguably prettytable
   ```
3. Save your Szkopul credentials in a `creds.save` file or let the tool generate and manage it for you.

---

## Commands

### `whoami`

Displays the username of the currently logged-in user. If the username is not found in the credentials file, it prompts the user to log in.

#### Usage
```bash
python main.py whoami
```

#### Example
```bash
$ python main.py whoami
Dawid Czech
```

---

### `login`

Logs in a user to the Szkopul platform by saving credentials locally for future use.

#### Arguments
- `username` *(str, optional)*: Your Szkopul username.
- `password` *(str, optional)*: Your Szkopul password.
- `rootLink` *(str, optional)*: The root URL of the Szkopul platform.

#### Usage
```bash
python main.py login --username <your_username> --password <your_password> --rootLink https://szkopul.edu.pl/c/plockie-treningi-olimpijskie/p/
```

#### Example
```bash
$ python main.py login --username johndoe --password mypassword --rootLink https://szkopul.edu.pl/c/plockie-treningi-olimpijskie/p/
Logged in successfully
```

---

### `ranking`

Fetches the ranking from the Szkopul platform and displays it in a formatted table sorted by points.

#### Usage
```bash
python main.py ranking
```

#### Example
```bash
$ python main.py ranking
+---------+----------+--------+
|  Name   | Username | Points |
+---------+----------+--------+
| Alice   | alice123 | 95     |
| Bob     | bob456   | 85     |
+---------+----------+--------+
```

---

### `latest_sub`

Fetches details about the latest submission of the logged-in user.

#### Arguments
- `--url` *(bool, optional)*: Outputs the submission URL.
- `--points` *(bool, optional)*: Outputs the points of the latest submission.

#### Usage
```bash
python main.py latest_sub
```

#### Examples
Get the details in a table:
```bash
$ python main.py latest_sub
+---------------------+--------------------+------+--------+
|      Timestamp      | Submission url    | Task | Points |
+---------------------+--------------------+------+--------+
| 2023-10-01 10:00:00 | https://szkopul...| A    | 90     |
+---------------------+--------------------+------+--------+
```

Get only the URL:
```bash
$ python main.py latest_sub --url
https://szkopul.edu.pl/c/plockie-treningi-olimpijskie/submissions/123
```

---

### `errors`

Checks errors for a specific submission by its URL.

#### Arguments
- `subUrl` *(str)*: The URL of the specific submission to check for errors.

#### Usage
```bash
python main.py errors --subUrl <submission_url>
```

#### Example
```bash
$ python main.py errors --subUrl https://szkopul.edu.pl/c/plockie-treningi-olimpijskie/submissions/123
+-------+------+---------------------------+
| Error | Line | Message                   |
+-------+------+---------------------------+
| E001  | 5    | Syntax error              |
| E002  | 15   | Missing semicolon         |
+-------+------+---------------------------+
```

---

### `get_tasks`

Fetches and displays a list of tasks from Szkopul. Can filter tasks based on completion status or specific task/subtask URLs.

#### Arguments
- `--only_not_completed` *(bool, optional)*: Fetches only tasks that are not completed.
- `--subUrl` *(str, optional)*: Filters for a specific subtask by its short name.
- `--taskUrl` *(str, optional)*: Filters for a specific task by its short name.

#### Usage
```bash
python main.py get_tasks
```

#### Examples
Display all tasks:
```bash
$ python main.py get_tasks
+-----------+---------------+--------+-------------------+-------------------+-----------+
| Task code | Task          | Points | Submissions left  | Task url          | Submit    |
+-----------+---------------+--------+-------------------+-------------------+-----------+
| 101       | Problem Solv. | 50     | 5                 | https://szkopul.. | Yes       |
+-----------+---------------+--------+-------------------+-------------------+-----------+
```

Display only incomplete tasks:
```bash
$ python main.py get_tasks --only_not_completed
```

Filter a specific task:
```bash
$ python main.py get_tasks --taskUrl ant 
```

---

### `submit`

Submits a file for evaluation for a specific task.

#### Arguments
- `subUrl` *(str)*: The submission URL of the task.
- `file` *(str)*: Path to the file to be submitted.
- `filetype` *(str)*: File type, one of `C`, `C++`, `Pascal`, or `python`.

#### Usage
```bash
python main.py submit --subUrl <submission_url> --file <file_path> --filetype <file_type>
```

#### Example
```bash
$ python main.py submit --subUrl https://szkopul.edu.pl/task/123 --file solution.py --filetype python
```

---

## License

This project is licensed under the terms of the MIT License.
