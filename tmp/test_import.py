import time
print("Starting import...")
start = time.time()
from flask_socketio import SocketIO
end = time.time()
print(f"flask_socketio imported in {end - start:.2f} seconds")

print("Importing app.extensions...")
start = time.time()
try:
    from app.extensions import socketio
    print(f"app.extensions imported in {time.time() - start:.2f} seconds")
except Exception as e:
    print(f"Error importing app.extensions: {e}")
