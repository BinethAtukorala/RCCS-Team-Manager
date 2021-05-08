import pymongo
import re
import sys
import json
import logging
import datetime
import os
import pprint

import discord
from discord.ext import commands

# -------- MongoDB Imports
from pymongo import MongoClient, errors
from bson.objectid import ObjectId

# -------- Configure logging

LOG_FILE = "logs.log"

with open(LOG_FILE, 'w') as f:
    f.writelines(f"RCCS Team Manager Bot - {str(datetime.datetime.now())}\n\n==============================\n\n")

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

def debug(message: str):
    """
    Print and log debug message
    """
    if(get_config()["debug"]):
        print("Debug:", message)    
        logging.debug(message)

def create_config():
    print("\nConfiguration\n")
    
    print(" - Discord")
    token = input("Enter Discord bot token : ")
    prefix = input("Enter prefix for bot (Default '~') : ") or "~"

    print(" - MongoDB")
    url = input("Enter url for MongoDB : ")
    db = input("Enter database name : ")

    config = {
        "discord": {
            "token": token,
            "prefix": prefix
        },
        "mongo": {
            "url": url,
            "db": db
        }
    }

    with open('config.json', 'w') as f:
        t = json.dumps(config, indent=4)
        t = re.sub('\[\n {7}', '[', t)
        t = re.sub('(?<!\]),\n {7}', ',', t)
        t = re.sub('\n {4}\]', ']', t)
        f.write(t)

def recreate_config():
    create_config()
    todoCol = get_mongo_config()
    info("Please restart to update config.json...")
    sys.exit(-1)

def get_config():
    """
    Read /config.json and return it's content as a dictionary
    """
    try: 
        with open("config.json", "r") as f:
            data = f.read()
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
        warn("Field \"mongo\" not found in config.json")
        recreate_config() if (input("Do you want to recreate config.json? (y/n): ") == "y") else err("config.json - Field not found")
    
    if("url" in mongo_configs and "db" in mongo_configs):
        url = mongo_configs["url"]
        db = mongo_configs["db"]
    else:
        warn("Field not found in config.json")
        recreate_config() if (input("Do you want to recreate config.json? (y/n): ") == "y") else err("config.json - Field not found")

    try:
        my_client = MongoClient(url, serverSelectionTimeoutMS=10000)
    except errors.ServerSelectionTimeoutError as e:
        err(f"MongoDB server timed out. url: {url}")

    # Check whether the db exists in the server
    if db in my_client.list_database_names():
        mydb = my_client[db]
    else:
        warn(f'Database by name "{db}" not found')
        recreate_config() if (input("Do you want to recreate config.json? (y/n): ") == "y") else err("config.json - Field not found")
    
    return mydb["todo"]

# -------- MongoDB inits

# if not os.path.isfile("config.json"):  
#     warn("File config.json not found.")  
#     create_config()

todoCol = get_mongo_config()

def get_discord_config(): 
    """
    Return TOKEN, BOT_PREFIX from utils.get_config()
    """
    config = get_config()
    
    if("discord" in config):
        discord_configs = config["discord"]  
    else:
        warn("Field \"discord\" not found in config.json")
        recreate_config() if (input("Do you want to recreate config.json? (y/n): ") == "y") else err("config.json - Field not found")
    
    if("token" not in discord_configs):
        warn("Key \"token\" not found in config.json.")
        recreate_config() if (input("Do you want to recreate config.json? (y/n): ") == "y") else err("config.json - Field not found")
        sys.exit(-1)
    
    token = discord_configs["token"]
    
    if("prefix" in discord_configs):
        prefix = discord_configs['prefix'] 
    else:
        prefix = "~"
        warn("Key \"prefix\" not found in config.json. Using default prefix \"prefix\".")

    return token, prefix

async def format_todo_for_embed(todo: dict, bot) -> discord.Embed:
    """
    Formats todo to a dict to be used in an embed.
    """
    # Title and Description
    emb = discord.Embed(title=f"TODO - {todo['title']}",
                        description=todo['description'],
                        color=discord.Color.dark_gray())

    # Project
    if todo['project']:
        emb.add_field(name="◽ Project", value=todo['project'], inline=False)

    # Deadline
    emb.add_field(name="◽ Deadline", value=todo['deadline'].strftime("%Y-%m-%d"), inline=False)

    # Members
    members = todo['members']
    members_string = ""
    for member in members:
        members_string +=  f"▫ {await bot.fetch_user(member)}\n"
    if members_string != "":
        emb.add_field(name="◽ Members", value=members_string, inline=False)
    
    # Subtasks
    subtasks = todo['subtasks']
    subtasks_string = ""
    for subtask in subtasks:
        emoji = ":white_check_mark:" if subtask['completed'] else ":x:"
        if(subtask['completed'] == False):
            subtasks_string += f"▫ {subtask['title']}\n"
    
    if subtasks_string != "":
        emb.add_field(name="◽ Subtasks", value=subtasks_string, inline=False)
    
    emb.set_footer(text=f"- Royal College Computer Society '21")

    return emb


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
    todo_string += f"\n:white_small_square: Deadline - {todo['deadline'].strftime('%Y-%m-%d')}"   
    
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
        if id_str.endswith('1'):
            id_str += " "

        todo_list += f"\n║ {'   ' if (i < 10) else '' }{id_str}║ {title_text} ║  {x['deadline'].strftime('%Y-%m-%d')}   ║"
        # todo_list += f"\n**{i}.** {x['title']} - `{x['deadline'].strftime('%Y-%m-%d')}`"
        i += 1
    todo_list += "\n╚══╩═══════════════════════╩═════════╝"
    return todo_list

def format_todolist_for_embed(emb_title: str, all_todos: list) -> discord.Embed:
    """
    Format list object of todos and return a `discord.Embed` object.
    """
    letters = [
            "🇦",
            "🇧",
            "🇨",
            "🇩",
            "🇪",
            "🇫",
            "🇬",
            "🇭"      
            ]

    todos = list()
    x = 0
    for todo in all_todos:
        x += 1
        title = letters[x-1] + " " + todo['title']
        deadline = todo['deadline'].strftime('%Y-%m-%d')
        todos.append(
            {
                "title": title, 
                "deadline": deadline, 
                "description": todo['description'] if todo['description'] != "" else "No description."
            }
        )

    if(len(all_todos) > 0):

        emb = discord.Embed(title=emb_title,
                            color=discord.Color.gold())
        
        for todo in todos:
            emb.add_field(
                name=todo["title"] + " - `" + todo["deadline"] + "`", 
                value=todo["description"], 
                inline=False
                )
        
    else:
        emb = discord.Embed(title="No upcoming todos in the server",
                            color=discord.Color.gold())

    emb.set_footer(text=f"- Royal College Computer Society '21")

    return emb

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

    subtasks_dict_array = list()
    for x in subtasks:
        subtasks_dict_array.append({"title": x, "completed": False, "time": None, "user": None})
    members_dict_array = list()
    for x in members:
        members_dict_array.append(x.id)

    new_todo_document = {
        "title": title,
        "description": description,
        "project": project,
        "deadline": deadline,
        "creator": creator,
        "completed": False,
        "members": members_dict_array,
        "subtasks": subtasks_dict_array
    }

    todoCol.insert_one(new_todo_document)
    print(new_todo_document)

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
    v = list()  # Output list
    for x in cursor:
        v.append(x)
    return v

def is_a_date(string: str) -> bool:
    """
    Returns True if the provided string is in the correct format.
    """
    date_re = re.compile(r"\d\d\d\d-\d\d-\d\d")
    if(date_re.match(string) != None):
        try:
            date = deadline = datetime.datetime.strptime(string, "%Y-%m-%d")
        except ValueError:
            return False
        else:
            return True
    return False

