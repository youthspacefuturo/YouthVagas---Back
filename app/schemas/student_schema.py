from marshmallow import Schema, fields, validate, validates, ValidationError
import re

class StudentSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(allow_none=False, validate=validate.Length(min=2, max=100))
    email = fields.Email(allow_none=False)
    password = fields.Str(load_only=True, validate=validate.Length(min=6))
    phone = fields.Str(allow_none=False, validate=validate.Length(min=10, max=20))
    github_url = fields.Str(validate=validate.URL(), allow_none=True)
    resume_url = fields.Str(validate=validate.URL(), allow_none=True)
    cpf = fields.Str(allow_none=False, validate=validate.Length(min=11, max=14))
    city = fields.Str(allow_none=True)
    skills = fields.Str(allow_none=True)
    about = fields.Str(allow_none=True)
    is_active = fields.Bool(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    
    # Relationship field - applications
    applications = fields.Nested('ApplicationSchema', many=True, dump_only=True, exclude=['student'])
    
    @validates('cpf')
    def validate_cpf(self, value):
        if value is None:
            return
        cpf = re.sub(r'\D', '', value)
        if len(cpf) != 11:
            raise ValidationError('CPF deve ter 11 dígitos')
        if cpf == cpf[0] * 11:
            raise ValidationError('CPF inválido')
    
    @validates('phone')
    def validate_phone(self, value):
        if value is None:
            return
        phone = re.sub(r'\D', '', value)
        if len(phone) not in [10, 11]:
            raise ValidationError('Telefone deve ter 10 ou 11 dígitos')
    
    @validates('github_url')
    def validate_github_url(self, value):
        if value is None or value == '':
            return
        # Allow empty strings for optional fields
        if not value.strip():
            return
