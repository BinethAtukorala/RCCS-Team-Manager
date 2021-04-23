import pymongo


def format_todo(all_todos: list) -> str:
    todo_list = ""
    i = 1
    # Format the todos for discord
    for x in all_todos:
        todo_list += f"\n**{i}.** {x['title']} - `{x['deadline']}`"
        i += 1
    return todo_list


def cursor_to_list(cursor: pymongo.collection.Cursor):
    """
    converts cursor to list.

    """

    v = []  # Output list
    for x in cursor:
        v.append(x)
    return v
