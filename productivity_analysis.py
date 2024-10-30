from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

@app.route("/productivity", methods=["GET"])
def productivity():
    response = requests.get("http://task_stats:5001/view_tasks")
    if response.ok:
        tasks = response.json()["tasks"]
        completed_tasks = sum(task.get("completed", False) for task in tasks)
        total_tasks = len(tasks)
        productivity_percentage = (completed_tasks / total_tasks) * 100 if total_tasks else 0
        return jsonify({"productivity_percentage": productivity_percentage})
    else:
        return jsonify({"error": "Error fetching tasks from task_stats service"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5004)