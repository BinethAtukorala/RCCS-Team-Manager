name = "utils"

import pymongo, re, sys, json, logging
from datetime import datetime

# Configure logging
logging.basicConfig(filename="logs", level=logging.INFO)

def err(message: str):
    print("Error:", message)
    logging.error(message)
    sys.exit(-1)

def warn(message: str):
    print("Warning:", message)
    logging.warning(message)

def get_config():
    try: 
        with open("config.json", "r") as myfile:
            data=myfile.read()
        return json.loads(data)
    except FileNotFoundError:
        err("File \"config.json\" not found!")

def format_todolist(all_todos: list) -> str:
    """
    format list object of todos.
    """
    todo_list = ""
    i = 1
    # Format the todos for discord
    for x in all_todos:
        todo_list += f"\n**{i}.** {x['title']} - `{x['deadline']}`"
        i += 1
    return todo_list


def cursor_to_list(cursor: pymongo.collection.Cursor):
    """
    converts pymongo.collection.Cursor object to list.

    """

    v = []  # Output list
    for x in cursor:
        v.append(x)
    return v

def is_a_date(string: str) -> bool:
    """
    Returns True if the provided string is in the correct format.
    """
    date_re = re.compile(r"\d\d/\d\d/\d\d\d\d")
    if(date_re.match(string) != None):
        try:
            date = deadline = datetime.strptime(string, "%d/%m/%Y")
        except ValueError:
            return False
        else:
            return True
    return False

