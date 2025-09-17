
import unittest
from app import create_app, db
from app.models.company import Company

class TestCompany(unittest.TestCase):
    """EI VONLINDE AQUI É PRA IMPLEMENTAR OS TESTES DA COMPANY"""
    
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
    
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_company_creation(self):
        # Testar criação de empresa
        company = Company(name="Test Company", email="company@test.com", address="Test Address")
        db.session.add(company)
        db.session.commit()
        self.assertIsNotNone(company.id)
        self.assertEqual(company.name, "Test Company")

if __name__ == '__main__':
    unittest.main()