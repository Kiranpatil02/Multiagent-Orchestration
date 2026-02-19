import sqlite3


def get_cursor():
    con=sqlite3.connect("tasks.db")
    con.execute("PRAGMA foreign_keys = ON")
    cursor=con.cursor()
    return cursor


