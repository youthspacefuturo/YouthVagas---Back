from flask import Blueprint, request, jsonify
from app.services.job_services import JobService
from app.schemas.job_schema import JobSchema
from app.middleware.auth_middleware import company_required, refresh_token_if_needed

job_bp = Blueprint('job', __name__)
job_schema = JobSchema()
jobs_schema = JobSchema(many=True)

@job_bp.route('/jobs', methods=['POST'])
@company_required
def create_job(**kwargs):
    """Empresa criar nova vaga"""
    try:
        from flask import current_app
        current_user = kwargs.get('current_user')
        data = request.get_json()
        
        # Debug logging
        if current_app.debug:
            print(f"🔍 DEBUG: create_job route hit")
            print(f"🔍 DEBUG: Request data: {data}")
            print(f"🔍 DEBUG: Current user: {current_user}")
        
        if not data:
            return jsonify({'error': 'Dados não fornecidos'}), 400
        
        if not current_user or not current_user.get('id'):
            return jsonify({'error': 'Usuário não autenticado'}), 401
        
        # Log para debug
        from flask import current_app
        if current_app.debug:
            print(f"DEBUG: Creating job for company {current_user['id']}")
            print(f"DEBUG: Received data: {data}")
        
        # Adicionar company_id automaticamente
        data['company_id'] = current_user['id']
        
        # Validar campos obrigatórios antes da validação do schema
        required_fields = ['title', 'description', 'location', 'contract_type', 'work_mode', 'education', 'experience', 'skills']
        missing_fields = []
        
        for field in required_fields:
            if not data.get(field) or (isinstance(data.get(field), str) and not data.get(field).strip()):
                missing_fields.append(field)
        
        if missing_fields:
            return jsonify({
                'error': 'Campos obrigatórios não preenchidos',
                'errors': {field: ['Este campo é obrigatório'] for field in missing_fields}
            }), 422
        
        # Validar e normalizar dados
        loaded = job_schema.load(data)
        job = JobService.create_job(loaded, extra_payload=data)
        
        return jsonify({
            'message': 'Vaga criada com sucesso',
            'job': job.to_dict()
        }), 201
        
    except Exception as e:
        # Melhor tratamento de erros de validação
        from marshmallow import ValidationError
        from flask import current_app
        
        if current_app.debug:
            print(f"DEBUG: Error creating job: {str(e)}")
            print(f"DEBUG: Error type: {type(e).__name__}")
        
        if isinstance(e, ValidationError):
            return jsonify({
                'error': 'Dados inválidos',
                'errors': e.messages
            }), 422
        
        current_app.logger.error(f"Erro ao criar vaga: {str(e)}")
        return jsonify({'error': str(e)}), 400

@job_bp.route('/jobs', methods=['GET'])
def get_jobs():
    """Listar todas as vagas ativas (público)"""
    try:
        # Permitir filtro opcional por empresa
        company_id = request.args.get('company_id', type=int)
        
        if company_id is not None:
            jobs = JobService.get_jobs_by_company(company_id)
        else:
            jobs = JobService.get_all_jobs()
            
        # Usar to_dict() para incluir dados da empresa
        jobs_data = [job.to_dict() for job in jobs]
        return jsonify(jobs_data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@job_bp.route('/jobs/<int:id>', methods=['GET'])
def get_job(id):
    """Buscar vaga específica por ID (público)"""
    try:
        job = JobService.get_job_by_id(id)
        if job and job.is_active:
            return jsonify(job.to_dict()), 200
        return jsonify({'error': 'Vaga não encontrada'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@job_bp.route('/companies/jobs/<int:id>', methods=['PUT'])
@company_required
def update_job(id, **kwargs):
    """Empresa atualizar sua própria vaga"""
    try:
        current_user = kwargs.get('current_user')
        
        # Verificar se a vaga pertence à empresa logada
        job = JobService.get_job_by_id(id)
        if not job:
            return jsonify({'error': 'Vaga não encontrada'}), 404
            
        if job.company_id != current_user['id']:
            return jsonify({'error': 'Você só pode atualizar suas próprias vagas'}), 403
        
        data = request.get_json()
        data['company_id'] = current_user['id']  # Garantir que não mude a empresa
        
        # Usar partial=True para permitir updates parciais
        loaded = job_schema.load(data, partial=True)
        job = JobService.update_job(id, loaded, extra_payload=data)
        
        return jsonify({
            'message': 'Vaga atualizada com sucesso',
            'job': job.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@job_bp.route('/companies/jobs/<int:id>', methods=['DELETE'])
@company_required
def delete_job(id, **kwargs):
    """Empresa deletar sua própria vaga"""
    try:
        from app.services.application_services import ApplicationService
        current_user = kwargs.get('current_user')
        
        # Verificar se a vaga pertence à empresa logada
        job = JobService.get_job_by_id(id)
        if not job:
            return jsonify({'error': 'Vaga não encontrada'}), 404
            
        if job.company_id != current_user['id']:
            return jsonify({'error': 'Você só pode deletar suas próprias vagas'}), 403
        
        # Verificar se há candidaturas para esta vaga
        applications_count = ApplicationService.get_job_applications_count(id)
        if applications_count > 0:
            return jsonify({
                'error': f'Não é possível deletar a vaga. Existem {applications_count} candidatura(s) ativa(s). Remova todas as candidaturas antes de deletar a vaga.'
            }), 400
        
        JobService.delete_job(id)
        
        return jsonify({'message': 'Vaga deletada com sucesso'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@job_bp.route('/companies/jobs/<int:id>/deactivate', methods=['PUT'])
@company_required
def deactivate_job(id, **kwargs):
    """Empresa desativar sua própria vaga"""
    try:
        current_user = kwargs.get('current_user')
        
        # Verificar se a vaga pertence à empresa logada
        job = JobService.get_job_by_id(id)
        if not job:
            return jsonify({'error': 'Vaga não encontrada'}), 404
            
        if job.company_id != current_user['id']:
            return jsonify({'error': 'Você só pode desativar suas próprias vagas'}), 403
        
        job = JobService.deactivate_job(id)
        return jsonify({
            'message': 'Vaga desativada com sucesso',
            'job': job_schema.dump(job)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@job_bp.route('/companies/jobs', methods=['GET'])
@company_required
def get_company_jobs(**kwargs):
    """Empresa listar suas próprias vagas"""
    try:
        current_user = kwargs.get('current_user')
        jobs = JobService.get_jobs_by_company(current_user['id'])
        return jsonify(jobs_schema.dump(jobs)), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

