from app import create_app
from flask import render_template
from datetime import datetime

app = create_app()

@app.context_processor
def inject_now():
    return {'now': datetime.utcnow()}

@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404

@app.errorhandler(403)
def forbidden(e):
    return render_template('errors/403.html'), 403

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('errors/500.html'), 500

if __name__ == '__main__':
    app.run(debug=False, port=5008)