def register_routes(app):
    """Register all route blueprints with the Flask app.

    Add your blueprints here. Example:
        from app.routes.products import products_bp
        app.register_blueprint(products_bp)
    """
    from app.routes.user import user_bp
    from app.routes.url import url_bp
    from app.routes.redirect import redirect_bp
    
    app.register_blueprint(user_bp, url_prefix="/api")
    app.register_blueprint(url_bp, url_prefix="/api")
    app.register_blueprint(redirect_bp)
