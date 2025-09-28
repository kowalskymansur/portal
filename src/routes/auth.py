from flask import Blueprint, jsonify, request
from src.models.user import User, Session, db
from datetime import datetime, timedelta
from functools import wraps

auth_bp = Blueprint('auth', __name__)

def require_auth(f):
    """Decorator para verificar autenticação"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Token de autenticação necessário'}), 401
        
        if token.startswith('Bearer '):
            token = token[7:]
        
        session = Session.query.filter_by(token=token, is_active=True).first()
        if not session or session.is_expired():
            return jsonify({'error': 'Token inválido ou expirado'}), 401
        
        request.current_user = session.user
        request.current_session = session
        return f(*args, **kwargs)
    
    return decorated_function

def require_permission(permission):
    """Decorator para verificar permissões específicas"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not hasattr(request, 'current_user'):
                return jsonify({'error': 'Usuário não autenticado'}), 401
            
            if not request.current_user.has_permission(permission):
                return jsonify({'error': 'Permissão insuficiente'}), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@auth_bp.route('/login', methods=['POST'])
def login():
    """Endpoint para login de usuário"""
    data = request.json
    
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Username e password são obrigatórios'}), 400
    
    user = User.query.filter_by(username=data['username']).first()
    
    if not user or not user.check_password(data['password']):
        return jsonify({'error': 'Credenciais inválidas'}), 401
    
    if not user.is_active:
        return jsonify({'error': 'Usuário inativo'}), 401
    
    # Criar nova sessão
    session = Session(
        user_id=user.id,
        token=Session.generate_token(),
        expires_at=datetime.utcnow() + timedelta(hours=8)  # Sessão expira em 8 horas
    )
    
    db.session.add(session)
    user.update_last_login()
    db.session.commit()
    
    return jsonify({
        'token': session.token,
        'user': user.to_dict(),
        'expires_at': session.expires_at.isoformat()
    }), 200

@auth_bp.route('/logout', methods=['POST'])
@require_auth
def logout():
    """Endpoint para logout de usuário"""
    request.current_session.is_active = False
    db.session.commit()
    
    return jsonify({'message': 'Logout realizado com sucesso'}), 200

@auth_bp.route('/me', methods=['GET'])
@require_auth
def get_current_user():
    """Endpoint para obter informações do usuário atual"""
    return jsonify(request.current_user.to_dict()), 200

@auth_bp.route('/verify-token', methods=['POST'])
def verify_token():
    """Endpoint para verificar se um token é válido"""
    data = request.json
    token = data.get('token')
    
    if not token:
        return jsonify({'valid': False, 'error': 'Token não fornecido'}), 400
    
    session = Session.query.filter_by(token=token, is_active=True).first()
    
    if not session or session.is_expired():
        return jsonify({'valid': False, 'error': 'Token inválido ou expirado'}), 401
    
    return jsonify({
        'valid': True,
        'user': session.user.to_dict(),
        'expires_at': session.expires_at.isoformat()
    }), 200

@auth_bp.route('/refresh-token', methods=['POST'])
@require_auth
def refresh_token():
    """Endpoint para renovar token de sessão"""
    # Desativar sessão atual
    request.current_session.is_active = False
    
    # Criar nova sessão
    new_session = Session(
        user_id=request.current_user.id,
        token=Session.generate_token(),
        expires_at=datetime.utcnow() + timedelta(hours=8)
    )
    
    db.session.add(new_session)
    db.session.commit()
    
    return jsonify({
        'token': new_session.token,
        'expires_at': new_session.expires_at.isoformat()
    }), 200

