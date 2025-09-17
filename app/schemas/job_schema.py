from marshmallow import Schema, fields, validate, pre_load, post_dump, EXCLUDE

class JobSchema(Schema):
    class Meta:
        unknown = EXCLUDE
        
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    description = fields.Str(required=True, validate=validate.Length(min=10))
    salary_range = fields.Str(required=True, validate=validate.Length(min=1))
    contract_type = fields.Str(required=True, validate=validate.OneOf(['CLT', 'PJ', 'Freelance', 'Estágio', 'Trainee']))
    benefits = fields.Str(allow_none=True, missing="")
    location = fields.Str(required=True, validate=validate.Length(min=1))
    work_hours = fields.Str(allow_none=True, missing="40h semanais")
    work_mode = fields.Str(required=True, validate=validate.OneOf(['Presencial', 'Remoto', 'Híbrido']))
    requirements = fields.Str(allow_none=True, missing="")
    education = fields.Str(required=True, validate=validate.Length(min=1))
    experience = fields.Str(required=True, validate=validate.Length(min=1))
    skills = fields.Str(required=True, validate=validate.Length(min=1))
    is_active = fields.Bool(load_default=True)
    company_id = fields.Int(required=True)
    created_at = fields.DateTime(dump_only=True)
    
    # Campos derivados da empresa para exibição - todos os campos necessários
    company_name = fields.Str(dump_only=True)
    company_website = fields.Str(dump_only=True)
    company_sector = fields.Str(dump_only=True)
    company_size = fields.Str(dump_only=True)
    company_about = fields.Str(dump_only=True)
    company_fantasy_name = fields.Str(dump_only=True)
    company_city = fields.Str(dump_only=True)
    company_cnpj = fields.Str(dump_only=True)
    company_phone = fields.Str(dump_only=True)
    company_email = fields.Str(dump_only=True)
    
    # Relationship field - applications
    applications = fields.Nested('ApplicationSchema', many=True, dump_only=True, exclude=['job'])

    @pre_load
    def normalize_payload(self, in_data, **kwargs):
        data = dict(in_data or {})

        # Mapear chaves camelCase -> snake_case
        key_map = {
            'salary': 'salary_range',
            'contractType': 'contract_type',
            'workMode': 'work_mode',
            'workHours': 'work_hours',
        }
        
        for src, dst in key_map.items():
            if src in data and dst not in data:
                data[dst] = data.pop(src)

        # Extrair quickQuestions { education, experience, skills }
        qq = data.get('quickQuestions')
        if isinstance(qq, dict):
            if 'education' in qq and 'education' not in data:
                data['education'] = qq.get('education')
            if 'experience' in qq and 'experience' not in data:
                data['experience'] = qq.get('experience')
            if 'skills' in qq and 'skills' not in data:
                skills_val = qq.get('skills')
                if isinstance(skills_val, list):
                    data['skills'] = ', '.join([str(s) for s in skills_val])
                else:
                    data['skills'] = skills_val

        # skills no nível raiz pode vir como lista
        if isinstance(data.get('skills'), list):
            data['skills'] = ', '.join([str(s) for s in data['skills']])

        # Benefícios pode vir como lista
        if isinstance(data.get('benefits'), list):
            data['benefits'] = ', '.join([str(b) for b in data['benefits']])

        # Normalizar work_mode
        wm = data.get('work_mode')
        if isinstance(wm, str):
            wm_upper = wm.strip().upper()
            mapping = {
                'PRESENCIAL': 'Presencial',
                'REMOTO': 'Remoto',
                'HIBRIDO': 'Híbrido',
                'HÍBRIDO': 'Híbrido',
            }
            data['work_mode'] = mapping.get(wm_upper, wm.title())

        # Garantir que company_id seja inteiro
        if 'company_id' in data and isinstance(data['company_id'], str):
            try:
                data['company_id'] = int(data['company_id'])
            except ValueError:
                pass

        return data

    @post_dump
    def present_arrays(self, data, **kwargs):
        # Converter skills string para lista no retorno
        skills_val = data.get('skills')
        if isinstance(skills_val, str):
            parts = [p.strip() for p in skills_val.split(',') if p.strip()]
            data['skills'] = parts
        
        # Adicionar dados da empresa se o relacionamento estiver carregado
        original_obj = self.context.get('original_obj') if hasattr(self, 'context') else None
        if not original_obj and hasattr(kwargs, 'original_data'):
            original_obj = kwargs['original_data']
        
        if hasattr(original_obj, 'company') and original_obj.company:
            company = original_obj.company
            data['company_name'] = company.name or 'Empresa não informada'
            data['company_website'] = company.website
            data['company_sector'] = company.sector or 'Não informado'
            data['company_size'] = company.company_size or 'Não informado'
            data['company_about'] = company.about or 'Informações sobre a empresa não disponíveis.'
            data['company_fantasy_name'] = company.fantasy_name
            data['company_city'] = company.city
            data['company_cnpj'] = company.cnpj
            data['company_phone'] = company.phone
            data['company_email'] = company.email
        return data