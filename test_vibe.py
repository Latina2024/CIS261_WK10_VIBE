from VIBE import Student, StudentManager


def test_student_average_and_letter_grade():
    student = Student("Alice", "S-101", 90, 80, 95)

    assert student.calculate_average() == 88.33
    assert student.calculate_letter_grade() == "B"


def test_student_report_includes_required_fields():
    student = Student("Bob", "S-202", 100, 85, 90)

    assert student.name == "Bob"
    assert student.student_id == "S-202"
    assert student.test_1 == 100
    assert student.test_2 == 85
    assert student.test_3 == 90
    assert student.calculate_average() == 91.67
    assert student.calculate_letter_grade() == "A"


def test_manager_statistics_and_file_round_trip(tmp_path):
    manager = StudentManager()
    manager.add_student(Student("Alice", "S-101", 90, 80, 95))
    manager.add_student(Student("Bob", "S-202", 100, 85, 90))
    manager.add_student(Student("Cara", "S-303", 60, 70, 75))

    assert manager.highest_average().name == "Bob"
    assert manager.lowest_average().name == "Cara"
    assert manager.class_average() == 82.78

    file_path = tmp_path / "student_grades.txt"
    manager.save_to_file(file_path.name, directory=tmp_path)
    new_manager = StudentManager()
    new_manager.load_from_file(file_path.name, directory=tmp_path)

    assert len(new_manager.students) == 3
    assert new_manager.search_by_name("alice")[0].student_id == "S-101"
