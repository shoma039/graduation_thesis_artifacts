import sqlite3
from typing import Optional, List, Dict, Any
from pathlib import Path
from datetime import datetime
from ..db import schema

def get_conn():
    return schema.get_connection()

def insert_location(display_name: str, lat: float, lon: float, timezone: str) -> int:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('SELECT id FROM locations WHERE display_name = ?', (display_name,))
    row = cur.fetchone()
    if row:
        conn.close()
        return row['id']
    cur.execute('INSERT INTO locations (display_name, lat, lon, timezone) VALUES (?, ?, ?, ?)', (display_name, lat, lon, timezone))
    conn.commit()
    lid = cur.lastrowid
    conn.close()
    return lid

def insert_task(title: str, priority: str, place_id: Optional[int], deadline: str) -> int:
    conn = get_conn()
    cur = conn.cursor()
    now = datetime.utcnow().isoformat()
    cur.execute('INSERT INTO tasks (title, completed, priority, place_id, deadline, created_at, updated_at) VALUES (?, 0, ?, ?, ?, ?, ?)',
                (title, priority, place_id, deadline, now, now))
    conn.commit()
    tid = cur.lastrowid
    conn.close()
    return tid

def list_tasks() -> List[Dict[str, Any]]:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('SELECT t.*, l.display_name, l.timezone FROM tasks t LEFT JOIN locations l ON t.place_id = l.id WHERE t.completed = 0 ORDER BY t.deadline ASC')
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

def get_task(task_id: int) -> Optional[Dict[str, Any]]:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('SELECT t.*, l.display_name, l.lat, l.lon, l.timezone FROM tasks t LEFT JOIN locations l ON t.place_id = l.id WHERE t.id = ?', (task_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None

def mark_task_complete(task_id: int):
    conn = get_conn()
    cur = conn.cursor()
    # remove candidate dates for this task first
    cur.execute('DELETE FROM candidate_dates WHERE task_id = ?', (task_id,))
    # then remove the task
    cur.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    conn.commit()
    conn.close()


def insert_candidate_date(task_id: int, date: str, is_confirmed: int = 0, expected_precipitation: Optional[float] = None, expected_temperature: Optional[float] = None) -> int:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('INSERT INTO candidate_dates (task_id, date, is_confirmed, expected_precipitation, expected_temperature) VALUES (?, ?, ?, ?, ?)',
                (task_id, date, is_confirmed, expected_precipitation, expected_temperature))
    conn.commit()
    cid = cur.lastrowid
    conn.close()
    return cid


def get_candidate_dates_on_date(date: str) -> List[Dict[str, Any]]:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('SELECT cd.*, t.created_at FROM candidate_dates cd JOIN tasks t ON cd.task_id = t.id WHERE cd.date = ?', (date,))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def list_candidate_dates_for_task(task_id: int) -> List[Dict[str, Any]]:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('SELECT * FROM candidate_dates WHERE task_id = ? ORDER BY date ASC', (task_id,))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def delete_candidate_dates_for_task(task_id: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('DELETE FROM candidate_dates WHERE task_id = ?', (task_id,))
    conn.commit()
    conn.close()


def update_task(task_id: int, title: Optional[str], priority: Optional[str], place_id: Optional[int], deadline: Optional[str]):
    conn = get_conn()
    cur = conn.cursor()
    now = datetime.utcnow().isoformat()
    cur.execute('SELECT * FROM tasks WHERE id = ?', (task_id,))
    if not cur.fetchone():
        conn.close()
        raise ValueError('task not found')
    # build update
    cur.execute('UPDATE tasks SET title = COALESCE(?, title), priority = COALESCE(?, priority), place_id = COALESCE(?, place_id), deadline = COALESCE(?, deadline), updated_at = ? WHERE id = ?', (title, priority, place_id, deadline, now, task_id))
    conn.commit()
    conn.close()


def set_candidate_confirmed(candidate_id: int, confirmed: int = 1):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('UPDATE candidate_dates SET is_confirmed = ? WHERE id = ?', (confirmed, candidate_id))
    conn.commit()
    conn.close()


def get_candidate_date(candidate_id: int) -> Optional[Dict[str, Any]]:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('SELECT cd.*, t.title FROM candidate_dates cd JOIN tasks t ON cd.task_id = t.id WHERE cd.id = ?', (candidate_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def list_candidate_dates_in_range(start_date: str, end_date: str) -> List[Dict[str, Any]]:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('SELECT cd.*, t.title, l.display_name FROM candidate_dates cd JOIN tasks t ON cd.task_id = t.id LEFT JOIN locations l ON t.place_id = l.id WHERE cd.date >= ? AND cd.date <= ? ORDER BY cd.date ASC', (start_date, end_date))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows
