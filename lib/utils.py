import pymongo


def format_todo(all_todos: pymongo.collection.Cursor) -> str:
    todo_list = ""
    i = 1
    # Format the todos for discord
    for x in all_todos:
        todo_list += f"\n**{i}.** {x['title']} - `{x['deadline']}`"
        i += 1
    return todo_list


def cursor_to_list(cursor: pymongo.collection.Cursor, properties: [str]):
    """
    converts cursor to list.

    :parameter properties: should be a array of string indexes
    """

    v = []
    for x in cursor:
        v2 = []
        for c_property in properties:
            v2.append(x[c_property])

        v.append(v2)
    return v
