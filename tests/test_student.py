# tests/test_student.py
import unittest
from app import create_app, db
from app.models.student import Student

class TestStudent(unittest.TestCase):
    """EI VONLINDE AQUI É PRA IMPLEMENTAR OS TESTES DE STUDENT"""
    
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
    
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_student_creation(self):
        # Testar criação de student
        student = Student(name="Test Student", email="student@test.com", course="Computer Science")
        db.session.add(student)
        db.session.commit()
        self.assertIsNotNone(student.id)
        self.assertEqual(student.name, "Test Student")

if __name__ == '__main__':
    unittest.main()