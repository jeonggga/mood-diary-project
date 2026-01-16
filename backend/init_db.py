import pymysql
import os

# Configuration matches config.py and user inputs
DB_HOST = '127.0.0.1'
DB_USER = 'root'
DB_PASSWORD = '1q2w3e4r'
DB_NAME = 'mood_diary'

def init_db():
    print(f"Connecting to MariaDB at {DB_HOST} as {DB_USER}...")
    try:
        # Connect to MySQL Server (no db selected yet)
        conn = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        try:
            with conn.cursor() as cursor:
                # 1. Create Database if not exists
                print(f"Creating database '{DB_NAME}' if not exists...")
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
                
                # 2. Select Database
                print(f"Using database '{DB_NAME}'...")
                cursor.execute(f"USE {DB_NAME};")
                
                # 3. Read schema.sql
                schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
                print(f"Reading schema from {schema_path}...")
                with open(schema_path, 'r', encoding='utf-8') as f:
                    schema_sql = f.read()
                
                # 4. Execute statements
                statements = schema_sql.split(';')
                for stmt in statements:
                    stmt = stmt.strip()
                    if stmt:
                        print(f"Executing SQL: {stmt[:50].replace(chr(10), ' ')}...")
                        cursor.execute(stmt)
                
                conn.commit()
                print("Schema applied successfully!")

                # 5. Verify
                cursor.execute("SHOW TABLES;")
                tables = cursor.fetchall()
                print(f"Current tables in {DB_NAME}:")
                for table in tables:
                    print(f" - {table}")
                
        finally:
            conn.close()
            print("Connection closed.")

    except ImportError:
        print("Error: pymysql module not found. Please run 'pip install pymysql' first.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    init_db()
