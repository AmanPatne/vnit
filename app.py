from flask import Flask
from routes import init_routes  # if using modular routing
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Secure sessions

# Initialize routes
init_routes(app)

if __name__ == '__main__':
    app.run(debug=True)
