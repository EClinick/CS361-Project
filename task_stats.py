from flask import Flask, jsonify, request
from datetime import datetime, timedelta

app = Flask(__name__)

tasks = []


@app.route("/stats", methods=["GET"])
def get_stats():
    total_tasks = len(tasks)
    completed_tasks = sum(task.get("completed", False) for task in tasks)
    pending_tasks = total_tasks - completed_tasks

    # Calculate average completion time
    completion_times = []
    for task in tasks:
        if task.get("completed", False) and task.get("stopped_at"):
            created_at = datetime.strptime(task["created_at"], "%Y-%m-%d %H:%M:%S")
            stopped_at = datetime.strptime(task["stopped_at"], "%Y-%m-%d %H:%M:%S")
            completion_times.append((stopped_at - created_at).total_seconds())

    avg_completion_time = sum(completion_times) / len(completion_times) if completion_times else 0
    # Formatting the output to display min and sec instead of seconds
    avg_completion_time = f"{int(avg_completion_time // 60)} min {int(avg_completion_time % 60)} sec"

    return jsonify({
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "pending_tasks": pending_tasks,
        "avg_completion_time": avg_completion_time
    })

@app.route("/task_summary", methods=["GET"])
def task_summary():
    summary = {
        "low": {"completed": 0, "not_completed": 0},
        "medium": {"completed": 0, "not_completed": 0},
        "high": {"completed": 0, "not_completed": 0}
    }
    for task in tasks:
        priority = task.get("priority", "low")
        if task.get("completed", False):
            summary[priority]["completed"] += 1
        else:
            summary[priority]["not_completed"] += 1

    return jsonify(summary)

@app.route("/completion_times", methods=["GET"])
def completion_times():
    # Return a list of completion times (in seconds) for completed tasks
    completion_times = []
    for task in tasks:
        if task.get("completed", False) and task.get("stopped_at"):
            created_at = datetime.strptime(task["created_at"], "%Y-%m-%d %H:%M:%S")
            stopped_at = datetime.strptime(task["stopped_at"], "%Y-%m-%d %H:%M:%S")
            completion_time = (stopped_at - created_at).total_seconds()
            completion_times.append({"completion_time": completion_time})

    return jsonify(completion_times)

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