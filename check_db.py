import sqlite3
import os

db_path = 'db.sqlite3'
if not os.path.exists(db_path):
    print(f"Error: {db_path} not found.")
else:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM api_job LIMIT 5;")
        rows = cursor.fetchall()
        print(f"Success! Found {len(rows)} jobs in database.")
        for row in rows:
            print(row)
    except Exception as e:
        print(f"Error executing query: {e}")
    finally:
        conn.close()
