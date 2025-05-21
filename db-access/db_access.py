from flask import Flask, request, jsonify
import psycopg2
import os

from heron_utils.heron_api import HeronApi
from heron_utils.query_heron import _get_device_measurement, heron_device_history
from csv_loader import load_csv_stream

app = Flask(__name__)

# —— Global singleton ——
# This runs once when each Gunicorn worker imports this module
heron_api = HeronApi()

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

@app.route('/query_heron', methods=['POST'])
def query_heron():
    payload    = request.get_json() or {}
    device_id  = payload.get('device_id')
    start_date = payload.get('start_date')
    end_date   = payload.get('end_date')

    if not all([device_id, start_date, end_date]):
        return jsonify({
            'success': False,
            'error': 'device_id, start_date and end_date are required'
        }), 400

    try:
        data = _get_device_measurement(
           heron_api_instance=heron_api,
           device_id=device_id,
           time_from_nano=start_date,
           time_to_nano=end_date
        )
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/upload_csv', methods=['POST'])
def upload_csv():
    """
    Expects multipart/form-data with a file field named 'file'.
    Wraps the binary stream in TextIOWrapper so copy_from() sees text.
    """
    f = request.files.get('file')
    if not f:
        return jsonify(success=False, error="No file part"), 400

    # Wrap the underlying binary stream as a text stream
    text_stream = io.TextIOWrapper(f.stream, encoding='utf-8')
    
    # Skip header line
    header = text_stream.readline()
    if not header:
        return jsonify(success=False, error="Empty file"), 400

    try:
        # Bulk-load into your table
        load_csv_stream(
            stream=text_stream,
            table_name="device_measurements_30",
            db_params=DB_PARAMS
        )
        return jsonify(success=True), 200

    except Exception as e:
        app.logger.exception("upload_csv failed")
        return jsonify(success=False, error=str(e)), 500