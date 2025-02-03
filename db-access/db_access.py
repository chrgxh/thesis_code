from flask import Flask, request, jsonify
import psycopg2
import os

app = Flask(__name__)

# Database connection details from environment variables
DB_HOST = os.getenv('DB_HOST', 'localhost')  # Default to localhost
DB_PORT = os.getenv('DB_PORT', '5432')      # Default to PostgreSQL default port
DB_NAME = os.getenv('DB_NAME', 'test_db')   # Default to 'test_db'
DB_USER = os.getenv('DB_USER', 'user')      # Default to 'user'
DB_PASSWORD = os.getenv('DB_PASSWORD', 'password')  # Default to 'password'

@app.route('/')
def index():
    return "Welcome to the Flask API! Use the `/query` endpoint to send database queries."

@app.route('/query', methods=['POST'])
def run_query():
    query = request.json.get('query')  # Get the query from the request
    conn=None
    cursor=None
    try:
        # Connect to the database
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = conn.cursor()

        # Execute the query
        cursor.execute(query)
        columns = [desc[0] for desc in cursor.description]  # Get column names
        rows = cursor.fetchall()  # Get all results

        # Format the results as a list of dictionaries
        result = [dict(zip(columns, row)) for row in rows]

        conn.close()
        return jsonify({'success': True, 'data': result})  # Return JSON response
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    finally:
        if cursor:
            cursor.close()
        if conn is not None:
            conn.close()

if __name__ == '__main__':
    # Read application host and port from environment variables
    app_host = os.getenv('APP_HOST', '0.0.0.0')  # Default to 0.0.0.0
    app_port = int(os.getenv('APP_PORT', 5000))  # Default to 5000

    app.run(host=app_host, port=app_port)
