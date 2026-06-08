#!/usr/bin/env python3
import os, sqlite3

# 测试各种 URI 格式
DB_PATH = '/Users/yuzelong/CodeBuddy/20260605140513/app/instance/gravelcho.db'
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

# 测试1: 直接用 sqlite3 写
conn = sqlite3.connect(DB_PATH)
conn.execute('CREATE TABLE IF NOT EXISTS test (id INTEGER)')
conn.close()
print('sqlite3 直接写入: OK', DB_PATH)

# 测试2: SQLAlchemy 各种 URI 格式
from sqlalchemy import create_engine

uris = [
    f'sqlite:///{DB_PATH}',           # 3 slashes (relative)
    f'sqlite:////{DB_PATH}',         # 4 slashes (absolute)
    f'sqlite:///{DB_PATH}',           # 另一种写法
    'sqlite:///' + DB_PATH,           # 无多余斜杠
]

for uri in uris:
    try:
        eng = create_engine(uri)
        with eng.connect() as c:
            c.execute('SELECT 1')
        print(f'OK: {uri[:60]}...')
    except Exception as e:
        print(f'FAIL: {uri[:60]}... err={e}')
