import discord
import asyncio
from discord.ext import commands

from datetime import datetime

from lib import utils

class Todo(commands.Cog):
    """
    Todo commands
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='listall')
    async def list_all_todos(self, ctx):
        """List all the todos in the database"""
        all_todos = utils.get_todos({"completed": False})

        #Check if any todos exists
        if(len(all_todos) > 0):

            # Format the todos for discord
            todoList = utils.format_todolist(all_todos)

            response = "**All upcoming todos in this server** {0}\n{1}".format(ctx.message.author.mention, todoList)
        else:
            response = "No upcoming todos in this server."

        await ctx.send(response)

    @commands.command(name='list')
    async def list_todos(self, ctx, index=0):
        """List todos assigned to or created by the user.\n\
        `list <ID>` - Show more information of a specific todo."""
        creator = ctx.message.author.id

        # Todos assigned to the author
        all_todos_to_author = utils.cursor_to_list(utils.get_todos({"members": creator, "completed": False}))

        #Todos created by author
        all_todos_by_author = utils.get_todos({"creator": creator, "completed": False, "members": {'$ne': creator} })

        # Respond with the info of a specific todo if an index is given
        if(index > 0 and (len(all_todos_to_author) >= index or len(all_todos_by_author) <= index)):

            # Check which list does the index refer to
            if(len(all_todos_to_author) >= index):
                todo = all_todos_to_author[index-1]

            elif(len(all_todos_by_author) <= index):
                todo = all_todos_by_author[index-1]

            members = list()
            for x in todo['members']:
                user = await self.bot.fetch_user(x)
                members.append(user.name + "#" + user.discriminator)
            todo['members'] = members
            
            response = utils.format_todo(todo)

            message_sent = await ctx.send(response)

            await message_sent.add_reaction("✅")

            def checkReaction(reaction, user):
                return user == ctx.message.author and (str(reaction.emoji) == "✅")
            
            try:
                reaction, user = await self.bot.wait_for('reaction_add', check=checkReaction, timeout=20)
                if(str(reaction.emoji) == "✅"):
                    utils.complete_todo(todo["_id"], user)
                    await ctx.send("✅ Marked as completed!")
            except asyncio.TimeoutError:
                await message_sent.remove_reaction("✅", self.bot.user)

        
        # List all todos if no index is given
        else:
            i = 0

            # Check if any exists
            if(len(all_todos_by_author) > 0): 

                todoList = utils.format_todolist(all_todos_by_author) # Format for discord

                await ctx.send("**Todos assigned to others by you** {0}\n{1}\n\n".format(ctx.message.author.mention, todoList))

            if(len(all_todos_to_author) > 0):

                await ctx.send("**\nYour upcoming todos\n**")

                # Create coroutine to handle reactions of the messages
                # because otherwise the next message wouldn't be shown before the reaction check is done
                
                    
                async def message_task(i:int, todo: dict, message):
                    await message.add_reaction("✅")                    
                    
                    def checkReaction(reaction, user):
                        return user == ctx.message.author and (str(reaction.emoji) == "✅") and reaction.message == message

                    try:
                        reaction, user = await self.bot.wait_for('reaction_add', check=checkReaction, timeout=20)
                        if(str(reaction.emoji) == "✅"):
                            utils.complete_todo(todo["_id"], user)
                            await ctx.send(f"✅ Marked as completed! - **{i}.** {todo['title']}")
                            await message.remove_reaction("✅", self.bot.user)
                            await message.remove_reaction("✅", ctx.message.author)
                    except asyncio.TimeoutError:
                        await message.remove_reaction("✅", self.bot.user)
                
                messages_coroutines = list()

                await ctx.send("╔══╦═══════════════════════╦═════════╗\n║ ID ║ **Title**                                                              ║ **Deadline**           ║\n╠══╬═══════════════════════╬═════════╣")

                for todo in all_todos_to_author:
                    title = todo['title']
                    i += 1
                    if (len(title) > 38):
                        title_text = title[:35] + "..."
                    else:
                        title_text = title + " " * (68 - len(title))

                    id_str = str(i)
                    if id_str.endswith('1'):
                        id_str += " "

                    # Sending the message outside the coroutine to maintain message number ordering
                    message = await ctx.send(f"\n║ {'   ' if (i < 10) else '' }{id_str} ║ {title_text} ║  {todo['deadline'].strftime('%d/%m/%Y')}   ║")

                    messages_coroutines.append(message_task(i, todo, message))

                await ctx.send("\n╚══╩═══════════════════════╩═════════╝")
                
                asyncio.run_coroutine_threadsafe(asyncio.wait(messages_coroutines, return_when=asyncio.ALL_COMPLETED), # Wait for the reactions to be done
                                                asyncio.get_event_loop())

            else:
                await ctx.send("No upcoming todos for you. Yayy")
    
    @commands.command(name='add')
    async def addTodo(self, ctx, *members_str):
        """Add a new todo to the database"""
        creator = ctx.message.author.id
        
        await ctx.send("Type `cancel` to exit and `skip` to skip optional fields.\n\n"
                        + ":grey_question: What is the title of the todo?")

        # Check the whether the reply is given by the author of the command
        def check(m):
            return m.author == ctx.message.author
        
        # Wait for reply and exit if it's 'cancel'
        # TODO: Code is too redundant
        try:
            reply = (await self.bot.wait_for('message', check=check, timeout=60.0)).content

            title = reply
        except asyncio.TimeoutError:
            await ctx.send("Sorry, you took too long to reply")
            return

        await ctx.send(f":white_check_mark: Title is `{title}`\n\n:grey_question: Please give me a brief description about it (optional).")

        # Wait for reply and exit if it's 'cancel'
        try:
            reply = (await self.bot.wait_for('message', check=check, timeout=60.0)).content

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
            reply = (await self.bot.wait_for('message', check=check, timeout=60.0)).content

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

        await ctx.send(f":white_check_mark: Project is `{project}`\n\n"
                        + ":grey_question: When is the deadline? (DD/MM/YYYY)")

        # Wait for reply and exit if it's 'cancel'

        async def get_deadline(bot):
            try:
                reply = (await bot.wait_for('message', check=check, timeout=60.0)).content

                if(reply.lower() == "cancel"):
                    await ctx.send(":no_entry: Canceled!")
                    return None

                reply.replace("-", "/")
                reply.replace(".", "/")

                if(utils.is_a_date(reply)):
                    return datetime.strptime(reply, "%d/%m/%Y")
                else:
                    await ctx.send("Uhh... That doesn't look like a valid date.\nDeadline should be in the format (DD/MM/YYYY). Please enter the date again.")
                    return await get_deadline(bot)

            except asyncio.TimeoutError:
                await ctx.send("Sorry, you took too long to reply")
                return None

        deadline = await get_deadline(self.bot)

        if(deadline == None):
            return

        await ctx.send(f":white_check_mark: Deadline is `{deadline.strftime('%d/%m/%Y')}`\n\n:grey_question: Please mention the people you want to assign this to. (optional)")

        members = list()
        # Wait for reply and exit if it's 'cancel'
        try:
            reply = (await self.bot.wait_for('message', check=check, timeout=60.0)).content

            if(reply.lower() == "cancel"):
                await ctx.send(":no_entry: Canceled!")
                return

            if(reply.lower() != "skip"):
                for x in reply.split():
                    members.append(await self.fetch_user(x[3:-1]))

        except asyncio.TimeoutError:
            await ctx.send("Sorry, you took too long to reply")

        members_text = ""
        if(len(members) > 0):
            for x in members:   
                members_text+=f"{x}, "
            members_text = members_text[:-2]
        members_text = "not given."

        await ctx.send(f":white_check_mark: Members are {members_text}\n\n:grey_question: Please list out subtasks of the todo in each line. (optional)")
        subtasks = list()
        # Wait for reply and exit if it's 'cancel'
        try:
            reply = (await self.bot.wait_for('message', check=check, timeout=60.0)).content

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
        message = f"Are the following details correct?\n\n"
        message += f":white_small_square: Title - {title}\n"
        message += f":white_small_square: Description - {description}\n" if description else ""
        message += f":white_small_square: Deadline - {deadline.strftime('%d/%m/%Y')}\n"
        message += f":white_small_square: Members - {members_text}\n" if members_text != "not given." else ""
        message += f":white_small_square: Subtasks - {subtasks_text}" if subtasks_text else ""

        message_sent = await ctx.send(message)

        await message_sent.add_reaction("✅")
        await message_sent.add_reaction("❌")

        def checkReaction(reaction, user):
            return user == ctx.message.author and (str(reaction.emoji) == "✅" or str(reaction.emoji) == "❌")
        
        try:
            reaction, user = await self.bot.wait_for('reaction_add', check=checkReaction, timeout=20)
        except asyncio.TimeoutError:
            await ctx.send("Sorry, you took too long to react.")
        
        if(str(reaction.emoji) == "✅"):
            utils.add_todo(title, description, project, deadline, creator, members, subtasks)

            await ctx.send(":white_check_mark: Done, Todo Created")
            
        else:
            await ctx.send("Todo Rejected. :x:")
            print("Todo rejected")
        
        await message_sent.remove_reaction("✅", self.bot.user)
        await message_sent.remove_reaction("❌", self.bot.user)

def setup(bot):
    bot.add_cog(Todo(bot))