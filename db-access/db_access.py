import psycopg2
import json

def export_data():
    # Path to your config.json file
    config_file_path = "config.json"

    try:
        # Load the configuration file
        with open(config_file_path, "r") as file:
            config = json.load(file)

        # Extract database settings
        DB_SETTINGS = config["db"]

        # Establish connection to the database
        conn = psycopg2.connect(
            host=DB_SETTINGS['host'],
            port=DB_SETTINGS['port'],
            dbname=DB_SETTINGS['database'],
            user=DB_SETTINGS['user'],
            password=DB_SETTINGS['password']
        )

        cur = conn.cursor()

        with open('out_metadata.csv', 'w') as f:
            cur.copy_expert('COPY device_metadata TO STDOUT WITH CSV HEADER', f)
            print("Table exported to CSV!")
        
    except psycopg2.Error as e:
        print("Error:", e)
    finally:
        if 'cur' in locals() and cur:
            cur.close()
        if 'conn' in locals() and conn:
            conn.close()
            

if __name__ == "__main__":
    export_data()
