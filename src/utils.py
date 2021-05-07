name = "utils"

import pymongo, re, sys, json, logging, discord
import datetime

# -------- MongoDB Imports
from pymongo import MongoClient, errors
from bson.objectid import ObjectId

# -------- Configure logging

LOG_FILE = "logs.log"

with open(LOG_FILE, 'w') as file:
    file.writelines(f"RCCS Team Manager Bot - {str(datetime.datetime.now())}\n\n==============================\n\n")

logging.basicConfig(filename=LOG_FILE, level=logging.INFO)


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

def info(message: str):
    """
    Print and log info message
    """
    print("Info:", message)
    logging.info(message)

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

def get_mongo_config():
    """
    Return todoCol
    """
    config = get_config()
    if("mongo" in config):
        mongo_configs = config["mongo"]
    else:
        err("Field \"mongo\" not found in config.json")
    
    url = mongo_configs["url"]
    db = mongo_configs["db"]

    try:
        myClient = MongoClient(url, serverSelectionTimeoutMS=10000)
    except errors.ServerSelectionTimeoutError as e:
        err(f"MongoDB server timed out. url: {url}")

    # Check whether the db exists in the server
    if db in myClient.list_database_names():
        mydb = myClient[db]
    else:
        err(f'Database by name "{db}" not found')
    
    return mydb["todo"]

# -------- MongoDB inits

todoCol = get_mongo_config()    

def get_discord_config(): 
    """
    Return TOKEN, BOT_PREFIX from utils.get_config()
    """
    config = get_config()
    if("discord" in config):
        discord_configs = config["discord"]
    else:
        err("Field \"discord\" not found in config.json")
    if("token" not in discord_configs):
        err("Key \"token\" not found in config.json.")
        sys.exit(-1)
    token = discord_configs["token"]
    if("prefix" in discord_configs):
        prefix = discord_configs['prefix']
    else:
        prefix = "~"
        warn("Key \"prefix\" not found in config.json. Using default prefix \"prefix\".")
    return token, prefix
    

def format_todo(todo: dict) -> str:
    """
    Formats todo to string
    """

    # Title
    todo_string = f":white_small_square: Title - {todo['title']}"
    
    # Descripttion
    todo_string += f"\n:white_small_square: Description - {todo['description']}"

    # Project
    todo_string += f"\n:white_small_square: Project - {todo['project']}"

    # Deadline
    todo_string += f"\n:white_small_square: Deadline - {todo['deadline'].strftime('%d/%m/%Y')}"   
    
    # Members
    members = todo['members']
    members_string = ""
    for member in members:
        members_string += member + ", "
    
    # Remove the trailing end ", "
    members_string = members_string[:-2]
    todo_string += f"\n:white_small_square: Members - {members_string}"

    # Subtasks
    subtasks = todo['subtasks']
    subtasks_string = "\n\n:white_small_square: Subtasks"
    for subtask in subtasks:
        emoji = ":white_check_mark:" if subtask['completed'] else ":x:"
        if(subtask['completed'] == False):
            subtasks_string += f"\n\t:small_orange_diamond: {subtask['title']}"
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

    # ╔══╦═══════════════════════╦═════════╗
    # ║ ID ║ Title                                                               ║ Deadline           ║
    # ╠══╬═══════════════════════╬═════════╣
    # ║ 01 ║ Hi                                                                   ║  23/04/2021   ║
    # ║  1 ║
    # ╚══╩═══════════════════════╩═════════╝

    todo_list = "╔══╦═══════════════════════╦═════════╗\n║ ID ║ **Title**                                                              ║ **Deadline**           ║\n╠══╬═══════════════════════╬═════════╣"
    i = 1
    # Format the todos for discord
    for x in all_todos:
        if (len(x['title']) > 38):
            title_text = x['title'][:35] + "..."
        else:
            title_text = x['title'] + " " * (68 - len(x['title']))
        
        id_str = str(i)
        if (id_str[-1] == '1'):
            id_str += " "

        todo_list += f"\n║ {'   ' if (i < 10) else '' }{id_str}║ {title_text} ║  {x['deadline'].strftime('%d/%m/%Y')}   ║"
        # todo_list += f"\n**{i}.** {x['title']} - `{x['deadline'].strftime('%d/%m/%Y')}`"
        i += 1
    todo_list += "\n╚══╩═══════════════════════╩═════════╝"
    return todo_list

def add_todo(
    title: str, 
    description: str, 
    project: str, 
    deadline: datetime.datetime, 
    creator: int, 
    members: list, 
    subtasks: list):
    """
    Create and add a todo document in the mongodb collection.
    """

    subtasksDictArray = []
    for x in subtasks:
        subtasksDictArray.append({"title": x, "completed": False, "time": None, "user": None})
    membersDictArray = []
    for x in members:
        membersDictArray.append(x.id)

    newTodoDocument = {
        "title": title,
        "description": description,
        "project": project,
        "deadline": deadline,
        "creator": creator,
        "completed": False,
        "members": membersDictArray,
        "subtasks": subtasksDictArray
    }

    todoCol.insert_one(newTodoDocument)
    print(newTodoDocument)

def complete_todo(id: ObjectId, user: discord.User):
    """
    Mark a todo document as completed
    """

    todoCol.update_one({"_id": id}, {"$set" : {"completed": True, "completed_by": user.id}})


def get_todos(filter: dict = {}) -> list:
    """
    Get documents from the todo collection which matches the filter given.
    """
    return cursor_to_list(todoCol.find(filter))

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
            date = deadline = datetime.datetime.strptime(string, "%d/%m/%Y")
        except ValueError:
            return False
        else:
            return True
    return False

