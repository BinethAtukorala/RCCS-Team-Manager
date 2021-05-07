# -------- Discord Imports
import discord
from discord.ext import commands

# -------- MongoDB Imports
from pymongo import MongoClient
from bson.objectid import ObjectId

import utils

import asyncio
from datetime import datetime

# -------- Discord inits

TOKEN, BOT_PREFIX = utils.get_discord_config()
    
bot = commands.Bot( command_prefix = BOT_PREFIX )

# =========== Commands ==============

@bot.event
async def on_ready():
    print("Connected to servers: ")
    guilds = await bot.fetch_guilds(limit=100).flatten()
    for guild in guilds:
        print(guild.name)
    await bot.change_presence(status=discord.Status.online, activity=discord.Game("📑 Todo Crunch"))

# List all todos in the database
@bot.command(name='listall')
async def listAllTodos(ctx):
    allTodos = utils.get_todos({"completed": False})

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
    allTodosToAuthor = utils.cursor_to_list(utils.get_todos({"members": creator, "completed": False}))

    #Todos created by author
    allTodosByAuthor = utils.get_todos({"creator": creator, "completed": False, "members": {'$ne': creator} })

    # Respond with the info of a specific todo if an index is given
    if(index > 0 and (len(allTodosToAuthor) >= index or len(allTodosByAuthor) <= index)):

        # Check which list does the index refer to
        if(len(allTodosToAuthor) >= index):
            todo = allTodosToAuthor[index-1]
        elif(len(allTodosByAuthor) <= index):
            todo = allTodosByAuthor[index-1]

        members = []
        for x in todo['members']:
            user = await bot.fetch_user(x)
            members.append(user.name + "#" + user.discriminator)
        todo['members'] = members
        
        response = utils.format_todo(todo)

        messageSent = await ctx.send(response)

        await messageSent.add_reaction("✅")

        def checkReaction(reaction, user):
            return user == ctx.message.author and (str(reaction.emoji) == "✅")
        
        try:
            reaction, user = await bot.wait_for('reaction_add', check=checkReaction, timeout=20)
            if(str(reaction.emoji) == "✅"):
                utils.complete_todo(todo["_id"], user)
                await ctx.send("✅ Marked as completed!")
        except asyncio.TimeoutError:
            await messageSent.remove_reaction("✅", bot.user)

    
    # List all todos if no index is given
    else:
        i = 0
        # Check if any exist

        # Check if any exista
        if(len(allTodosByAuthor) > 0):

            # Format for discord
            todoList = utils.format_todolist(allTodosByAuthor)

            await ctx.send("**Todos assigned to others by you** {0}\n{1}\n\n".format(ctx.message.author.mention, todoList))

        if(len(allTodosToAuthor) > 0):

            await ctx.send("**\nYour upcoming todos\n**")

            # Create coroutine to handle reactions of the messages, because otherwise the next message wouldn't be shown before the reaction check is done
            async def message_task(i:int, todo: dict, message):
                await message.add_reaction("✅")

                def checkReaction(reaction, user):
                    return user == ctx.message.author and (str(reaction.emoji) == "✅") and reaction.message == message
                
                try:
                    reaction, user = await bot.wait_for('reaction_add', check=checkReaction, timeout=20)
                    if(str(reaction.emoji) == "✅"):
                        utils.complete_todo(todo["_id"], user)
                        await ctx.send(f"✅ Marked as completed! - **{i}.** {todo['title']}")
                except asyncio.TimeoutError:
                    await message.remove_reaction("✅", bot.user)
            # A list to store all coroutines
            messages = list()

            await ctx.send("╔══╦═══════════════════════╦═════════╗\n║ ID ║ **Title**                                                              ║ **Deadline**           ║\n╠══╬═══════════════════════╬═════════╣")

            for todo in allTodosToAuthor:
                title = todo['title']
                i += 1
                if (len(title) > 38):
                    title_text = title[:35] + "..."
                else:
                    title_text = title + " " * (68 - len(title))

                id_str = str(i)
                if (id_str[-1] == '1'):
                    id_str += " "

                # Sending the message outside the coroutine to maintain message number ordering
                message = await ctx.send(f"\n║ {'   ' if (i < 10) else '' }{id_str}║ {title_text} ║  {todo['deadline'].strftime('%d/%m/%Y')}   ║")
                messages.append(message_task(i, todo, message))
            await ctx.send("\n╚══╩═══════════════════════╩═════════╝")
            # Wait for the reactions to be done
            asyncio.run_coroutine_threadsafe(asyncio.wait(messages, return_when=asyncio.ALL_COMPLETED), asyncio.get_event_loop())

        else:
            await ctx.send("No upcoming todos for you. Yayy")

        

# Create new todo
@bot.command(name='add')
async def addTodo(ctx, *members_str):
    creator = ctx.message.author.id
    
    await ctx.send("Type `cancel` to exit and `skip` to skip optional fields.\n\n:grey_question: What is the title of the todo?")

    # Check the whether the reply is given by the author of the command
    def check(m):
        return m.author == ctx.message.author
    
    # Wait for reply and exit if it's 'cancel'
    # TODO: Code is too redundant
    try:
        reply = (await bot.wait_for('message', check=check, timeout=60.0)).content
        if(reply.lower() == "cancel"):
            await ctx.send(":no_entry: Canceled!")
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
            await ctx.send(":no_entry: Canceled!")
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
            await ctx.send(":no_entry: Canceled!")
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
            await ctx.send(":no_entry: Canceled!")
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
            await ctx.send(":no_entry: Canceled!")
            return
        if(reply.lower() != "skip"):
            for x in reply.split():
                members.append(await bot.fetch_user(x[3:-1]))
    except asyncio.TimeoutError:
        await ctx.send("Sorry, you took too long to reply")

    members_text = ""
    if(len(members) > 0):
        for x in members:   
            members_text+=f"{x}, "
        members_text = members_text[:-2]
    members_text = "not given."

    await ctx.send(f":white_check_mark: Members are {members_text}\n\n:grey_question: Please list out subtasks of the todo in each line. (optional)")
    subtasks = []
    # Wait for reply and exit if it's 'cancel'
    try:
        reply = (await bot.wait_for('message', check=check, timeout=60.0)).content
        if(reply.lower() == "cancel"):
            await ctx.send(":no_entry: Canceled!")
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
    message = "Are the following details correct?\n"
    message += f"\n:white_small_square: Title - {title}"
    message += f"\n:white_small_square: Description - {description}"
    message += f"\n:white_small_square: Deadline - {deadline.strftime('%d/%m/%Y')}"
    message += f"\n:white_small_square: Members - {members_text}"
    message += f"\n:white_small_square: Subtasks - {subtasks_text}"

    messageSent = await ctx.send(message)

    await messageSent.add_reaction("✅")
    await messageSent.add_reaction("❌")

    def checkReaction(reaction, user):
        return user == ctx.message.author and (str(reaction.emoji) == "✅" or str(reaction.emoji) == "❌")
    
    try:
        reaction, user = await bot.wait_for('reaction_add', check=checkReaction, timeout=20)
    except asyncio.TimeoutError:
        await ctx.send("Sorry, you took too long to react.")
    
    if(str(reaction.emoji) == "✅"):

        utils.add_todo(title, description, project, deadline, creator, members, subtasks)

        await ctx.send(":white_check_mark: Done, Todo Created")
        
    else:
        await ctx.send("Todo Rejected. :x:")
        print("Todo rejected")

# -------- Run the goddamn bot

print("## Starting Bot ##")
bot.run(TOKEN)