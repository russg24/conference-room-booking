import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def init_db():
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST'),
            database='postgres',
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASS')
        )
        cur = conn.cursor()

        # Create the Bookings Table
        # The 'UNIQUE' constraint prevents double-booking the same room on the same date
        cur.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            room_id INTEGER NOT NULL,
            room_name VARCHAR(100),
            date VARCHAR(20) NOT NULL,
            total_price DECIMAL(10, 2) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(room_id, date)
        );
        """)
        
        conn.commit()
        cur.close()
        conn.close()
        print("✅ Booking Table Ready!")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    init_db()