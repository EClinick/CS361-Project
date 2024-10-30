from flask import Flask, jsonify, request
from datetime import datetime, timedelta
import requests

app = Flask(__name__)

@app.route("/reminders", methods=["GET"])
def get_reminders():
    response = requests.get("http://task_stats:5001/view_tasks")
    if response.ok:
        tasks = response.json()["tasks"]
        upcoming_tasks = [
            task for task in tasks 
            if datetime.strptime(task["due_date"], "%Y-%m-%d") <= datetime.now() + timedelta(days=1)
        ]
        return jsonify({"upcoming_tasks": upcoming_tasks})
    else:
        return jsonify({"error": "Error fetching tasks from task_stats service"}), 500

@app.route("/mark_complete", methods=["POST"])
def mark_complete():
    task_id = request.json.get("id")
    response = requests.get("http://task_stats:5001/view_tasks")
    if response.ok:
        tasks = response.json()["tasks"]
        for task in tasks:
            if task["id"] == task_id:
                task["completed"] = True
                update_response = requests.post("http://task_stats:5001/update_task", json=task)
                if update_response.ok:
                    return jsonify({"message": "Task marked as complete!"})
                else:
                    return jsonify({"error": "Error updating task in task_stats service"}), 500
        return jsonify({"message": "Task not found!"}), 404
    else:
        return jsonify({"error": "Error fetching tasks from task_stats service"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)