# tests/test_jobs.py
import unittest
from app import create_app, db
from app.models.job import Job
from app.models.company import Company

class TestJobs(unittest.TestCase):
    """EI VONLINDE AQUI É PRA IMPLEMENTAR OS TESTES DE JOBS"""
    
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        
        # Criar uma company para o teste de job
        self.company = Company(name="Test Company", email="company@test.com")
        db.session.add(self.company)
        db.session.commit()
    
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_job_creation(self):
        # Testar criação de job
        job = Job(title="Developer", description="Backend Developer", company_id=self.company.id)
        db.session.add(job)
        db.session.commit()
        self.assertIsNotNone(job.id)
        self.assertEqual(job.title, "Developer")

if __name__ == '__main__':
    unittest.main()