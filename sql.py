import os
import sys
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv
from tabulate import tabulate

# Ensure the output directory exists
OUTPUT_DIR = "outputs"
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def get_db_connection():
    """Establishes and returns a database connection."""
    load_dotenv()
    
    # Fetch credentials
    user = os.getenv('USER')
    password = os.getenv('PASSWORD')
    dbname = os.getenv('DBNAME')
    
    try:
        conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password
        )
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

def run_query_file(filename, conn):
    """
    Reads SQL from a file, executes it, writes output to .txt,
    and returns the row count.
    """
    try:
        if not os.path.exists(filename):
            print(f"Error: File '{filename}' not found.")
            return -1

        # Read the SQL file
        with open(filename, 'r') as f:
            sql_query = f.read()

        # Execute
        cur = conn.cursor()
        cur.execute(sql_query)
        rows = cur.fetchall()
        
        # Determine Output Filename (e.g., "1.sql" -> ".outputs/1.txt")
        base_name = os.path.basename(filename)
        out_name = os.path.splitext(base_name)[0] + "_sql.txt"
        out_path = os.path.join(OUTPUT_DIR, out_name)

        # Write results to file using tabulate
        headers = [desc[0] for desc in cur.description] if cur.description else []
        table_output = tabulate(rows, headers=headers, tablefmt='psql')

        # 4. Write results to file
        with open(out_path, 'w') as f:
            f.write(table_output)

        cur.close()
        return len(rows)

    except Exception as e:
        print(f"Error processing {filename}: {e}")
        return -1

def main():

    if len(sys.argv) < 2:
        print("Usage: python sql_runner.py <filename.sql>")
        sys.exit(1)

    sql_file = sys.argv[1]

    conn = get_db_connection()
    if not conn:
        return

    # Run specific file
    print(f"Running {sql_file}...")
    row_count = run_query_file(sql_file, conn)
    
    if row_count >= 0:
        print(f" -> Success. Rows: {row_count}")
        print(f" -> Output saved to {OUTPUT_DIR}/{os.path.splitext(os.path.basename(sql_file))[0]}.txt")
    else:
        print(" -> Failed.")

    conn.close()

if __name__ == "__main__":
    main()