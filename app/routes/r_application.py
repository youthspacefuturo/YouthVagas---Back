from flask import Blueprint, request, jsonify
from app.services.application_services import ApplicationService
from app.schemas.application_schema import ApplicationSchema, ApplyToJobSchema, ApplicationStatusUpdateSchema
from app.middleware.auth_middleware import student_required, company_required

application_bp = Blueprint('application', __name__)
application_schema = ApplicationSchema()
applications_schema = ApplicationSchema(many=True)
apply_schema = ApplyToJobSchema()
status_update_schema = ApplicationStatusUpdateSchema()

@application_bp.route('/jobs/<int:job_id>/apply', methods=['POST'])
@student_required
def apply_to_job(job_id, **kwargs):
    """Estudante se candidatar a uma vaga"""
    try:
        from flask import current_app
        current_user = kwargs.get('current_user')
        data = request.get_json() or {}
        
        # Debug logging
        if current_app.debug:
            print(f"🔍 DEBUG: apply_to_job route hit with job_id={job_id}")
            print(f"🔍 DEBUG: Request data: {data}")
            print(f"🔍 DEBUG: Current user: {current_user}")
        
        if not current_user or not current_user.get('id'):
            return jsonify({'error': 'Usuário não autenticado'}), 401
        
        # Validar dados com schema
        errors = apply_schema.validate(data)
        if errors:
            return jsonify({'errors': errors}), 400
        
        cover_letter = data.get('cover_letter')
        
        application = ApplicationService.apply_to_job(
            job_id=job_id,
            student_id=current_user['id'],
            cover_letter=cover_letter
        )
        
        return jsonify({
            'message': 'Candidatura enviada com sucesso',
            'application': application_schema.dump(application)
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        from flask import current_app
        current_app.logger.error(f"Erro ao aplicar para vaga: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@application_bp.route('/jobs/<int:job_id>/applications', methods=['GET'])
@company_required
def get_job_applications(job_id, **kwargs):
    """Empresa ver candidaturas de uma vaga específica"""
    try:
        from flask import current_app
        current_user = kwargs.get('current_user')
        
        # Debug logging
        if current_app.debug:
            print(f"🔍 DEBUG: get_job_applications route hit with job_id={job_id}")
            print(f"🔍 DEBUG: Current user: {current_user}")
        
        if not current_user or not current_user.get('id'):
            return jsonify({'error': 'Usuário não autenticado'}), 401
        
        applications = ApplicationService.get_applications_for_job(
            job_id=job_id,
            company_id=current_user['id']
        )
        
        # Debug logging for applications data
        if current_app.debug:
            print(f"🔍 DEBUG: Found {len(applications)} applications for job {job_id}")
            for app in applications:
                print(f"🔍 DEBUG: Application {app.id} - Job: {app.job_id}, Student: {app.student_id}")
        
        # Use to_dict() method to ensure all student data is included
        try:
            applications_data = [app.to_dict() for app in applications]
            if current_app.debug:
                print(f"🔍 DEBUG: to_dict() serialization successful, returning {len(applications_data)} items")
                # Debug first application to check student data
                if applications_data:
                    first_app = applications_data[0]
                    print(f"🔍 DEBUG: First application student data: {first_app.get('student')}")
            return jsonify(applications_data), 200
        except Exception as serialization_error:
            if current_app.debug:
                print(f"🔍 DEBUG: to_dict() serialization error: {str(serialization_error)}")
                print(f"🔍 DEBUG: Serialization error type: {type(serialization_error).__name__}")
            raise serialization_error
        
    except ValueError as e:
        from flask import current_app
        if current_app.debug:
            print(f"🔍 DEBUG: ValueError in get_job_applications: {str(e)}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        from flask import current_app
        current_app.logger.error(f"Erro ao buscar candidaturas: {str(e)}")
        if current_app.debug:
            print(f"🔍 DEBUG: Exception in get_job_applications: {str(e)}")
            import traceback
            traceback.print_exc()
        return jsonify({'error': 'Erro interno do servidor'}), 500

@application_bp.route('/applications/<int:application_id>/status', methods=['PUT'])
@company_required
def update_application_status(application_id, **kwargs):
    """Empresa atualizar status de candidatura"""
    try:
        current_user = kwargs.get('current_user')
        data = request.get_json() or {}
        
        if not current_user or not current_user.get('id'):
            return jsonify({'error': 'Usuário não autenticado'}), 401
        
        # Validar dados com schema
        errors = status_update_schema.validate(data)
        if errors:
            return jsonify({'errors': errors}), 400
        
        status = data.get('status')
            
        application = ApplicationService.update_application_status(
            application_id=application_id,
            status=status,
            company_id=current_user['id']
        )
        
        return jsonify({
            'message': 'Status atualizado com sucesso',
            'application': application_schema.dump(application)
        }), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        from flask import current_app
        current_app.logger.error(f"Erro ao atualizar status: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@application_bp.route('/applications/<int:application_id>', methods=['DELETE'])
@company_required
def delete_application(application_id, **kwargs):
    """Empresa deletar uma candidatura"""
    try:
        from flask import current_app
        current_user = kwargs.get('current_user')
        
        if current_app.debug:
            print(f"🔍 DEBUG: delete_application route hit with application_id={application_id}")
            print(f"🔍 DEBUG: Current user: {current_user}")
        
        if not current_user or not current_user.get('id'):
            return jsonify({'error': 'Usuário não autenticado'}), 401
        
        ApplicationService.delete_application(
            application_id=application_id,
            company_id=current_user['id']
        )
        
        return jsonify({
            'message': 'Candidatura removida com sucesso'
        }), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        from flask import current_app
        current_app.logger.error(f"Erro ao deletar candidatura: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500