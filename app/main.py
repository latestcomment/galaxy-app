from flask import Flask, jsonify, render_template, request
import sqlite3
import asyncio
import websockets
import json
import threading

from subscribe import start_websocket_listener
from database import Database

app = Flask(__name__)

# Flask routes
@app.route('/')
def home():
    return render_template("index.html")

@app.route('/dash')
def dash():
    return render_template('dash.html')

@app.route('/trades', methods=['GET'])
def get_trades():
    conn = sqlite3.connect("test.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM trades")
    rows = cursor.fetchall()
    conn.close()
    
    # Parse trades into JSON-friendly format
    trades = [row for row in rows]
    return jsonify(trades)

if __name__ == '__main__':
    
    ca = "2RVftrRbF1uocTuPVWmLzy1tnxArspgjQAGE3GVSpump"
    total_token = float(1000000000.0)

    # Start WebSocket listener in a separate thread
    websocket_thread = threading.Thread(target=start_websocket_listener, args=(ca, total_token,), daemon=True)
    websocket_thread.start()
    
    # Run Flask app
    app.run(debug=True)