import sqlite3

def initialize_database():
    try:
        # Connect to the SQLite database (this will create the db if it doesn't exist)
        conn = sqlite3.connect("streamsmart.db")
        cursor = conn.cursor()

        # Create the users table if it doesn't exist
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            mobile TEXT NOT NULL,
            date_of_birth TEXT NOT NULL,
            height INTEGER NOT NULL,
            weight INTEGER NOT NULL,
            gender TEXT NOT NULL,
            password TEXT NOT NULL
        )''')

        # Check if the necessary columns exist and add them if missing
        cursor.execute("PRAGMA table_info(users);")
        columns = cursor.fetchall()

        column_names = [column[1] for column in columns]
        
        if "date_of_birth" not in column_names:
            cursor.execute("ALTER TABLE users ADD COLUMN date_of_birth TEXT;")
            print("Column 'date_of_birth' added to 'users' table.")
        
        if "height" not in column_names:
            cursor.execute("ALTER TABLE users ADD COLUMN height INTEGER;")
            print("Column 'height' added to 'users' table.")
        
        if "weight" not in column_names:
            cursor.execute("ALTER TABLE users ADD COLUMN weight INTEGER;")
            print("Column 'weight' added to 'users' table.")
        
        if "gender" not in column_names:
            cursor.execute("ALTER TABLE users ADD COLUMN gender TEXT;")
            print("Column 'gender' added to 'users' table.")

        # Commit changes and close the connection
        conn.commit()
        print("Database initialized and columns added (if they didn't exist).")

    except sqlite3.Error as e:
        print(f"SQLite error: {e}")

    finally:
        conn.close()

# Call the function to initialize the database
initialize_database()
