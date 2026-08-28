import sqlite3
import csv

DB_NAME = "teiko.db"
CSV_FILE = "cell-count.csv"

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def create_tables(conn):
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS project (
            project_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS subject (
            subject_id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            subject_name TEXT NOT NULL,
            condition TEXT,
            age INTEGER,
            sex TEXT,
            treatment TEXT,
            response TEXT,
            FOREIGN KEY (project_id) REFERENCES project(project_id)
        );

        CREATE TABLE IF NOT EXISTS sample (
            sample_id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_id INTEGER NOT NULL,
            sample_name TEXT NOT NULL,
            sample_type TEXT,
            time_from_treatment_start INTEGER,
            FOREIGN KEY (subject_id) REFERENCES subject(subject_id)
        );

        CREATE TABLE IF NOT EXISTS cell_count (
            cell_count_id INTEGER PRIMARY KEY AUTOINCREMENT,
            sample_id INTEGER NOT NULL,
            population TEXT NOT NULL,
            count INTEGER NOT NULL,
            FOREIGN KEY (sample_id) REFERENCES sample(sample_id)
        );
    """)
    conn.commit()

def clear_tables(conn):
    conn.executescript("""
        DELETE FROM cell_count;
        DELETE FROM sample;
        DELETE FROM subject;
        DELETE FROM project;
    """)
    conn.commit()

def load_csv(conn):
    with open(CSV_FILE, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            conn.execute("""
                INSERT OR IGNORE INTO project (name)
                VALUES (?)
            """, (row["project"],))

            project_id = conn.execute(
                "SELECT project_id FROM project WHERE name = ?", (row["project"],)
            ).fetchone()[0]

            conn.execute("""
                INSERT OR IGNORE INTO subject (project_id, subject_name, condition, age, sex, treatment, response)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (project_id, row["subject"], row["condition"], row["age"], row["sex"], row["treatment"], row["response"]))

            subject_id = conn.execute(
                "SELECT subject_id FROM subject WHERE subject_name = ?", (row["subject"],)
            ).fetchone()[0]

            cursor = conn.execute("""
                INSERT INTO sample (subject_id, sample_name, sample_type, time_from_treatment_start)
                VALUES (?, ?, ?, ?)
            """, (subject_id, row["sample"], row["sample_type"], row["time_from_treatment_start"]))

            sample_id = cursor.lastrowid

            populations = ["b_cell", "cd8_t_cell", "cd4_t_cell", "nk_cell", "monocyte"]
            for pop in populations:
                conn.execute("""
                    INSERT INTO cell_count (sample_id, population, count)
                    VALUES (?, ?, ?)
                """, (sample_id, pop, int(row[pop])))

        conn.commit()

def main():
    conn = get_connection()
    create_tables(conn)
    clear_tables(conn)
    load_csv(conn)
    conn.close()

if __name__ == "__main__":
    main()