"""
Unit Tests for Harvard CS50 SQL Relational Engine
Author: Sergio Andrés Ipuz Saavedra (@Sais-gallego)
"""

import os
import sys
import unittest
import sqlite3

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.relational_engine import HarvardCS50Database


class TestHarvardCS50SQL(unittest.TestCase):

    def setUp(self):
        self.db = HarvardCS50Database()
        self.db.seed_initial_data()

    def tearDown(self):
        self.db.close()

    def test_schema_and_integrity_constraints(self):
        # 1. Check Constraint test: Invalid house must fail
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.cursor.execute("""
                INSERT INTO students (first_name, last_name, email, house, enrolled_year)
                VALUES ('Hacker', 'User', 'hacker@harvard.edu', 'InvalidHouse', 2026);
            """)

        # 2. Check Constraint test: Negative credits must fail
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.cursor.execute("""
                INSERT INTO courses (code, title, department, credits)
                VALUES ('CS999', 'Fake Course', 'Computer Science', 15);
            """)

    def test_multi_table_joins_and_aggregations(self):
        counts = self.db.get_course_enrollment_counts()
        self.assertGreater(len(counts), 0)

        # CS50x has multiple enrollments
        top_course = counts[0]
        self.assertIn("enrolled_count", top_course)
        self.assertGreaterEqual(top_course["enrolled_count"], 1)

    def test_virtual_view_honors_students(self):
        self.db.create_honors_view()
        honors = self.db.execute_query("SELECT * FROM honors_students;")
        self.assertGreater(len(honors), 0)

        # Sergio Ipuz has 4 courses with 4.0 GPA
        sergio = [h for h in honors if h["first_name"] == "Sergio"][0]
        self.assertEqual(sergio["gpa"], 4.0)
        self.assertEqual(sergio["courses_taken"], 4)

    def test_recursive_cte_prerequisites(self):
        tree = self.db.get_recursive_prerequisites()
        self.assertEqual(len(tree), 3)
        codes = [row["course_code"] for row in tree]
        self.assertIn("CS50SQL", codes)
        self.assertIn("CS50AI", codes)
        self.assertIn("CS50Cyber", codes)

    def test_b_tree_indexing_optimization(self):
        bench = self.db.benchmark_index_scan(num_records=1000)
        self.assertIn("records_tested", bench)

        # Verify EXPLAIN plan indicates index search
        explain_with = " ".join(bench["query_plan_with_index"])
        self.assertIn("SEARCH", explain_with.upper())

    def test_acid_transaction_commit_and_rollback(self):
        # Successful transfer from CS50x (id=1) to MATH21A (id=5) for Sergio (id=1)
        success = self.db.transfer_enrollment_transaction(
            student_id=1, old_course_id=1, new_course_id=5, semester="Fall 2026"
        )
        self.assertTrue(success)

        # Verify enrollment changed
        enrolled = self.db.execute_query(
            "SELECT * FROM enrollments WHERE student_id = 1 AND course_id = 5;"
        )
        self.assertEqual(len(enrolled), 1)

        # Failed transfer with non-existent old course (must rollback atomically)
        failed = self.db.transfer_enrollment_transaction(
            student_id=1, old_course_id=999, new_course_id=2, semester="Fall 2026"
        )
        self.assertFalse(failed)


if __name__ == "__main__":
    unittest.main()
