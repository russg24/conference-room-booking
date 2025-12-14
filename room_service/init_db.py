import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def init_db():
    try:
        print("Connecting to database...")
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST'),
            database='postgres',
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASS')
        )
        cur = conn.cursor()

        # 1. Reset Table (Drop old versions to ensure clean slate)
        print("Resetting 'rooms' table...")
        cur.execute("DROP TABLE IF EXISTS rooms CASCADE;")

        # 2. Create Table
        cur.execute("""
        CREATE TABLE rooms (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            capacity INTEGER NOT NULL,
            location VARCHAR(100) NOT NULL,
            price_per_hour DECIMAL(10, 2) NOT NULL
        );
        """)

        # 3. Add Data (Your Design Blueprint)
        print("Adding rooms...")
        rooms_data = [
            # Berlin (Tier 3 - Baseline)
            ('Mitte Room', 50, 'Berlin', 100.00),
            ('Alexanderplatz Hall', 75, 'Berlin', 150.00),

            # London (Tier 2 - Premium)
            ('Westminster Suite', 50, 'London', 150.00),
            ('Piccadilly Hall', 75, 'London', 225.00),
            
            # Paris (Tier 1 - Luxury)
            ('Louvre Room', 50, 'Paris', 200.00),
            ('Versailles Hall', 75, 'Paris', 300.00)
        ]

        for room in rooms_data:
            cur.execute(
                "INSERT INTO rooms (name, capacity, location, price_per_hour) VALUES (%s, %s, %s, %s)",
                room
            )

        conn.commit()
        cur.close()
        conn.close()
        print("✅ Room Inventory Created Successfully!")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    init_db()