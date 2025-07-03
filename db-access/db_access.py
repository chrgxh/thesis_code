from flask import Flask, request, jsonify
import psycopg2
import os
import io
from csv_loader import load_csv_stream

app = Flask(__name__)

# Database config from env
DB_HOST     = os.getenv('DB_HOST', 'localhost')
DB_PORT     = os.getenv('DB_PORT', '5432')
DB_NAME     = os.getenv('DB_NAME', 'test_db')
DB_USER     = os.getenv('DB_USER', 'user')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'password')

DB_PARAMS = {
    "host":     DB_HOST,
    "port":     int(DB_PORT),
    "database": DB_NAME,
    "user":     DB_USER,
    "password": DB_PASSWORD,
}

@app.route('/')
def index():
    return "Welcome! POST to /query or /query_heron."

@app.route('/query', methods=['POST'])
def run_query():
    query = request.json.get('query')
    try:
        conn = psycopg2.connect(host=DB_HOST, port=DB_PORT,
                                database=DB_NAME,
                                user=DB_USER, password=DB_PASSWORD)
        with conn, conn.cursor() as cur:
            cur.execute(query)
            cols = [c[0] for c in cur.description]
            rows = cur.fetchall()
        return jsonify({'success': True,
                        'data': [dict(zip(cols, r)) for r in rows]})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/upload_csv', methods=['POST'])
def upload_csv():
    f = request.files.get('file')
    if not f:
        return jsonify(success=False, error="No file part"), 400

    try:
        # Read and decode entire content
        content = f.read().decode('utf-8')

        # Pass full content (with header) as a StringIO stream
        text_stream = io.StringIO(content)

        # Let load_csv_stream handle the header and data
        load_csv_stream(
            stream=text_stream,
            table_name="device_measurements_30",
            db_params=DB_PARAMS
        )

        return jsonify(success=True), 200

    except Exception as e:
        app.logger.exception("upload_csv failed")
        return jsonify(success=False, error=str(e)), 500
