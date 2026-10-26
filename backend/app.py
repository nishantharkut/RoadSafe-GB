import os
from flask import Flask, jsonify
from flask_cors import CORS
from backend.config import Config
from backend.routes.health import health_bp
from backend.routes.overview import overview_bp
from backend.routes.trends import trends_bp
from backend.routes.hotspots import hotspots_bp
from backend.routes.severity import severity_bp
from backend.routes.collisions import collisions_bp
from backend.routes.data_quality import data_quality_bp

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Configure CORS for local development
    CORS(app, origins=config_class.CORS_ORIGINS, supports_credentials=True)
    
    # Register blueprints
    app.register_blueprint(health_bp)
    app.register_blueprint(overview_bp)
    app.register_blueprint(trends_bp)
    app.register_blueprint(hotspots_bp)
    app.register_blueprint(severity_bp)
    app.register_blueprint(collisions_bp)
    app.register_blueprint(data_quality_bp)
    
    # Error handlers
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"error": "Bad Request", "message": str(error)}), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Not Found", "message": "Resource not found"}), 404

    @app.errorhandler(500)
    def server_error(error):
        return jsonify({"error": "Internal Server Error", "message": "An unexpected error occurred"}), 500

    @app.route("/")
    def index():
        return jsonify({
            "name": "RoadSafe GB REST API",
            "version": "1.0.0",
            "description": "Spatial and Temporal Mining of Road Accident Patterns in Great Britain",
            "endpoints": [
                "/api/health",
                "/api/overview",
                "/api/trends",
                "/api/hotspots",
                "/api/severity-analysis",
                "/api/collisions",
                "/api/collisions/<id>",
                "/api/data-quality"
            ]
        })

    return app

app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    print(f"Starting RoadSafe GB Backend on http://127.0.0.1:{port}...")
    app.run(host="0.0.0.0", port=port, debug=Config.DEBUG)
