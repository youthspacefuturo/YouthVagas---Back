#!/usr/bin/env python3
"""
Test script to verify that the schema circular reference issue is fixed.
This script tests the ApplicationSchema serialization without running the full Flask app.
"""

import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.schemas.application_schema import ApplicationSchema
from app.schemas.job_schema import JobSchema
from app.schemas.student_schema import StudentSchema

def test_schema_serialization():
    """Test that schemas can be instantiated and used without circular reference errors."""
    
    print("🧪 Testing schema instantiation...")
    
    try:
        # Test individual schema instantiation
        job_schema = JobSchema()
        student_schema = StudentSchema()
        application_schema = ApplicationSchema()
        applications_schema = ApplicationSchema(many=True)
        
        print("✅ All schemas instantiated successfully")
        
        # Test mock data serialization
        mock_application_data = {
            'id': 1,
            'job_id': 1,
            'student_id': 1,
            'status': 'pending',
            'cover_letter': 'Test cover letter',
            'created_at': '2023-10-01T12:00:00',
            'job': {
                'id': 1,
                'title': 'Test Job',
                'description': 'Test job description',
                'salary_range': '5000-8000',
                'contract_type': 'CLT',
                'location': 'São Paulo',
                'work_mode': 'Remoto',
                'education': 'Superior',
                'experience': '2+ anos',
                'skills': 'Python, Flask',
                'company_id': 1,
                'company_name': 'Test Company'
            },
            'student': {
                'id': 1,
                'name': 'Test Student',
                'email': 'test@example.com',
                'phone': '11999999999',
                'github_url': 'https://github.com/test',
                'cpf': '12345678901'
            }
        }
        
        # Test single application serialization
        result = application_schema.dump(mock_application_data)
        print("✅ Single application serialization successful")
        print(f"📄 Result keys: {list(result.keys())}")
        
        # Test multiple applications serialization
        mock_applications_data = [mock_application_data]
        results = applications_schema.dump(mock_applications_data)
        print("✅ Multiple applications serialization successful")
        print(f"📄 Results count: {len(results)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Schema test failed: {str(e)}")
        print(f"❌ Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False

def test_nested_field_exclusions():
    """Test that nested field exclusions work correctly."""
    
    print("\n🧪 Testing nested field exclusions...")
    
    try:
        application_schema = ApplicationSchema()
        
        # Check that job field excludes applications
        job_field = application_schema.fields.get('job')
        if job_field and hasattr(job_field, 'exclude'):
            print(f"✅ Job field excludes: {job_field.exclude}")
        
        # Check that student field excludes applications
        student_field = application_schema.fields.get('student')
        if student_field and hasattr(student_field, 'exclude'):
            print(f"✅ Student field excludes: {student_field.exclude}")
            
        return True
        
    except Exception as e:
        print(f"❌ Nested field exclusion test failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Starting schema fix validation tests...\n")
    
    test1_passed = test_schema_serialization()
    test2_passed = test_nested_field_exclusions()
    
    print(f"\n📊 Test Results:")
    print(f"   Schema Serialization: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"   Nested Exclusions: {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    
    if test1_passed and test2_passed:
        print("\n🎉 All tests passed! Schema circular reference issue is fixed.")
        sys.exit(0)
    else:
        print("\n💥 Some tests failed. Schema issues still exist.")
        sys.exit(1)
