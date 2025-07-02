from datetime import timezone, datetime
import csv
import io
import pandas as pd

def flatten_payload_to_csv_buffer(payload, device_id_prefix, root_field=None):
    """
    Take the dict-of-lists payload and a device_id_prefix,
    parse timestamps into timezone-aware datetimes,
    and return an io.StringIO CSV buffer with columns:
    device_id, timestamp, power_data, phase.

    If root_field is provided and exists in payload, flatten payload[root_field];
    otherwise flatten payload directly.
    """
    # pick the dict that holds the phase → readings map
    readings_map = payload.get(root_field) if root_field and isinstance(payload.get(root_field), dict) else payload

    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["device_id", "timestamp", "power_data", "phase"])

    for phase_str, readings in readings_map.items():
        if not isinstance(readings, list):
            continue

        # determine integer phase, or None
        try:
            phase = int(phase_str)
        except (ValueError, TypeError):
            phase = None

        for r in readings:
            raw_ts = r.get("time", "")
            try:
                # parse ISO8601 (with trailing 'Z' → UTC)
                dt = datetime.fromisoformat(raw_ts.replace("Z", "+00:00"))
            except ValueError:
                # fallback: treat as naive UTC
                dt = datetime.fromisoformat(raw_ts).replace(tzinfo=timezone.utc)

            ts_iso = dt.isoformat()

            value = r.get("value", "")

            if phase is not None:
                device_id = f"{device_id_prefix}-{phase}"
                phase_val = phase
            else:
                device_id = device_id_prefix
                phase_val = ""

            writer.writerow([device_id, ts_iso, value, phase_val])

    buf.seek(0)
    return buf

def preview_csv_buffer(buf, n=6):
    """
    Read the first n lines (including header) from the CSV buffer
    and return them as a pandas DataFrame for inspection.
    """
    lines = buf.getvalue().splitlines()[:n]
    preview_buf = io.StringIO("\n".join(lines))
    return pd.read_csv(preview_buf)