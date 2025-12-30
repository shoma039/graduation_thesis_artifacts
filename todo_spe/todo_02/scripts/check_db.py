import sqlite3
import os
from glob import glob

print('cwd:', os.getcwd())

db_files = glob('*.db')
if not db_files:
    print('No .db files in cwd')
else:
    print('Found db files:', db_files)

for p in db_files:
    try:
        conn = sqlite3.connect(p)
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cur.fetchall()]
        print('\nDB:', p)
        print('  tables:', tables)
        if 'tasks' in tables:
            cur.execute('SELECT COUNT(*) FROM tasks')
            print('  tasks count:', cur.fetchone()[0])
        else:
            print('  tasks table not present')
        conn.close()
    except Exception as e:
        print('  error reading', p, e)
