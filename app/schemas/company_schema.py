from marshmallow import Schema, fields, validate, validates, ValidationError
import re

class CompanySchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(allow_none=False, validate=validate.Length(min=2, max=100))
    email = fields.Email(allow_none=False)
    password = fields.Str(load_only=True, validate=validate.Length(min=6))
    phone = fields.Str(allow_none=False, validate=validate.Length(min=10, max=20))
    cnpj = fields.Str(allow_none=False, validate=validate.Length(min=14, max=18))
    website = fields.Str(validate=validate.URL(), allow_none=True)
    sector = fields.Str(allow_none=True)
    company_size = fields.Str(allow_none=True)
    about = fields.Str(allow_none=True)
    fantasy_name = fields.Str(allow_none=True)
    city = fields.Str(allow_none=True)
    is_active = fields.Bool(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    
    @validates('cnpj')
    def validate_cnpj(self, value):
        if value is None:
            return
        cnpj = re.sub(r'\D', '', value)
        if len(cnpj) != 14:
            raise ValidationError('CNPJ deve ter 14 dígitos')
        if cnpj == cnpj[0] * 14:
            raise ValidationError('CNPJ inválido')
    
    @validates('phone')
    def validate_phone(self, value):
        if value is None:
            return
        phone = re.sub(r'\D', '', value)
        if len(phone) not in [10, 11]:
            raise ValidationError('Telefone deve ter 10 ou 11 dígitos')
    
    @validates('website')
    def validate_website(self, value):
        if value is None or value == '':
            return
        # Allow empty strings for optional fields
        if not value.strip():
            return
