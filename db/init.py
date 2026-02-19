from db.connect import get_cursor
from pathlib import Path



def init_db():
    schema_path=Path(__file__).parent/"schema.sql"
    schema=schema_path.read_text()

    con=get_cursor()
    cur=con.cursor()

    cur.executescript(schema)

    con.commit()
    print(f"Db has been initialised")


if __name__=="__main__":
    init_db()
    