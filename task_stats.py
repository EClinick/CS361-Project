from flask import Flask, jsonify, request
from datetime import datetime, timedelta

app = Flask(__name__)

tasks = []

@app.route("/stats", methods=["GET"])
def get_stats():
    total_tasks = len(tasks)
    completed_tasks = sum(task.get("completed", False) for task in tasks)
    pending_tasks = total_tasks - completed_tasks
    return jsonify({
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "pending_tasks": pending_tasks
    })

@app.route("/add_task", methods=["POST"])
def add_task():
    task = request.json
    tasks.append(task)
    return jsonify({"message": "Task added successfully!"})

@app.route("/view_tasks", methods=["GET"])
def view_tasks():
    return jsonify({"tasks": tasks})

@app.route("/update_task", methods=["POST"])
def update_task():
    task_data = request.json
    task_id = task_data.get("id")
    for task in tasks:
        if task["id"] == task_id:
            task.update(task_data)
            return jsonify({"message": "Task updated successfully!"})
    return jsonify({"error": "Task not found!"}), 404

@app.route("/delete_task", methods=["POST"])
def delete_task():
    task_id = request.json.get("id")
    global tasks
    tasks = [task for task in tasks if task["id"] != task_id]
    return jsonify({"message": "Task deleted successfully!"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)