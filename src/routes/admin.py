from flask import Blueprint, jsonify, request
from src.models.user import User, db
from src.routes.auth import require_auth, require_permission

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard', methods=['GET'])
@require_auth
@require_permission('manage_users')
def get_dashboard_stats():
    """Obter estatísticas do dashboard (apenas administradores)"""
    try:
        total_users = User.query.count()
        active_users = User.query.filter_by(is_active=True).count()
        inactive_users = total_users - active_users
        
        # Contagem por role
        roles_count = {}
        roles = ['administrador', 'exclusao', 'edicao', 'leitura']
        for role in roles:
            roles_count[role] = User.query.filter_by(role=role, is_active=True).count()
        
        return jsonify({
            'total_users': total_users,
            'active_users': active_users,
            'inactive_users': inactive_users,
            'roles_count': roles_count
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/users/bulk-action', methods=['POST'])
@require_auth
@require_permission('manage_users')
def bulk_user_action():
    """Ações em lote para usuários (apenas administradores)"""
    data = request.json
    
    if not data or not data.get('action') or not data.get('user_ids'):
        return jsonify({'error': 'Ação e IDs dos usuários são obrigatórios'}), 400
    
    action = data['action']
    user_ids = data['user_ids']
    
    try:
        users = User.query.filter(User.id.in_(user_ids)).all()
        
        if not users:
            return jsonify({'error': 'Nenhum usuário encontrado'}), 404
        
        # Verificar se o usuário atual não está na lista (para evitar auto-modificação)
        current_user_in_list = any(user.id == request.current_user.id for user in users)
        if current_user_in_list:
            return jsonify({'error': 'Não é possível aplicar ações em lote na sua própria conta'}), 400
        
        updated_count = 0
        
        if action == 'activate':
            for user in users:
                user.is_active = True
                updated_count += 1
                
        elif action == 'deactivate':
            for user in users:
                user.is_active = False
                updated_count += 1
                
        elif action == 'delete':
            for user in users:
                db.session.delete(user)
                updated_count += 1
                
        elif action == 'change_role':
            new_role = data.get('new_role')
            valid_roles = ['administrador', 'leitura', 'edicao', 'exclusao']
            
            if not new_role or new_role not in valid_roles:
                return jsonify({'error': f'Role deve ser um dos seguintes: {", ".join(valid_roles)}'}), 400
            
            for user in users:
                user.role = new_role
                updated_count += 1
        else:
            return jsonify({'error': 'Ação inválida'}), 400
        
        db.session.commit()
        
        return jsonify({
            'message': f'Ação "{action}" aplicada com sucesso',
            'updated_count': updated_count
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/system-info', methods=['GET'])
@require_auth
@require_permission('manage_users')
def get_system_info():
    """Obter informações do sistema (apenas administradores)"""
    try:
        import os
        import sys
        from datetime import datetime
        
        # Informações básicas do sistema
        system_info = {
            'python_version': sys.version,
            'flask_version': '3.1.1',  # Versão do Flask
            'database_path': os.path.join(os.path.dirname(__file__), '..', 'database', 'app.db'),
            'current_time': datetime.utcnow().isoformat(),
            'total_users': User.query.count(),
            'active_sessions': 0  # Placeholder - seria necessário implementar contagem de sessões ativas
        }
        
        return jsonify(system_info), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

