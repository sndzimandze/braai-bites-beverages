"""
Quick run script for Braai Bites & Beverages
Runs on port 5002 to avoid conflicts
"""
import sys
import io
from app import create_app

# Fix Unicode encoding for Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Create the Flask app instance (needed for gunicorn)
app = create_app()

if __name__ == '__main__':
    PORT = 5002
    print("\n" + "="*60)
    print("Braai Bites & Beverages is starting...")
    print("="*60)
    print(f"\nApplication running at: http://localhost:{PORT}")
    print(f"Press CTRL+C to stop the server\n")
    print("="*60 + "\n")

    app.run(
        host='0.0.0.0',
        port=PORT,
        debug=True
    )
