import os
import time
from flask import Flask, g, request, Response
from routes.games import games_bp
from models import db
from utils.database import get_connection_string

# Prometheus client for metrics
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

# Get the server directory path
base_dir: str = os.path.abspath(os.path.dirname(__file__))

app: Flask = Flask(__name__)

# Configure and initialize the database
app.config['SQLALCHEMY_DATABASE_URI'] = get_connection_string()
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Create tables
with app.app_context():
    db.create_all()

# Register blueprints
app.register_blueprint(games_bp)

# Prometheus metrics
REQUEST_COUNT = Counter(
    'flask_http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'http_status']
)

REQUEST_LATENCY = Histogram(
    'flask_request_latency_seconds',
    'Histogram of request latency (seconds)',
    ['method', 'endpoint']
)

EXCEPTION_COUNT = Counter(
    'flask_exceptions_total',
    'Total exceptions raised by endpoint',
    ['endpoint']
)


@app.before_request
def start_timer() -> None:
    g.start_time = time.time()


@app.after_request
def record_request_data(response: Response) -> Response:
    try:
        resp_time = time.time() - getattr(g, 'start_time', time.time())
        endpoint = request.endpoint or 'unknown'
        REQUEST_LATENCY.labels(method=request.method, endpoint=endpoint).observe(resp_time)
        REQUEST_COUNT.labels(method=request.method, endpoint=endpoint, http_status=response.status_code).inc()
    except Exception:
        # Don't let metrics collection break the app
        pass
    return response


@app.teardown_request
def record_exceptions(exc):
    if exc is not None:
        endpoint = request.endpoint or 'unknown'
        EXCEPTION_COUNT.labels(endpoint=endpoint).inc()


@app.route('/metrics')
def metrics() -> Response:
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5100) # Listen on all interfaces for container networking