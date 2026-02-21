import sqlite3


def get_cursor():
    con=sqlite3.connect("tasks.db")
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    return con


