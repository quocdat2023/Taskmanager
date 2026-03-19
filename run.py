try:
    import eventlet
    eventlet.monkey_patch()
except ImportError:
    pass

import os
from app import create_app
from app.extensions import socketio

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 7860))
    print(" * Serving Flask app 'app'")
    print(" * Debug mode: off")
    print(f" * Running on all addresses (0.0.0.0)")
    print(f" * Running on http://127.0.0.1:{port}")
    print(" * WebSockets (Socket.IO) are ENABLED via eventlet")
    socketio.run(app, debug=False, use_reloader=False, host='0.0.0.0', port=port, allow_unsafe_werkzeug=True)
