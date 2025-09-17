# tests/test_auth.py
import unittest
import json
from app import create_app, db
from app.models.student import Student
from app.models.company import Company

class TestAuth(unittest.TestCase):
    """Testes de autenticação para Student e Company"""
    
    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
    
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_student_registration(self):
        data = {
            "name": "Test Student",
            "email": "student@test.com",
            "password": "password123",
            "confirm_password": "password123",
            "course": "Computer Science"
        }
        response = self.client.post('/student/register',
                                  data=json.dumps(data),
                                  content_type='application/json')
        self.assertEqual(response.status_code, 201)
    
    def test_student_login(self):
        # Primeiro cria um estudante
        student = Student(name="Test Student", email="student@test.com", password="password123", course="Computer Science")
        db.session.add(student)
        db.session.commit()
        
        # Testa login do estudante
        data = {
            "email": "student@test.com",
            "password": "password123"
        }
        response = self.client.post('/student/login',
                                  data=json.dumps(data),
                                  content_type='application/json')
        self.assertEqual(response.status_code, 200)
    
    def test_company_registration(self):
        data = {
            "name": "Test Company",
            "email": "company@test.com",
            "password": "password123",
            "confirm_password": "password123",
            "address": "Test Address"
        }
        response = self.client.post('/company/register',
                                  data=json.dumps(data),
                                  content_type='application/json')
        self.assertEqual(response.status_code, 201)
    
    def test_company_login(self):
        # Primeiro cria uma empresa
        company = Company(name="Test Company", email="company@test.com", password="password123", address="Test Address")
        db.session.add(company)
        db.session.commit()
        
        # Testa login da empresa
        data = {
            "email": "company@test.com",
            "password": "password123"
        }
        response = self.client.post('/company/login',
                                  data=json.dumps(data),
                                  content_type='application/json')
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()