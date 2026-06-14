import os
import sys

script_dir = r"D:\aiphxt-app\ai-service"
os.chdir(script_dir)
sys.path.insert(0, script_dir)

db_path = os.path.join(script_dir, "app.db")
print(f"Database path: {db_path}")
print(f"Exists: {os.path.exists(db_path)}")
print()

if os.path.exists(db_path):
    import sqlite3
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("=== Tables in database:")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    for table in tables:
        print(f"  - {table[0]}")

    print()
    print("=== Users table:")
    try:
        cursor.execute("SELECT * FROM users;")
        columns = [description[0] for description in cursor.description]
        print(f"  Columns: {columns}")
        rows = cursor.fetchall()
        print(f"  Total users: {len(rows)}")
        for row in rows:
            print(f"    {row}")
    except Exception as e:
        print(f"  ERROR: {e}")

    conn.close()
else:
    print("Database does not exist")
