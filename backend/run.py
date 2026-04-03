import os
from app import create_app
from app.config import config

if __name__ == '__main__':
    env = os.getenv('FLASK_ENV', 'development')
    app = create_app(env)
    
    debug = (env == 'development') and os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
    port = int(os.getenv('FLASK_PORT', 5000))
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )
