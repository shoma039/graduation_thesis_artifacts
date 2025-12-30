from src.storage import db


def create_task(title, priority, location_id, deadline_utc, candidate_date_local, status='open'):
    conn = db.get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO task (title, priority, location_id, deadline_utc, candidate_date_local, status, created_at, updated_at) VALUES (?,?,?,?,?,?,datetime('now'),datetime('now'))",
        (title, priority, location_id, deadline_utc, candidate_date_local, status),
    )
    conn.commit()
    tid = cur.lastrowid
    conn.close()
    return tid


def get_task(task_id):
    conn = db.get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM task WHERE id = ?", (task_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def update_task(task_id, **fields):
    if not fields:
        return
    keys = ", ".join([f"{k} = ?" for k in fields.keys()])
    vals = list(fields.values())
    vals.append(task_id)
    conn = db.get_conn()
    cur = conn.cursor()
    cur.execute(f"UPDATE task SET {keys}, updated_at = datetime('now') WHERE id = ?", vals)
    conn.commit()
    conn.close()


def delete_task(task_id):
    conn = db.get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM task WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
