"""
CS50 SQL - Relational Engine, Schemas, Views, Indexes, and Transactions
Author: Sergio Andrés Ipuz Saavedra (@Sais-gallego)
Harvard University CS50's Introduction to Databases with SQL (Prof. Carter Zenke & David J. Malan)
"""

import sqlite3
import time
from typing import Dict, List, Tuple, Any, Optional


class HarvardCS50Database:
    """
    In-memory RDBMS environment implementing the core projects
    and concepts of Harvard CS50 SQL (Cyber, Packages, Dese, Census, Meteorites).
    """

    def __init__(self):
        self.conn = sqlite3.connect(":memory:")
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self._init_schemas()

    def _init_schemas(self):
        """Initialize relational schemas across 3NF tables with strict constraints."""
        # Enable Foreign Key enforcement in SQLite
        self.cursor.execute("PRAGMA foreign_keys = ON;")

        # 1. Students Table
        self.cursor.execute("""
            CREATE TABLE students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                house TEXT CHECK(house IN ('Gryffindor', 'Hufflepuff', 'Ravenclaw', 'Slytherin', 'HarvardYard')),
                enrolled_year INTEGER NOT NULL CHECK(enrolled_year >= 1636)
            );
        """)

        # 2. Courses Table
        self.cursor.execute("""
            CREATE TABLE courses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT UNIQUE NOT NULL,
                title TEXT NOT NULL,
                department TEXT NOT NULL,
                credits INTEGER NOT NULL CHECK(credits BETWEEN 1 AND 8)
            );
        """)

        # 3. Enrollments (Many-to-Many junction table)
        self.cursor.execute("""
            CREATE TABLE enrollments (
                student_id INTEGER NOT NULL,
                course_id INTEGER NOT NULL,
                grade REAL CHECK(grade BETWEEN 0.0 AND 4.0),
                semester TEXT NOT NULL,
                PRIMARY KEY (student_id, course_id, semester),
                FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
                FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
            );
        """)

        # 4. Audit Log Table for Transaction / Security Triggers
        self.cursor.execute("""
            CREATE TABLE audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action TEXT NOT NULL,
                target_table TEXT NOT NULL,
                record_id INTEGER,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            );
        """)
        self.conn.commit()

    def seed_initial_data(self):
        """Populate relational database with sample records."""
        students_data = [
            ("Sergio", "Ipuz", "sergio@harvard.edu", "HarvardYard", 2026),
            ("David", "Malan", "malan@harvard.edu", "HarvardYard", 1999),
            ("Carter", "Zenke", "carter@harvard.edu", "HarvardYard", 2020),
            ("Brian", "Yu", "brian@harvard.edu", "HarvardYard", 2019),
            ("Ada", "Lovelace", "ada@harvard.edu", "Ravenclaw", 1840)
        ]
        self.cursor.executemany("""
            INSERT INTO students (first_name, last_name, email, house, enrolled_year)
            VALUES (?, ?, ?, ?, ?);
        """, students_data)

        courses_data = [
            ("CS50x", "Introduction to Computer Science", "Computer Science", 4),
            ("CS50AI", "Introduction to Artificial Intelligence with Python", "Computer Science", 4),
            ("CS50SQL", "Introduction to Databases with SQL", "Computer Science", 4),
            ("CS50Cyber", "Introduction to Cybersecurity", "Computer Science", 4),
            ("MATH21A", "Multivariable Calculus", "Mathematics", 4)
        ]
        self.cursor.executemany("""
            INSERT INTO courses (code, title, department, credits)
            VALUES (?, ?, ?, ?);
        """, courses_data)

        enrollments_data = [
            (1, 1, 4.0, "Fall 2026"),
            (1, 2, 4.0, "Fall 2026"),
            (1, 3, 4.0, "Fall 2026"),
            (1, 4, 4.0, "Fall 2026"),
            (2, 1, 4.0, "Fall 1999"),
            (3, 3, 4.0, "Fall 2020"),
            (4, 2, 4.0, "Fall 2019")
        ]
        self.cursor.executemany("""
            INSERT INTO enrollments (student_id, course_id, grade, semester)
            VALUES (?, ?, ?, ?);
        """, enrollments_data)
        self.conn.commit()

    # --- Week 0: Querying & Aggregations ---
    def execute_query(self, sql: str, params: Tuple[Any, ...] = ()) -> List[Dict[str, Any]]:
        """Execute parameterized query and return list of dictionaries."""
        self.cursor.execute(sql, params)
        rows = self.cursor.fetchall()
        return [dict(row) for row in rows]

    def get_course_enrollment_counts(self) -> List[Dict[str, Any]]:
        """Demonstrates GROUP BY, COUNT, and ORDER BY."""
        sql = """
            SELECT c.code, c.title, COUNT(e.student_id) AS enrolled_count, AVG(e.grade) AS avg_grade
            FROM courses c
            LEFT JOIN enrollments e ON c.id = e.course_id
            GROUP BY c.id
            ORDER BY enrolled_count DESC, c.code ASC;
        """
        return self.execute_query(sql)

    # --- Week 4: Views & CTEs ---
    def create_honors_view(self):
        """Create a Virtual View for high-achieving students (GPA >= 3.8)."""
        self.cursor.execute("""
            CREATE VIEW IF NOT EXISTS honors_students AS
            SELECT s.id, s.first_name, s.last_name, s.email, AVG(e.grade) AS gpa, COUNT(e.course_id) AS courses_taken
            FROM students s
            JOIN enrollments e ON s.id = e.student_id
            GROUP BY s.id
            HAVING AVG(e.grade) >= 3.8;
        """)
        self.conn.commit()

    def get_recursive_prerequisites(self) -> List[Dict[str, Any]]:
        """Demonstrates Common Table Expressions (CTE) with WITH RECURSIVE."""
        # Create prerequisites table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS prerequisites (
                course_code TEXT,
                prereq_code TEXT
            );
        """)
        self.cursor.executemany("""
            INSERT INTO prerequisites VALUES (?, ?);
        """, [
            ("CS50SQL", "CS50x"),
            ("CS50AI", "CS50x"),
            ("CS50Cyber", "CS50x")
        ])
        self.conn.commit()

        sql = """
            WITH RECURSIVE prereq_tree AS (
                SELECT course_code, prereq_code, 1 AS depth
                FROM prerequisites
                WHERE prereq_code = 'CS50x'
                UNION ALL
                SELECT p.course_code, p.prereq_code, pt.depth + 1
                FROM prerequisites p
                JOIN prereq_tree pt ON p.prereq_code = pt.course_code
            )
            SELECT * FROM prereq_tree;
        """
        return self.execute_query(sql)

    # --- Week 5: Optimizing & B-Tree Indexes ---
    def benchmark_index_scan(self, num_records: int = 5000) -> Dict[str, Any]:
        """
        Demonstrate execution time difference between Full Table Scan (SCAN)
        and B-Tree Index Search (SEARCH) using EXPLAIN QUERY PLAN.
        """
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS benchmark_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                serial_num INTEGER NOT NULL,
                payload TEXT NOT NULL
            );
        """)
        # Insert batch
        data = [(i, f"payload_{i}") for i in range(num_records)]
        self.cursor.executemany("INSERT INTO benchmark_data (serial_num, payload) VALUES (?, ?);", data)
        self.conn.commit()

        # Query Plan without index
        explain_no_idx = self.execute_query(
            "EXPLAIN QUERY PLAN SELECT * FROM benchmark_data WHERE serial_num = ?;", (4200,)
        )
        t0 = time.perf_counter()
        for _ in range(100):
            self.execute_query("SELECT * FROM benchmark_data WHERE serial_num = ?;", (4200,))
        duration_no_idx = time.perf_counter() - t0

        # Create B-Tree Index
        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_benchmark_serial ON benchmark_data(serial_num);")
        self.conn.commit()

        # Query Plan with index
        explain_with_idx = self.execute_query(
            "EXPLAIN QUERY PLAN SELECT * FROM benchmark_data WHERE serial_num = ?;", (4200,)
        )
        t1 = time.perf_counter()
        for _ in range(100):
            self.execute_query("SELECT * FROM benchmark_data WHERE serial_num = ?;", (4200,))
        duration_with_idx = time.perf_counter() - t1

        return {
            "records_tested": num_records,
            "query_plan_without_index": [r["detail"] for r in explain_no_idx],
            "query_plan_with_index": [r["detail"] for r in explain_with_idx],
            "duration_without_index_sec": round(duration_no_idx, 6),
            "duration_with_index_sec": round(duration_with_idx, 6),
            "speedup_factor": round(duration_no_idx / duration_with_idx, 2) if duration_with_idx > 0 else 1.0
        }

    # --- Week 3 & 6: Transactions & ACID Rollback ---
    def transfer_enrollment_transaction(self, student_id: int, old_course_id: int, new_course_id: int, semester: str) -> bool:
        """
        Executes atomic transaction transfer.
        If any step fails, automatically rolls back to guarantee consistency.
        """
        try:
            self.cursor.execute("BEGIN TRANSACTION;")
            # Delete old enrollment
            self.cursor.execute("""
                DELETE FROM enrollments
                WHERE student_id = ? AND course_id = ? AND semester = ?;
            """, (student_id, old_course_id, semester))

            if self.cursor.rowcount == 0:
                raise ValueError("Old enrollment record not found")

            # Insert new enrollment
            self.cursor.execute("""
                INSERT INTO enrollments (student_id, course_id, grade, semester)
                VALUES (?, ?, NULL, ?);
            """, (student_id, new_course_id, semester))

            # Log audit
            self.cursor.execute("""
                INSERT INTO audit_logs (action, target_table, record_id)
                VALUES ('TRANSFER_ENROLLMENT', 'enrollments', ?);
            """, (student_id,))

            self.conn.commit()
            return True
        except Exception:
            self.conn.rollback()
            return False

    def close(self):
        self.conn.close()
