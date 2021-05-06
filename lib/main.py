# -------- Discord Imports
import discord
from discord.ext import commands

# -------- MongoDB Imports
from pymongo import MongoClient
from bson.objectid import ObjectId

import utils
import asyncio
from datetime import datetime

# -------- MongoDB inits
myClient = MongoClient('mongodb://localhost:27017')
mydb = myClient["rccs"]

if "rccs" in myClient.list_database_names():
    mydb = myClient["rccs"]
else:
    print('Database by name "rccs" not found')
    exit

todoCol = mydb["todo"]

# -------- Discord inits

TOKEN = ""

with open("token", "r") as file:
    TOKEN = file.read()

bot = commands.Bot(command_prefix="~")

# =========== Commands ==============

# List all todos in the database
@bot.command(name='listall')
async def listTodos(ctx):
    allTodos = utils.cursor_to_list(todoCol.find())

    #Check if any todos exists
    if(len(allTodos) > 0):

        # Format the todos for discord
        todoList = utils.format_todolist(allTodos)

        response = "**All upcoming todos in this server** {0}\n{1}".format(ctx.message.author.mention, todoList)
    else:
        response = "No upcoming todos in this server."

    await ctx.send(response)

# List todos assigned and created by the message author
@bot.command(name='list')
async def listTodos(ctx, index=0):
    creator = ctx.message.author.id

    # Todos assigned to the author
    allTodos = utils.cursor_to_list(todoCol.find({"members": creator}))

    if(index > 0):
        response = allTodos[index]

    else:
        # Check if any exist
        if(len(allTodos) > 0):

            # Format for discord
            todoList = utils.format_todolist(allTodos)

            response = "**Your upcoming todos**\n{0}".format(todoList)
        else:
            response = "No upcoming todos for you. Yayy"

        # Todos created by author
        allTodos = utils.cursor_to_list(todoCol.find({"creator": creator}))

        # Check if any exista
        if(len(allTodos) > 0):

            # Format for discord
            todoList = utils.format_todolist(allTodos)

            response+= "\n\n**Todos created by you** {0}\n{1}".format(ctx.message.author.mention, todoList)


    await ctx.send(response)

# Create new todo
@bot.command(name='add')
async def addTodo(ctx, *members_str):
    creator = ctx.message.author.id
    
    await ctx.send("Type `cancel` to exit and `skip` to skip optional fields.\n\n:grey_question: What is the title of the todo?")

    # Check the whether the reply is given by the author of the command
    def check(m):
        return m.author == ctx.message.author
    
    # Wait for reply and exit if it's 'cancel'
    # !!!! Code is too redundant
    try:
        reply = (await bot.wait_for('message', check=check, timeout=60.0)).content
        if(reply.lower() == "cancel"):
            return
        title = reply
    except asyncio.TimeoutError:
        await ctx.send("Sorry, you took too long to reply")
        return

    await ctx.send(f":white_check_mark: Title is `{title}`\n\n:grey_question: Please give me a brief description about it (optional).")

    # Wait for reply and exit if it's 'cancel'
    try:
        reply = (await bot.wait_for('message', check=check, timeout=60.0)).content
        if(reply.lower() == "cancel"):
            return
        if(reply.lower() == "skip"):
            description = ""
        else:
            description = reply
    except asyncio.TimeoutError:
        await ctx.send("Sorry, you took too long to reply")
        return

    await ctx.send(f":white_check_mark: Description is `{description}`\n\n:grey_question: What project does this relate to? (optional)")

    # Wait for reply and exit if it's 'cancel'
    try:
        reply = (await bot.wait_for('message', check=check, timeout=60.0)).content
        if(reply.lower() == "cancel"):
            return
        if(reply.lower() == "skip"):
            project = ""
        else:
            project = reply
    except asyncio.TimeoutError:
        await ctx.send("Sorry, you took too long to reply")
        return

    await ctx.send(f":white_check_mark: Project is `{project}`\n\n:grey_question: When is the deadline? (DD/MM/YYYY)")

    def check_date(m):
        return check(m) and utils.is_a_date(m.content)

    # Wait for reply and exit if it's 'cancel'
    try:
        reply = (await bot.wait_for('message', check=check_date, timeout=60.0)).content
        if(reply.lower() == "cancel"):
            return
        deadline = datetime.strptime(reply, "%d/%m/%Y")
    except asyncio.TimeoutError:
        await ctx.send("Sorry, you took too long to reply")

    await ctx.send(f":white_check_mark: Deadline is `{deadline.strftime('%d/%m/%Y')}`\n\n:grey_question: Please mention the people you want to assign this to. (optional)")
    members = []
    # Wait for reply and exit if it's 'cancel'
    try:
        reply = (await bot.wait_for('message', check=check, timeout=60.0)).content
        if(reply.lower() == "cancel"):
            return
        if(reply.lower() != "skip"):
            for x in reply.split():
                members.append(await bot.fetch_user(x[3:-1]))
    except asyncio.TimeoutError:
        await ctx.send("Sorry, you took too long to reply")

    members_text = ""
    for x in members:
        members_text+=f"{x}, "
    members_text = members_text[:-2]

    await ctx.send(f":white_check_mark: Members are `{members_text}`\n\n:grey_question: Please list out subtasks of the todo in each line. (optional)")
    subtasks = []
    # Wait for reply and exit if it's 'cancel'
    try:
        reply = (await bot.wait_for('message', check=check, timeout=60.0)).content
        if(reply.lower() == "cancel"):
            return
        if(reply.lower() != "skip"):
            for x in reply.split("\n"):
                subtasks.append(x)
    except asyncio.TimeoutError:
        await ctx.send("Sorry, you took too long to reply")
    
    subtasks_text = ""
    for x in subtasks:
        subtasks_text+=f"{x}, "
    subtasks_text = subtasks_text[:-2]

    messageSent = await ctx.send(f"""Are the following details correct?

:white_small_square: Title - {title}
:white_small_square: Description - {description}
:white_small_square: Project - {project}
:white_small_square: Deadline - {deadline.strftime("%d/%m/%Y")}
:white_small_square: Members - {members_text}
:white_small_square: Subtasks - {subtasks_text}
""")

    await messageSent.add_reaction("✅")
    await messageSent.add_reaction("❌")

    def checkReaction(reaction, user):
        return user == ctx.message.author and (str(reaction.emoji) == "✅" or str(reaction.emoji) == "❌")
    
    try:
        reaction, user = await bot.wait_for('reaction_add', check=checkReaction, timeout=20)
    except asyncio.TimeoutError:
        await ctx.send("Sorry, you took too long to react.")
    
    if(str(reaction.emoji) == "✅"):
        await ctx.send(":white_check_mark: Done, Todo Created")

        subtasksDictArray = []
        for x in subtasks:
            subtasksDictArray.append({"title":x, "completed": False})
        membersDictArray = []
        for x in members:
            membersDictArray.append(x.id)

        newTodoDocument = {
            "title": title,
            "description": description,
            "project": project,
            "deadline": deadline,
            "creator": creator,
            "members": membersDictArray,
            "subtasks": subtasksDictArray
        }

        todoCol.insert_one(newTodoDocument)

        print(f"Todo confirmed: {newTodoDocument}")
    else:
        await ctx.send("Todo Rejected. :x:")
        print("Todo rejected")

# -------- Run the goddamn bot

print("## Starting Bot ##")
bot.run(TOKEN)