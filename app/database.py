from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import uuid4
import sqlite3

import config


@dataclass
class BaseModel:
    id: str
    # created: datetime = datetime.now()


@dataclass
class LoginRecord(BaseModel):
    nonce: str
    redirect_url: Optional[str] = None
    session: Optional[str] = None


@dataclass
class SessionRecord(BaseModel):
    access_token: str
    refresh_token: str
    user_id: str
    expire: datetime
    name: str
    picture: Optional[str] = None


class MyPbDb:
    db: sqlite3.Connection

    def __init__(self):
        self.db = db = sqlite3.connect('../docker/app/db/db.sqlite')
        cursor = db.cursor()
        cursor.execute("""
CREATE TABLE IF NOT EXISTS sessions (
    id TEXT PRIMARY KEY NOT NULL,
    access_token TEXT NOT NULL,
    refresh_token TEXT NOT NULL,
    user_id TEXT NOT NULL,
    name TEXT,
    picture TEXT,
    expire DATE NOT NULL
);
""")
        cursor.execute("""
CREATE TABLE IF NOT EXISTS login (
    id TEXT PRIMARY KEY NOT NULL,
    nonce TEXT NOT NULL,
    redirect_url TEXT,
    session_id INTEGER,
    FOREIGN KEY (session_id) REFERENCES sessions (id)
);
""")
        db.commit()

    def get_nonce(self, nonce: str) -> LoginRecord:
        query = """
SELECT id, nonce, redirect_url, session_id FROM login
    WHERE nonce = ?"""
        cursor = self.db.cursor()
        cursor.execute(query, (nonce,))
        records = cursor.fetchone()
        if len(records) == 0:
            raise Exception('not found')

        return LoginRecord(*records)

    def get_nonce_by_id_or_none(self, _id: str) -> LoginRecord | None:
        conditions = {
            "id": _id,
        }
        query = """
SELECT id, nonce, redirect_url, session_id FROM login
    WHERE """ + " AND ".join([f"{key} = ?" for key in conditions.keys()])
        cursor = self.db.cursor()
        cursor.execute(query, tuple(conditions.values()))
        records = cursor.fetchall()
        if len(records) == 0:
            return None
        return LoginRecord(*records[0])

    def clear_existing_nonce(self, nonce: str):
        cursor = self.db.cursor()
        cursor.execute("DELETE FROM login WHERE nonce = ?;", (nonce,))
        self.db.commit()
        return None

    def create_new_login_nonce(self, nonce: str, redirect_url: str) -> LoginRecord:
        _id = uuid4().hex
        cursor = self.db.cursor()
        cursor.execute("INSERT INTO login (id, nonce, redirect_url) VALUES (:id, :nonce, :redirect_url)", {
            "id": _id,
            "nonce": nonce,
            "redirect_url": redirect_url
        })
        self.db.commit()
        return LoginRecord(_id, nonce, redirect_url)

    def update_login_nonce(self, record: LoginRecord) -> LoginRecord:
        query = """
UPDATE login SET
    nonce = :nonce,
    session_id = :session_id
WHERE
    id = :id
"""
        cursor = self.db.cursor()
        cursor.execute(query, {
            "nonce": record.nonce,
            "session_id": record.session,
            "id": record.id
        })
        self.db.commit()
        return record

    def create_session(self, access_token: str, refresh_token: str, user_id: str, expire: datetime, name: str,
                       picture: Optional[str] = None) -> SessionRecord:
        _id = uuid4().hex
        query = """
INSERT INTO sessions (id, access_token, refresh_token, user_id, expire, name, picture) 
    VALUES (:id, :access_token, :refresh_token, :user_id, :expire, :name, :picture)
"""
        cursor = self.db.cursor()
        cursor.execute(query,
                       {
                           "id": _id,
                           "access_token": access_token,
                           "refresh_token": refresh_token,
                           "user_id": user_id,
                           "expire": expire.strftime("%Y-%m-%d %H:%M:%S.%f"),
                           "name": name,
                           "picture": picture,
                       })
        return SessionRecord(_id, access_token, refresh_token, user_id, expire, name, picture)

    def get_session_or_none(self, _id: str) -> SessionRecord | None:
        conditions = {
            "id": _id,
        }
        query = """
SELECT 
    id, 
    access_token,
    refresh_token,
    user_id,
    expire,
    name,
    picture
FROM sessions
WHERE """ + " AND ".join([f"{key} = ?" for key in conditions.keys()])
        cursor = self.db.cursor()
        cursor.execute(query, tuple(conditions.values()))
        records = cursor.fetchall()
        if len(records) == 0:
            return None
        return SessionRecord(*records[0])

    def update_session(self, record: SessionRecord) -> SessionRecord:
        query = """
UPDATE sessions SET
    :access_token, :refresh_token, :user_id, :expire, :name, :picture
WHERE
    id = :id
"""
        cursor = self.db.cursor()
        cursor.execute(query, {
            "access_token": record.access_token,
            "refresh_token": record.refresh_token,
            "user_id": record.user_id,
            "expire": record.expire,
            "name": record.name,
            "picture": record.picture,
            "id": record.id
        })
        self.db.commit()
