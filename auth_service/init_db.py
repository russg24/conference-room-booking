import os
import psycopg2
import bcrypt
from dotenv import load_dotenv

# Load variables from the .env file
load_dotenv()

def init_db():
    try:
        # Connect to the remote AWS database
        print("Connecting to database...")

        # We use os.getenv to read the secrets safely from your .env file
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST'),
            database='postgres',
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASS')
        )
        cur = conn.cursor()

        # 1. Create the Users Table
        print("Creating 'users' table...")
        cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL
        );
        """)

        # 2. Check/Add Admin User
        cur.execute("SELECT * FROM users WHERE username = %s", ('admin',))
        if cur.fetchone() is None:
            print("Creating admin user...")
            # Hash the password 'admin' for security
            hashed_pw = bcrypt.hashpw('admin'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", ('admin', hashed_pw))
        else:
            print("Admin user already exists.")

        # Save changes and close
        conn.commit()
        cur.close()
        conn.close()
        print("✅ Database setup complete!")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    init_db()