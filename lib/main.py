# -------- Discord Imports
import discord
from discord.ext import commands

# -------- MongoDB Imports
from pymongo import MongoClient
from bson.objectid import ObjectId

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

bot = commands.Bot(command_prefix="&")

# =========== Commands ==============

# List all todos in the database
@bot.command(name='listall')
async def listTodos(ctx):
    allTodos = todoCol.find()

    #Check if any todos exists
    if(todoCol.count_documents({}) > 0):
        todoList = ""
        i=1

        # Format the todos for discord
        for x in allTodos:
            todoList += f"\n**{i}.** {x['title']} - `{x['deadline']}`"
            i+=1

        response = "**All upcoming todos in this server** {0}\n{1}".format(ctx.message.author.mention, todoList)
    else:
        response = "No upcoming todos in this server."

    await ctx.send(response)

# List todos assigned and created by the message author
@bot.command(name='list')
async def listTodos(ctx):
    creator = ctx.message.author.id

    # Todos assigned to the author
    allTodos = todoCol.find({"members": creator})

    # Check if any exist
    if(todoCol.count_documents({"members": creator}) > 0):
        todoList = ""
        i=1

        # Format for discord
        for x in allTodos:
            todoList += f"\n**{i}.** {x['title']} - `{x['deadline']}`"
            i+=1

        response = "**Your upcoming todos** {0}\n{1}".format(ctx.message.author.mention, todoList)
    else:
        response = "No upcoming todos for you. Yayy"

    # Todos created by author
    allTodos = todoCol.find({"creator": creator})

    # Check if any exist
    if(todoCol.count_documents({"creator": creator}) > 0):
        todoList = ""
        i=1

        # Format for discord
        for x in allTodos:
            todoList += f"\n**{i}.** {x['title']} - `{x['deadline']}`"
            i+=1

        response+= "\n\n**Todos created by you** {0}\n{1}".format(ctx.message.author.mention, todoList)


    

    await ctx.send(response)

# Call someone (For fun)
@bot.command(name="call")
async def call(ctx, user: discord.Member = None):
    if user:
        await ctx.send(f"Pss pss, {user.mention}")
    else:
        await ctx.send("Who you wanna call?")

# -------- Run the goddamn bot

bot.run(TOKEN)