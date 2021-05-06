name = "utils"

import pymongo, re, sys, json, logging
from datetime import datetime

# Configure logging
logging.basicConfig(filename="logs.log", level=logging.INFO)

def err(message: str):
    """
    Print and log error. Exits the program
    """
    print("Error:", message)
    logging.error(message)
    sys.exit(-1)

def warn(message: str):
    """
    Print and log warning message
    """
    print("Warning:", message)
    logging.warning(message)

def get_config():
    """
    Read /config.json and return it's content as a dictionary
    """
    try: 
        with open("config.json", "r") as myfile:
            data=myfile.read()
        return json.loads(data)
    except FileNotFoundError:
        err("File \"config.json\" not found!")

def format_todo(todo: dict) -> str:
    """
    Formats todo to string
    """

    # Title
    todo_string = f":white_small_square: Title - {todo['title']}"
    
    # Descripttion
    todo_string += f"\n:white_small_square: Description - {todo['description']}"

    # Project
    todo_string += f"\n:white_small_square: Description - {todo['project']}"

    # Deadline
    todo_string += f"\n:white_small_square: Deadline - {todo['deadline'].strftime('%d/%m/%Y')}"   
    
    # Members
    members = todo['members']
    members_string = ""
    for member in members:
        members_string += member + ", "
    members_string = members_string[:-2]
    todo_string += f"\n:white_small_square: Members - {members_string}"

    # Subtasks
    subtasks = todo['subtasks']
    subtasks_string = "\n\n:white_small_square: Subtasks"
    for subtask in subtasks:
        emoji = ":white_check_mark:" if subtask['completed'] else ":x:"
        subtasks_string += f"\n\t:small_orange_diamond: {subtask['title']}:\t{emoji}"
    todo_string += subtasks_string

#     todo_string = (f"""
# :white_small_square: Title - {todo["title"]}
# :white_small_square: Description - {todo["description"]}
# :white_small_square: Project - {todo["project"]}
# :white_small_square: Deadline - {todo["deadline"].strftime("%d/%m/%Y")}
# :white_small_square: Members - {todo["members"]}
# :white_small_square: Subtasks - {todo["subtasks"]}
# """)

    return todo_string

def format_todolist(all_todos: list) -> str:
    """
    Format list object of todos.
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
    Converts pymongo.collection.Cursor object to list.

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

