from app import app

@app.route('/')
def api():
    return "Hellow World"
