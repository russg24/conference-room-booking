import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def reset_and_seed_users():
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            database=os.getenv('DB_NAME', 'postgres'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASS', 'postgres')
        )
        cur = conn.cursor()
        print("🔌 Connected to Database...")

        # 1. RESET: Drop the old table (CASCADE removes links to bookings)
        print("🗑️  Wiping old data (Alice & Bob)...")
        cur.execute("DROP TABLE IF EXISTS users CASCADE;")
        
        # 2. REBUILD: Create the table fresh
        print("🔨 Recreating Users table...")
        cur.execute("""
        CREATE TABLE users (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            password_hash VARCHAR(200) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # 3. SEED: Insert John and Jane
        new_users = [
            ("John Doe", "john@nexus.com", "password123"),
            ("Jane Smith", "jane@nexus.com", "password123")
        ]

        for name, email, pwd in new_users:
            cur.execute("""
                INSERT INTO users (name, email, password_hash) 
                VALUES (%s, %s, %s);
            """, (name, email, pwd))
        
        print(f"✅ Seeding Complete: Welcome {new_users[0][0]} and {new_users[1][0]}!")

        # Verify
        cur.execute("SELECT id, name, email FROM users;")
        rows = cur.fetchall()
        print("👥 Current Users in DB:", rows)

        conn.commit()
        cur.close()
        conn.close()

    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    reset_and_seed_users()