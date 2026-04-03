import os
import logging
from functools import wraps
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from flask import jsonify, request
from app.models.user import User

logger = logging.getLogger(__name__)

def allowed_file(filename, allowed_extensions):
    """Check if file has allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def secure_filename_custom(filename):
    """Secure filename by removing special characters"""
    import re
    filename = str(filename)
    filename = re.sub(r'[^\w\s.-]', '', filename)
    filename = re.sub(r'[-\s]+', '-', filename)
    return filename[:255]

def sanitize_input(text, max_length=10000):
    """Sanitize user input to prevent injection"""
    if not isinstance(text, str):
        return text
    
    # Remove null bytes
    text = text.replace('\x00', '')
    
    # Limit length
    text = text[:max_length]
    
    # Remove script tags
    import re
    text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r'javascript:', '', text, flags=re.IGNORECASE)
    
    return text.strip()

def validate_email(email):
    """Validate email format"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def hash_password(password):
    """Hash password (bcrypt used in User model)"""
    import bcrypt
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def verify_password(stored_hash, password):
    """Verify password"""
    import bcrypt
    return bcrypt.checkpw(password.encode('utf-8'), stored_hash)

def require_role(*roles):
    """Decorator to check user role"""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                verify_jwt_in_request()
                user_id = get_jwt_identity()
                user = User.find_by_id(user_id)
                
                if not user:
                    return jsonify({'error': 'User not found'}), 401
                
                if user.role not in roles:
                    return jsonify({'error': 'Insufficient permissions'}), 403
                
                request.user = user
                return fn(*args, **kwargs)
            except Exception as e:
                logger.error(f"Authorization error: {e}")
                return jsonify({'error': 'Unauthorized'}), 401
        return wrapper
    return decorator

def login_required(fn):
    """Decorator to require login"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            user = User.find_by_id(user_id)
            
            if not user:
                return jsonify({'error': 'User not found'}), 401
            
            request.user = user
            return fn(*args, **kwargs)
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return jsonify({'error': 'Unauthorized'}), 401
    return wrapper

def handle_exceptions(fn):
    """Decorator to handle exceptions globally"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {fn.__name__}: {e}")
            return jsonify({'error': 'Internal server error', 'message': str(e)}), 500
    return wrapper

def paginate_query(query, page=1, per_page=20):
    """Paginate MongoDB query results"""
    page = max(1, int(page))
    per_page = min(100, max(1, int(per_page)))
    skip = (page - 1) * per_page
    
    total = query.clone().count_documents({}) if hasattr(query, 'count_documents') else len(list(query))
    items = list(query.skip(skip).limit(per_page))
    
    return {
        'items': items,
        'total': total,
        'page': page,
        'per_page': per_page,
        'pages': (total + per_page - 1) // per_page
    }

def validate_required_fields(data, required_fields):
    """Validate required fields in request data"""
    missing_fields = [field for field in required_fields if field not in data or not data[field]]
    if missing_fields:
        return False, f"Missing required fields: {', '.join(missing_fields)}"
    return True, None

class RateLimiter:
    """Simple rate limiter"""
    def __init__(self):
        self.requests = {}
    
    def is_allowed(self, identifier, limit=10, window=60):
        """Check if request is allowed"""
        import time
        current_time = time.time()
        
        if identifier not in self.requests:
            self.requests[identifier] = []
        
        # Remove old requests
        self.requests[identifier] = [
            req_time for req_time in self.requests[identifier]
            if current_time - req_time < window
        ]
        
        if len(self.requests[identifier]) >= limit:
            return False
        
        self.requests[identifier].append(current_time)
        return True

rate_limiter = RateLimiter()
