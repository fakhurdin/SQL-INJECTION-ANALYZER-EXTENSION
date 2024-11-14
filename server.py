# server.py
from flask import Flask, request, jsonify
import scan  # Make sure scan.py is in the same directory

app = Flask(__name__)

@app.route('/scan', methods=['POST'])
def scan_url():
    data = request.json
    url = data.get('url')
    # Call the scanning function in scan.py with the given URL
    results = scan.sql_injection_scan(url)
    return jsonify(results=results)

if __name__ == '__main__':
    app.run(port=5000)
