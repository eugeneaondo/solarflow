import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Database:
    """PostgreSQL database connection manager"""
    
    def __init__(self):
        self.config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': os.getenv('DB_PORT', 5432),
            'database': os.getenv('DB_NAME', 'solarflow'),
            'user': os.getenv('DB_USER', 'solarflow_user'),
            'password': os.getenv('DB_PASSWORD', 'solarflow_pass')
        }
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = None
        try:
            conn = psycopg2.connect(**self.config)
            yield conn
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if conn:
                conn.close()
    
    def test_connection(self):
        """Test database connection"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT version();")
                    version = cursor.fetchone()[0]
                    print(f"✓ Connected to PostgreSQL")
                    print(f"  Version: {version[:50]}...")
                    return True
        except Exception as e:
            print(f"✗ Database connection failed: {e}")
            return False
    
    def insert_solar_data(self, data):
        """Insert solar panel data"""
        query = """
        INSERT INTO solar_data 
        (panel_id, timestamp, power_w, voltage_v, current_a, 
         temperature_c, efficiency, weather_factor)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id;
        """
        
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (
                        data['panel_id'],
                        data['timestamp'],
                        data['power_w'],
                        data['voltage_v'],
                        data['current_a'],
                        data['temperature_c'],
                        data.get('efficiency', 0.18),
                        data.get('weather_factor', 1.0)
                    ))
                    record_id = cursor.fetchone()[0]
                    return record_id
        except Exception as e:
            print(f"Error inserting data: {e}")
            return None
    
    def get_latest_data(self, panel_id=None):
        """Get latest data for panel(s)"""
        if panel_id:
            query = """
            SELECT * FROM solar_data 
            WHERE panel_id = %s 
            ORDER BY timestamp DESC 
            LIMIT 10;
            """
            params = (panel_id,)
        else:
            query = """
            SELECT * FROM latest_panel_data;
            """
            params = None
        
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    if params:
                        cursor.execute(query, params)
                    else:
                        cursor.execute(query)
                    return cursor.fetchall()
        except Exception as e:
            print(f"Error fetching data: {e}")
            return []
    
    def get_statistics(self):
        """Get current statistics"""
        query = """
        SELECT 
            COUNT(DISTINCT panel_id) as total_panels,
            SUM(power_w) as total_power_w,
            AVG(power_w) as avg_power_w,
            AVG(temperature_c) as avg_temperature_c,
            AVG(efficiency) as avg_efficiency,
            MAX(timestamp) as last_update
        FROM latest_panel_data;
        """
        
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute(query)
                    return cursor.fetchone()
        except Exception as e:
            print(f"Error fetching statistics: {e}")
            return None

# Test if run directly
if __name__ == "__main__":
    db = Database()
    if db.test_connection():
        print("\n✓ Database module working correctly!")
        
        # Test getting panels
        stats = db.get_statistics()
        if stats:
            print(f"\nCurrent Statistics:")
            print(f"  Total Panels: {stats['total_panels']}")
            print(f"  Total Power: {stats['total_power_w']} W")
    else:
        print("\n✗ Database connection failed!")
