from flask import Flask, request, jsonify
from query import query_class
from flask_cors import CORS, cross_origin

app = Flask(__name__)

CORS(app, resources={r"/query": {"origins": "*"}})

@app.route("/", methods=["GET"])   
def hello():
    return "Hello, World!", 200


@app.route("/query", methods=["POST", "OPTIONS"])
def handle_query():
    print("Request received!")
    if request.method == "OPTIONS":
        # Preflight request, return the necessary headers
        return jsonify({'message': 'CORS preflight passed'}), 200
    
    try:
        # Get the input from JSON
        data = request.get_json()
        user_input = data.get('query')

        if not user_input:
            return jsonify({"error": "No query provided"}), 400
        print(f"Query: {user_input}")  # Debug print
        result = query_class(user_input)
        if result is None:
            print("Result is None")
        else:
            print(f"Result: {result}")  # Debug print
        print(result)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": f"Error processing request: {e}"}), 400

if __name__ == "__main__":  
    app.run(host='0.0.0.0', port=5001)
