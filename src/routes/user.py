from flask import Blueprint, jsonify, request
from src.models.user import User, db
from src.routes.auth import require_auth, require_permission

user_bp = Blueprint('user', __name__)

@user_bp.route('/users', methods=['GET'])
@require_auth
@require_permission('manage_users')
def get_users():
    """Listar todos os usuários (apenas administradores)"""
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])

@user_bp.route('/users', methods=['POST'])
@require_auth
@require_permission('manage_users')
def create_user():
    """Criar novo usuário (apenas administradores)"""
    data = request.json
    
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Username e password são obrigatórios'}), 400
    
    # Verificar se o username já existe
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username já existe'}), 400
    
    # Verificar se o email já existe (se fornecido)
    if data.get('email') and User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email já existe'}), 400
    
    # Validar role
    valid_roles = ['administrador', 'leitura', 'edicao', 'exclusao']
    role = data.get('role', 'leitura')
    if role not in valid_roles:
        return jsonify({'error': f'Role deve ser um dos seguintes: {", ".join(valid_roles)}'}), 400
    
    user = User(
        username=data['username'],
        email=data.get('email'),
        role=role,
        is_active=data.get('is_active', True)
    )
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify(user.to_dict()), 201

@user_bp.route('/users/<int:user_id>', methods=['GET'])
@require_auth
@require_permission('manage_users')
def get_user(user_id):
    """Obter informações de um usuário específico (apenas administradores)"""
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict())

@user_bp.route('/users/<int:user_id>', methods=['PUT'])
@require_auth
@require_permission('manage_users')
def update_user(user_id):
    """Atualizar usuário (apenas administradores)"""
    user = User.query.get_or_404(user_id)
    data = request.json
    
    # Verificar se o username já existe (se está sendo alterado)
    if data.get('username') and data['username'] != user.username:
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'error': 'Username já existe'}), 400
        user.username = data['username']
    
    # Verificar se o email já existe (se está sendo alterado)
    if data.get('email') and data['email'] != user.email:
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email já existe'}), 400
        user.email = data['email']
    
    # Atualizar role se fornecido
    if data.get('role'):
        valid_roles = ['administrador', 'leitura', 'edicao', 'exclusao']
        if data['role'] not in valid_roles:
            return jsonify({'error': f'Role deve ser um dos seguintes: {", ".join(valid_roles)}'}), 400
        user.role = data['role']
    
    # Atualizar status ativo
    if 'is_active' in data:
        user.is_active = data['is_active']
    
    # Atualizar senha se fornecida
    if data.get('password'):
        user.set_password(data['password'])
    
    db.session.commit()
    return jsonify(user.to_dict())

@user_bp.route('/users/<int:user_id>', methods=['DELETE'])
@require_auth
@require_permission('manage_users')
def delete_user(user_id):
    """Excluir usuário (apenas administradores)"""
    user = User.query.get_or_404(user_id)
    
    # Não permitir que o usuário exclua a si mesmo
    if user.id == request.current_user.id:
        return jsonify({'error': 'Não é possível excluir sua própria conta'}), 400
    
    db.session.delete(user)
    db.session.commit()
    return '', 204

@user_bp.route('/users/<int:user_id>/toggle-status', methods=['POST'])
@require_auth
@require_permission('manage_users')
def toggle_user_status(user_id):
    """Ativar/desativar usuário (apenas administradores)"""
    user = User.query.get_or_404(user_id)
    
    # Não permitir que o usuário desative a si mesmo
    if user.id == request.current_user.id:
        return jsonify({'error': 'Não é possível desativar sua própria conta'}), 400
    
    user.is_active = not user.is_active
    db.session.commit()
    
    status = 'ativado' if user.is_active else 'desativado'
    return jsonify({
        'message': f'Usuário {status} com sucesso',
        'user': user.to_dict()
    })

@user_bp.route('/change-password', methods=['POST'])
@require_auth
def change_password():
    """Alterar senha do usuário atual"""
    data = request.json
    
    if not data or not data.get('current_password') or not data.get('new_password'):
        return jsonify({'error': 'Senha atual e nova senha são obrigatórias'}), 400
    
    user = request.current_user
    
    if not user.check_password(data['current_password']):
        return jsonify({'error': 'Senha atual incorreta'}), 400
    
    user.set_password(data['new_password'])
    db.session.commit()
    
    return jsonify({'message': 'Senha alterada com sucesso'}), 200

