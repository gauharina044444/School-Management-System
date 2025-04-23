from app import create_app
from datetime import datetime

app = create_app()

@app.context_processor
def inject_now():
    return {'now': datetime.utcnow()}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5007, debug=True, use_reloader=False)