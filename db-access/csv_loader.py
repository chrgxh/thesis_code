import io
import psycopg2

def load_csv_stream(stream, table_name, db_params):
    """
    Given a file-like stream (at its start—header still present),
    bulk-insert into Postgres using copy_from.

    - Wraps binary streams in TextIOWrapper.
    - Skips the header row automatically.
    - Loads into the specified columns only.
    """
    # 1) Ensure we have a text stream
    if isinstance(stream, (io.BufferedReader, io.BytesIO)):
        text_stream = io.TextIOWrapper(stream, encoding='utf-8')
    else:
        text_stream = stream

    # 2) Skip header row
    header = text_stream.readline()
    if not header:
        raise ValueError("CSV stream is empty or missing header")

    # 3) Connect and COPY
    conn = psycopg2.connect(**db_params)
    try:
        with conn, conn.cursor() as cur:
            cur.copy_from(
                file=text_stream,
                table=table_name,
                sep=",",
                columns=("device_id", "timestamp", "power_data", "phase")
            )
    finally:
        conn.close()
