from flask import Flask, request, jsonify

app = Flask(__name__)


users = {}

@app.route("/users", methods=["POST"])
def create_user():
    user_id = request.json.get("id")
    user_data = request.json
    users[user_id] = user_data
    return jsonify({"message": "User created successfully!"}), 201

@app.route("/users/<user_id>", methods=["GET"])
def get_user(user_id):
    user_data = users.get(user_id)
    if user_data:
        return jsonify(user_data)
    else:
        return jsonify({"message": "User not found!"}), 404

@app.route("/users/<user_id>", methods=["PUT"])
def update_user(user_id):
    user_data = request.json
    if user_id in users:
        users[user_id] = user_data
        return jsonify({"message": "User updated successfully!"})
    else:
        return jsonify({"message": "User not found!"}), 404

@app.route("/users/<user_id>", methods=["DELETE"])
def delete_user(user_id):
    if user_id in users:
        del users[user_id]
        return jsonify({"message": "User deleted successfully!"})
    else:
        return jsonify({"message": "User not found!"}), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5006)