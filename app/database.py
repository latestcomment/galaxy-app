import sqlite3
from typing import Dict, List, Tuple, Any, Optional
from datetime import datetime

class Database:
    def __init__(self, db_name: str):
        self.db_name = db_name
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()

    def disconnect(self) -> None:
        if self.conn:
            self.conn.close()
            print("Database connection closed.")

    def create_table(self, table_name: str, columns: Dict[str, str]) -> None:
        columns_def = ', '.join([f"{col} {dtype}" for col, dtype in columns.items()])
        query = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            {columns_def}
        )
        """
        try:
            self.cursor.execute(query)
            self.conn.commit()
            print(f"Table '{table_name}' created or already exists.")
        except sqlite3.Error as e:
            print(f"Error creating table '{table_name}': {e}")
            raise

    def insert(self, table_name: str, data: Dict[str, Any]) -> int:
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        try:
            self.cursor.execute(query, tuple(data.values()))
            self.conn.commit()
            print(f"Row inserted into '{table_name}' with ID {self.cursor.lastrowid}.")
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Error inserting into table '{table_name}': {e}")
            raise

    def upsert(self, table_name: str, data: Dict[str, Any], primary_key: str) -> None:
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        update_placeholders = ', '.join([f"{col} = ?" for col in data if col != primary_key])
        
        query = f"""
        INSERT INTO {table_name} ({columns})
        VALUES ({placeholders})
        ON CONFLICT({primary_key}) DO UPDATE SET {update_placeholders}
        """
        try:
            values = tuple(data.values())
            self.cursor.execute(query, values + tuple(v for k, v in data.items() if k != primary_key))
            self.conn.commit()
            print(f"Row with {primary_key} '{data[primary_key]}' upserted successfully.")
        except sqlite3.Error as e:
            print(f"Error upserting into table '{table_name}': {e}")
            raise