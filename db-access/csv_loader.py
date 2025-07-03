import psycopg2
import io

def load_csv_stream(stream, table_name, db_params):
    """
    Bulk-load CSV data into PostgreSQL with UPSERT.
    - Creates a temporary table
    - Uses COPY for fast loading
    - Inserts into real table with ON CONFLICT DO UPDATE SET ...
    """

    # 1. Wrap binary stream if needed
    if isinstance(stream, (io.BufferedReader, io.BytesIO)):
        text_stream = io.TextIOWrapper(stream, encoding='utf-8')
    else:
        text_stream = stream

    # 2. Read and parse header
    header_line = text_stream.readline()
    if not header_line:
        raise ValueError("CSV stream is empty or missing header")

    columns = [col.strip() for col in header_line.strip().split(',')]
    column_list = ', '.join(columns)
    temp_table = f"{table_name}_temp"
    dedup_table = f"{temp_table}_dedup"

    # 3. Define conflict columns (adjust if needed)
    conflict_cols = ['timestamp', 'device_id', 'phase']
    conflict_clause = ', '.join(conflict_cols)

    # 4. Build the update clause
    update_cols = [col for col in columns if col not in conflict_cols]
    update_clause = ', '.join(f"{col}=EXCLUDED.{col}" for col in update_cols)

    # 5. Connect and execute
    conn = psycopg2.connect(**db_params)
    try:
        with conn, conn.cursor() as cur:
            # Create temp table
            cur.execute(f"DROP TABLE IF EXISTS {temp_table};")
            cur.execute(f"""
                CREATE TEMP TABLE {temp_table} AS
                SELECT {column_list}
                FROM {table_name}
                LIMIT 0;
            """)


            # Load data into temp table
            cur.copy_from(
                file=text_stream,
                table=temp_table,
                sep=",",
                columns=tuple(columns)
            )

            # Deduplicate rows from source by averaging power
            cur.execute(f"DROP TABLE IF EXISTS {dedup_table};")
            cur.execute(f"""
                CREATE TEMP TABLE {dedup_table} AS
                SELECT 
                    timestamp,
                    device_id,
                    phase,
                    AVG(power_data) AS power_data
                FROM {temp_table}
                GROUP BY timestamp, device_id, phase;
            """)

            # Upsert from temp into real table
            cur.execute(f"""
                INSERT INTO {table_name} ({column_list})
                SELECT {column_list}
                FROM {dedup_table}
                ON CONFLICT ({conflict_clause}) DO UPDATE SET
                {update_clause};
            """)
    finally:
        conn.close()
