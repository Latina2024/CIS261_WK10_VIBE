import sys
import termios
import tty
from pathlib import Path


class Student:
    """Represents a student with name, ID, scores, average, and final grade."""

    def __init__(self, name, student_id, test_1, test_2, test_3):
        self.name = str(name).strip()
        self.id = str(student_id).strip()
        self.student_id = self.id
        self.test_1 = self._validate_score(test_1)
        self.test_2 = self._validate_score(test_2)
        self.test_3 = self._validate_score(test_3)
        self.test_scores = {
            "Test 1": self.test_1,
            "Test 2": self.test_2,
            "Test 3": self.test_3,
        }
        self.average = self.calculate_average()
        self.grade = self.calculate_letter_grade()

    @staticmethod
    def _validate_score(score):
        score = float(score)
        if not 0 <= score <= 100:
            raise ValueError("Test score must be between 0 and 100.")
        return round(score, 2)

    def calculate_average(self):
        average = (self.test_1 + self.test_2 + self.test_3) / 3
        self.average = round(average, 2)
        return self.average

    def calculate_letter_grade(self):
        average = self.calculate_average()
        if average >= 90:
            self.grade = "A"
        elif average >= 80:
            self.grade = "B"
        elif average >= 70:
            self.grade = "C"
        elif average >= 60:
            self.grade = "D"
        else:
            self.grade = "F"
        return self.grade

    def to_record(self):
        self.calculate_average()
        self.calculate_letter_grade()
        return (
            f"{self.name}|{self.id}|{self.test_1:.2f}|{self.test_2:.2f}|"
            f"{self.test_3:.2f}|{self.average:.2f}|{self.grade}"
        )

    @classmethod
    def from_record(cls, record_line):
        parts = record_line.split("|")
        if len(parts) != 7:
            raise ValueError(f"Invalid record format: {record_line}")

        name, student_id, test_1, test_2, test_3, average, grade = parts
        student = cls(name, student_id, test_1, test_2, test_3)
        student.average = float(average)
        student.grade = grade
        return student

    def display_student_record(self):
        print(f"Student Name: {self.name}")
        print(f"Student ID: {self.id}")
        print(f"Test 1: {self.test_1:.2f}")
        print(f"Test 2: {self.test_2:.2f}")
        print(f"Test 3: {self.test_3:.2f}")
        print(f"Average Score: {self.average:.2f}")
        print(f"Letter Grade: {self.grade}")


class StudentManager:
    """Stores student records and calculates class-level statistics."""

    def __init__(self):
        self.students = []

    def add_student(self, student):
        for existing in self.students:
            if existing.student_id.lower() == student.student_id.lower():
                raise ValueError(f"Student ID {student.student_id} already exists.")
        self.students.append(student)

    def search_by_name(self, name):
        search_value = name.lower()
        return [student for student in self.students if search_value in student.name.lower()]

    def highest_average(self):
        if not self.students:
            return None
        return max(self.students, key=lambda student: student.calculate_average())

    def lowest_average(self):
        if not self.students:
            return None
        return min(self.students, key=lambda student: student.calculate_average())

    def class_average(self):
        if not self.students:
            return 0.0
        return round(sum(student.calculate_average() for student in self.students) / len(self.students), 2)

    def display_all_students(self):
        if not self.students:
            print("No students found.")
            return

        headers = ["Name", "ID", "Test 1", "Test 2", "Test 3", "Average", "Grade"]
        rows = [
            [
                student.name,
                student.student_id,
                format(student.test_1, ".2f"),
                format(student.test_2, ".2f"),
                format(student.test_3, ".2f"),
                format(student.calculate_average(), ".2f"),
                student.calculate_letter_grade(),
            ]
            for student in self.students
        ]

        column_widths = [len(header) for header in headers]
        for row in rows:
            for index, value in enumerate(row):
                column_widths[index] = max(column_widths[index], len(value))

        def format_row(values):
            return " | ".join(value.ljust(column_widths[index]) for index, value in enumerate(values))

        print("\nStudent Records")
        print(format_row(headers))
        print("-" + "-+-".join("-" * width for width in column_widths) + "-")
        for row in rows:
            print(format_row(row))

    def display_class_statistics(self):
        if not self.students:
            print("No class statistics available. Add students first.")
            return

        highest = self.highest_average()
        lowest = self.lowest_average()
        average = self.class_average()

        print("\nClass Statistics")
        print(f"Highest Average: {highest.name} - {highest.calculate_average():.2f}")
        print(f"Lowest Average:  {lowest.name} - {lowest.calculate_average():.2f}")
        print(f"Class Average:   {average:.2f}")

    def save_to_file(self, filename="student_grades.txt", directory=None):
        if directory is None:
            directory = Path(__file__).resolve().parent
        path = Path(directory) / filename

        try:
            with path.open("w", encoding="utf-8") as file:
                for student in self.students:
                    file.write(student.to_record() + "\n")
            print(f"Student records were saved to {path.name}.")
            return path
        except OSError as exc:
            print(f"Error saving file: {exc}")
            return None

    def load_from_file(self, filename="student_grades.txt", directory=None):
        if directory is None:
            directory = Path(__file__).resolve().parent
        path = Path(directory) / filename

        if not path.exists():
            try:
                path.write_text("", encoding="utf-8")
                print(f"No saved file found. Created a new file: {path.name}")
            except OSError as exc:
                print(f"Error creating file: {exc}")
            return []

        try:
            self.students = []
            with path.open("r", encoding="utf-8") as file:
                for line in file:
                    if line.strip():
                        self.students.append(Student.from_record(line.strip()))
            print(f"Loaded {len(self.students)} student record(s) from {path.name}.")
            return self.students
        except (OSError, ValueError) as exc:
            print(f"Error loading file: {exc}")
            self.students = []
            return []


def read_key():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        key = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return key


def prompt_for_student():
    while True:
        try:
            name = input("Enter student name: ").strip()
            if not name:
                raise ValueError("Student name cannot be empty.")

            student_id = input("Enter student ID: ").strip()
            if not student_id:
                raise ValueError("Student ID cannot be empty.")

            test_1 = float(input("Enter Test 1 score: "))
            test_2 = float(input("Enter Test 2 score: "))
            test_3 = float(input("Enter Test 3 score: "))

            return Student(name, student_id, test_1, test_2, test_3)
        except ValueError as exc:
            print(f"Error: {exc}. Please try again.")
        except KeyboardInterrupt:
            print("\nReturning to menu.")
            return None


def add_student(manager):
    student = prompt_for_student()
    if student is None:
        return

    try:
        manager.add_student(student)
        print(f"Student {student.name} added successfully.")
    except ValueError as exc:
        print(f"Error: {exc}")


def search_student(manager):
    name = input("Enter student name to search: ").strip()
    matches = manager.search_by_name(name)
    if not matches:
        print(f"No student named '{name}' was found.")
        return

    print(f"Matches for '{name}':")
    for student in matches:
        student.display_student_record()
        print("-" * 30)


def display_student_table(manager):
    manager.display_all_students()


def save_students(manager):
    manager.save_to_file()


def load_students(manager):
    manager.load_from_file()


def main():
    manager = StudentManager()
    load_students(manager)

    while True:
        print("\nStudent Grade Manager")
        print("1. Add student")
        print("2. Display all students")
        print("3. Search by name")
        print("4. View class statistics")
        print("5. Save records")
        print("6. Load records")
        print("ESC. Exit")

        key = read_key()
        print()

        if key == "\x1b":
            print("Exiting program. Goodbye!")
            break

        if key == "1":
            add_student(manager)
        elif key == "2":
            display_student_table(manager)
        elif key == "3":
            search_student(manager)
        elif key == "4":
            manager.display_class_statistics()
        elif key == "5":
            save_students(manager)
        elif key == "6":
            load_students(manager)
        else:
            print("Invalid choice. Please press 1-6 or ESC to exit.")


if __name__ == "__main__":
    main()