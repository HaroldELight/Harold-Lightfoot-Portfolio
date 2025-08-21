import sqlite3
from config import settings

class Memory:
    def __init__(self):
        self.conn = sqlite3.connect(settings["MEMORY_DB_PATH"])
        self._create_table()

    def _create_table(self):
        c = self.conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS chat_memory (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_input TEXT,
                        ai_response TEXT
                    )''')
        self.conn.commit()

    def save(self, user_input, ai_response):
        c = self.conn.cursor()
        c.execute("INSERT INTO chat_memory (user_input, ai_response) VALUES (?, ?)", (user_input, ai_response))
        self.conn.commit()

    def get_all(self):
        c = self.conn.cursor()
        c.execute("SELECT user_input, ai_response FROM chat_memory")
        return c.fetchall()
