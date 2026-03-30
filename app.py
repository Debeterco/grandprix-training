from flask import Flask, jsonify, request
from flask_cors import CORS
from database import init_db, get_connection
import datetime

app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)

# Principal page
@app.route('/')
def index():
    return app.send_static_file('index.html')

# Status page
@app.route('/status')
def status():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) as total FROM orders')
    result = cursor.fetchone()
    conn.close()
    return jsonify({
        "status": "online",
        "system": "Production Orders System",
        "version": "1.0.0",
        "total_orders": result["total"],
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d%H:%M:%S")
    })

# Orders page
@app.route('/orders', methods=['GET'])
def listar_ordens():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM orders ORDER BY id DESC')
    orders = cursor.fetchall()
    conn.close()
    return jsonify([dict(o) for o in orders])

# Factory page
@app.route('/factory/<WEG>')
def boas_vindas(WEG):
    return jsonify({
    "menssage": f"Welcome, {WEG}! OP System online."
    })
    
if __name__ == '__main__':
    init_db()
    
app.run(debug=True, host='0.0.0.0', port=5000)