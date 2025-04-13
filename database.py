import sqlite3
from sqlite3 import Error

DATABASE_NAME = "library_manager.db"

class LibraryManager:
    def __init__(self):
        self.conn = self.create_connection()
        self.create_tables()

    def create_connection(self):
        try:
            return sqlite3.connect(DATABASE_NAME, check_same_thread=False)
        except Error as e:
            print(e)
            return None

    def create_tables(self):
        statements = [
            """
            CREATE TABLE IF NOT EXISTS classes (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL UNIQUE
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS subjects (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL UNIQUE
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                class_id INTEGER NOT NULL,
                FOREIGN KEY (class_id) REFERENCES classes(id)
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                class_id INTEGER NOT NULL,
                subject_id INTEGER NOT NULL,
                FOREIGN KEY (class_id) REFERENCES classes(id),
                FOREIGN KEY (subject_id) REFERENCES subjects(id)
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS assignments (
                student_id INTEGER NOT NULL,
                book_id INTEGER NOT NULL,
                PRIMARY KEY (student_id, book_id),
                FOREIGN KEY (student_id) REFERENCES students(id),
                FOREIGN KEY (book_id) REFERENCES books(id)
            );
            """
        ]
        cur = self.conn.cursor()
        for stmt in statements:
            cur.execute(stmt)
        self.conn.commit()

    # CRUD Classes
    def add_class(self, name):
        cur = self.conn.cursor()
        cur.execute("INSERT OR IGNORE INTO classes(name) VALUES(?)", (name,))
        self.conn.commit()

    def list_classes(self):
        cur = self.conn.cursor()
        cur.execute("SELECT id, name FROM classes ORDER BY name")
        return cur.fetchall()

    # CRUD Subjects
    def add_subject(self, name):
        cur = self.conn.cursor()
        cur.execute("INSERT OR IGNORE INTO subjects(name) VALUES(?)", (name,))
        self.conn.commit()

    def list_subjects(self):
        cur = self.conn.cursor()
        cur.execute("SELECT id, name FROM subjects ORDER BY name")
        return cur.fetchall()

    # CRUD Students
    def add_student(self, name, class_id):
        cur = self.conn.cursor()
        cur.execute("INSERT INTO students(name, class_id) VALUES(?, ?)", (name, class_id))
        self.conn.commit()

    def list_students(self, class_id=None):
        cur = self.conn.cursor()
        if class_id:
            cur.execute("SELECT id, name FROM students WHERE class_id=? ORDER BY name", (class_id,))
        else:
            cur.execute("SELECT id, name FROM students ORDER BY name")
        return cur.fetchall()

    # CRUD Books
    def add_book(self, title, author, class_id, subject_id):
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO books(title, author, class_id, subject_id) VALUES(?, ?, ?, ?)",
            (title, author, class_id, subject_id)
        )
        self.conn.commit()

    def list_books(self, class_id=None, subject_id=None):
        cur = self.conn.cursor()
        query = "SELECT id, title || ' (' || author || ')' AS label, class_id, subject_id FROM books"
        params = []
        filters = []
        if class_id:
            filters.append("class_id=?")
            params.append(class_id)
        if subject_id:
            filters.append("subject_id=?")
            params.append(subject_id)
        if filters:
            query += " WHERE " + " AND ".join(filters)
        query += " ORDER BY title"
        cur.execute(query, tuple(params))
        return cur.fetchall()

    # Assignments
    def student_has_subject(self, student_id, subject_id):
        cur = self.conn.cursor()
        cur.execute("""
            SELECT 1 FROM assignments
            JOIN books ON assignments.book_id = books.id
            WHERE assignments.student_id=? AND books.subject_id=?
        """, (student_id, subject_id))
        return cur.fetchone() is not None

    def assign_book(self, student_id, book_id):
        cur = self.conn.cursor()
        # verifica matéria
        cur.execute("SELECT subject_id FROM books WHERE id=?", (book_id,))
        row = cur.fetchone()
        if not row:
            return False
        if self.student_has_subject(student_id, row[0]):
            return False
        cur.execute("INSERT INTO assignments(student_id, book_id) VALUES(?, ?)", (student_id, book_id))
        self.conn.commit()
        return True

    def list_assignments(self, class_id=None):
        cur = self.conn.cursor()
        query = """
            SELECT c.name AS class, s.name AS student, subj.name AS subject, b.title
            FROM assignments a
            JOIN students s ON a.student_id = s.id
            JOIN books b ON a.book_id = b.id
            JOIN subjects subj ON b.subject_id = subj.id
            JOIN classes c ON s.class_id = c.id
        """
        params = []
        if class_id:
            query += " WHERE c.id=?"
            params.append(class_id)
        query += " ORDER BY s.name, subj.name"
        cur.execute(query, tuple(params))
        return cur.fetchall()
