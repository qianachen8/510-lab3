import sqlite3
import streamlit as st
from pydantic import BaseModel
import streamlit_pydantic as sp
from typing import Literal, List
import datetime

# Connect to SQLite database
con = sqlite3.connect("ToDoList.sqlite", isolation_level=None)
cur = con.cursor()

# Create the table
cur.execute(
    """
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY,
        task TEXT,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        created_by TEXT DEFAULT "Jackie",
        category TEXT,
        is_done BOOLEAN DEFAULT FALSE
    )
    """
)

# Define our Form
class Task(BaseModel):
    name: str
    description: str
    created_at: datetime.datetime
    created_by: str = "Qiana Chen" 
    category: Literal['School', 'Medical', 'Shopping','Family', 'Trip']
    is_done: bool

# This function will be called when the check mark is toggled, this is called a callback function
def toggle_is_done(is_done, row):
    cur.execute(
        """
        UPDATE tasks SET is_done = ? WHERE id = ?
        """,
        (is_done, row),
    )

# This function will be called when the delete button is clicked
def delete_task(row):
    cur.execute(
        """
        DELETE FROM tasks WHERE id = ?
        """,
        (row,),
    )

def main():
    st.title("ToDoList")

    # Create a Form using the streamlit-pydantic package, just pass it the Task Class
    data = sp.pydantic_form(key="task_form", model=Task)

    if data:
        # Convert created_at to the appropriate string format for SQLite TIMESTAMP
        created_at_str = data.created_at.strftime("%Y-%m-%d %H:%M:%S")
        cur.execute(
            """
            INSERT INTO tasks (task, description, created_at, created_by, category, is_done)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (data.name, data.description, created_at_str, data.created_by, data.category, data.is_done),
        )

    tasks = cur.execute(
        """
        SELECT * FROM tasks
        """
    ).fetchall()

    if tasks:
        for row in tasks:
            cols = st.columns([1, 3, 3, 2, 2, 2, 1, 1])
            is_done = row[6]

            # Checkbox for marking task as done
            if cols[0].checkbox("", is_done, key=row[0]):
                toggle_is_done(not is_done, row[0])

            # Task details
            cols[1].write(row[1])
            cols[2].write(row[2])
            cols[3].write(row[3])
            cols[4].write(row[4])
            cols[5].write(row[5])

            # Delete button
            if cols[5].button("Delete", key=f"delete-{row[0]}"):
                delete_task(row[0])
                st.experimental_rerun()

main()
