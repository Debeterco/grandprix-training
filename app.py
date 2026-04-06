"""
app.py - Back-end Flask of Production Order System.

API REST with complete CRUD, authentication by API Key,
input sanitization and global error handling

Author: João Vitor Kasteller Debeterco
Date: 2026
Version 2.0.0 (with security)
SENAI Jaragua do Sul - Tecnico em Cibersistemas para Automacao WEG
"""
import os
from dotenv import load_dotenv
from flask import Flask, jsonify, request, abort
from flask_cors import CORS
from database import init_db, get_connection
from functools import wraps
import datetime
import html

load_dotenv()
app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)

# Security config
# In production we need to use a env: os.environ.get('API_KEY')
API_KEY = os.environ.get('API_KEY')

def request_auth(f):
    """
    Decorator will protect the routes requesting an valid API_KEY.

    The client need to send the header:
        X-API-Key: <API_KEY configurated value>

    If key is incorrect or absent, return 401 Unauthorized.
    If correct, execute route normally.

    Use:
        @app.route('/route')
        @request_auth
        def my_route():
            ...
    """
    @wraps(f) # Preserve the name and docstring of the original function
    def decorator(*args, **kwargs):
        # Read the header X-API-Key requesition
        received_key = request.headers.get('X-API-Key')

        if not received_key:
            return jsonify({
                'error': 'Authentication necessary.',
                'instruction': 'Send the X-API-Key header with his key.'
            }), 401
        
        if received_key != API_KEY:
            return jsonify({
                'error': 'Invalid or expired API Key.'
            }), 403
        
        # Incorrect key: execute the route function normally
        return f(*args, **kwargs)
    return decorator

@app.errorhandler(400)
def request_invalid(error):
    return jsonify({
        'error': 'Request invalid.', 
        'detail': str(error)
    }), 400

@app.errorhandler(401)
def not_authorized(error):
    return jsonify({
        'error': 'Authentication necessary.'
    }), 401

@app.errorhandler(403)
def denied_access(error):
    return jsonify({
        'error': 'Denied access.'
    }), 403

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Resource not found.'
    }), 404

@app.errorhandler(405)
def not_allowed_method(error):
    return jsonify({
        'error': 'Not allowed HTTP method in this route.'
    }), 405

@app.errorhandler(500)
def denied_access(error):
    return jsonify({
        # Never return str(error) in production - expose stack trace
        'error': 'Error in the server. Contact the administrator.'
    }), 500

# Principal page
@app.route('/')
def index():
    return app.send_static_file('index.html')

# Status page
@app.route('/status')
def status():
    """ API Health Check with order count."""
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
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

# Orders page
@app.route('/orders', methods=['GET'])
def list_orders():
    """
    List all the production orders in descending order by ID.

    Public route - authentication not required.

    Methods:
        GET / orders
        GET / orders?status=Pending (Optional filters by status)

    Args:
        status (str, query param, optional): Orders filter by status.
            Allowed values: 'Pending', 'In Progress', 'Completed'.

    Returns:
        Response: JSON with orders list. Status HTTP 200.
        Return empty list [] if no order exists.

    Example:
        GET /orders -> 200 [{id:1, product:..., status='Pending'}, ...]
        GET /orders?status=Pending -> 200 [only pending orders]
    """
    status_filter = request.args.get('status')
    conn = get_connection()
    cursor = conn.cursor()
    if status_filter:
        cursor.execute('SELECT * FROM orders WHERE status = ? ORDER BY id DESC', (status_filter,))
    else:
        cursor.execute('SELECT * FROM orders ORDER BY id DESC')
    orders = cursor.fetchall()
    conn.close()
    return jsonify([dict(o) for o in orders])

# Factory page
@app.route('/factory/<WEG>')
def welcome(WEG):
    return jsonify({
    "message": f"Welcome, {WEG}! OP System online."
    })

# GET - Search order by ID
@app.route('/orders/<int:order_id>', methods=['GET'])
def search_order(order_id): # order_id is int
    """
    Search a unique production order by the ID.
    
    URL parameters:
        order_id(int): order ID to be searched
        
    Return:
        200 + JSON of the order, if founded.
        404 + error message, if dont exist.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # The '?' is replaced by the value of order_id in a secure way
    cursor.execute('SELECT * FROM orders WHERE id = ?', (order_id,))
    order = cursor.fetchone() # fetchone() return a unique register or None
    conn.close()
    
    if order is None:
        return jsonify({'error': f'Order {order_id} not found.'}), 404
    
    return jsonify(dict(order)), 200
    
# POST - Create new order production
@app.route('/orders', methods=['POST'])
@request_auth
def create_order():
    """
    Create a new order production by the JSON data sended.
    
    Waited Body(JSON):
        product(str): Product name. Required.
        quantity(int): Pieces quantity. Required, > 0.
        status(str): Optional. Pattern: 'Pendent'.
        
    Return:
        201 + JSON of the created order, in success case.
        400 + error message, if invalid data.
    """
    data = request.get_json()
    
    # Verify if body was sended and is a valid JSON
    if not data:
        return jsonify({'error': 'Ausent or invalid Body requisition.'}), 400
    
    # Verify required field 'product'
    # html.escape() neutralize special HTML characters
    product = html.escape(data.get('product', '').strip())
    if not product:
        return jsonify({'error': 'Field "product" is required and cant be empty.'}) , 400
    
    if len(product) > 200:
        return jsonify({
            'error': 'Long product name (max 200 characters).'
        }), 400

    # Verify required field 'quantity'
    quantity = data.get('quantity')
    if quantity is None:
        return jsonify({'error': 'Field "quantity" is required'}) , 400
    
    # Verify if quantity is a positive integer number
    try:
        quantity = int(quantity)
        if quantity <= 0 or quantity > 999999   :
            raise ValueError()
    except(ValueError, TypeError):
        return jsonify({
            'error': 'Field "quantity" is required to be a positive integer number between 1 and 999999.'
            }) , 400
    
    # Status is optional; use 'Pendent' if not informed
    valid_status = ['Pending', 'In Progress', 'Completed']
    status = data.get('status', 'Pending')
    if status not in valid_status:
        return jsonify({'error': f'Invalid status. Use:{valid_status}'}), 400
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO orders (product, quantity, status) VALUES (?, ?, ?)',
        (product, quantity, status)
    )
    conn.commit()
    
    # Recuperate the new ID automatically generated by the database
    new_id = cursor.lastrowid
    conn.close()
    
    # Searching the new register to complete return
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM orders WHERE id = ?', (new_id,))
    new_order = cursor.fetchone()
    conn.close()
    
    # Return 201 Created with a complete register
    return jsonify(dict(new_order)), 201
    
# PUT - Update Order Status
@app.route('/orders/<int:order_id>', methods=['PUT'])
@request_auth
def order_update(order_id):
    """
    Update status of an existent order.

    URL parameter: order_id (int): ID of order to update.

    Body waited (JSON):
        status (str): New status. Values accepted: 'Pending', 'In Progress', 'Completed'.
    Return:
        200 + JSON order updated.
        400 + error if invalid status.
        404 + error if order not found.
    """
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Ausent or invalid Body requisition.'}), 400
    
    # Valid status field
    valid_status = ['Pending', 'In Progress', 'Completed']
    new_status = data.get('status', '').strip()
    
    if not new_status:
        return jsonify({'error': 'Field "status" is required.'}), 400
    
    if new_status not in valid_status:
        return jsonify({'error': f'Invalid status. Allowed values:{valid_status}'}), 400
    conn = get_connection()
    cursor = conn.cursor()
    
    # Verify if order exist before update
    cursor.execute('SELECT id FROM orders WHERE id = ?', (order_id,))
    if cursor.fetchone() is None:
        conn.close()
        return jsonify({'error': f'Order {order_id} not found.'}), 404
    
    # Execute update
    cursor.execute('UPDATE orders SET status = ? WHERE id = ?',(new_status, order_id))
    conn.commit()
    conn.close()
    
    # Return register updated
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM orders WHERE id = ?', (order_id,))
    order_update = cursor.fetchone()
    conn.close()
    return jsonify(dict(order_update)), 200
    
# DELETE - Remove a order by ID
@app.route('/orders/<int:order_id>', methods=['DELETE'])
@request_auth
def order_remove(order_id):
    """
    Permanently remove a production order by ID.

    Protected route - require valid X-API-Key header.

    Methods:
        DELETE /orders/<id>
    
    URL parameters:
        order_id(int): ID of order to be removed (by URL).
    
    Returns:
        Response: JSON with confirmation message. Status 200.
        Response: JSON with error. Status 404 if ID dont exist.
        Response: JSON with error. Status 401/403 if no authentication.

    Example:
        DELETE /orders/5 -> 200 {message: 'Order 5 (Motor...) removed.'}
        DELETE /orders/999 -> 404 {message: 'Order 999 not found.'}
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # Verify existence before delete
    cursor.execute('SELECT id, product FROM orders WHERE id = ?', (order_id,))
    order = cursor.fetchone()
    
    if order is None:
        conn.close()
        return jsonify({'error': f'Order {order_id} not found.'}), 404

    product_name = order['product']
    
    # Correct DELETE
    cursor.execute('DELETE FROM orders WHERE id = ?', (order_id,))
    
    conn.commit()
    conn.close()
    
    return jsonify({
        'message': f'Order {order_id} ({product_name}) removed successfully.',
        'removed_id': order_id
    }), 200

# Entry point
if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)