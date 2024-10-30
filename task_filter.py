from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route("/filter_tasks", methods=["GET"])
def filter_tasks():
    priority = request.args.get("priority")
    response = requests.get("http://task_stats:5001/view_tasks")
    if response.ok:
        tasks = response.json()["tasks"]
        filtered_tasks = [task for task in tasks if task.get("priority") == priority]
        return jsonify({"filtered_tasks": filtered_tasks})
    else:
        return jsonify({"error": "Error fetching tasks from task_stats service"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003)