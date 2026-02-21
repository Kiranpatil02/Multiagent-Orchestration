from db.connect import get_cursor
from pathlib import Path



def init_db():
    con=get_cursor()
    try:
        with open('db/schema.sql','r') as f:
            schema=f.read()
        con.executescript(schema)
        con.commit()
        print("DB initialsed...")
    except Exception as e:
        print(f"Error in DB: {str(e)}")
        raise
    
