from flask import Flask, request, jsonify
import requests
from datetime import datetime
import json
import os

app = Flask(__name__)

# Path to the JSON file
PREFERENCES_FILE = "/app/data/filter_preferences.json"

def load_preferences():
    """Load preferences from JSON file, create if doesn't exist"""
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(PREFERENCES_FILE), exist_ok=True)
        
        if not os.path.exists(PREFERENCES_FILE):
            # Create with proper permissions
            with open(PREFERENCES_FILE, 'w') as f:
                json.dump({"saved_preferences": []}, f, indent=4)
            # Set file permissions
            os.chmod(PREFERENCES_FILE, 0o666)
        
        with open(PREFERENCES_FILE, 'r') as f:
            data = json.load(f)
            print(f"Loaded preferences: {data}")  # Debug log
            return data
    except Exception as e:
        print(f"Error loading preferences: {str(e)}")  # Debug log
        return {"saved_preferences": []}

def save_preferences(preferences_data):
    """Save preferences to JSON file"""
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(PREFERENCES_FILE), exist_ok=True)
        
        with open(PREFERENCES_FILE, 'w') as f:
            json.dump(preferences_data, f, indent=4)
        # Set file permissions
        os.chmod(PREFERENCES_FILE, 0o666)
        
        print(f"Saved preferences: {preferences_data}")  # Debug log
        return True
    except Exception as e:
        print(f"Error saving preferences: {str(e)}")  # Debug log
        return False

@app.route("/filter_tasks", methods=["GET"])
def filter_tasks():
    # Get filter parameters
    priority = request.args.get("priority")
    due_date = request.args.get("due_date")
    completed = request.args.get("completed")
    
    # Get all tasks
    response = requests.get("http://task_stats:5001/view_tasks")
    if not response.ok:
        return jsonify({"error": "Error fetching tasks from task_stats service"}), 500
    
    tasks = response.json()["tasks"]
    filtered_tasks = tasks

    # Apply priority filter if specified
    if priority and priority != "all":
        filtered_tasks = [task for task in filtered_tasks if task.get("priority") == priority]
    
    # Apply completion status filter if specified
    if completed is not None:
        completed_bool = completed.lower() == "true"
        filtered_tasks = [task for task in filtered_tasks if task.get("completed") == completed_bool]
    
    # Apply due date filter if specified
    if due_date:
        try:
            due_date = datetime.strptime(due_date, "%Y-%m-%d").date()
            filtered_tasks = [
                task for task in filtered_tasks 
                if datetime.strptime(task.get("due_date", ""), "%Y-%m-%d").date() == due_date
            ]
        except ValueError:
            return jsonify({"error": "Invalid date format"}), 400

    return jsonify({"filtered_tasks": filtered_tasks})

@app.route("/save_filter_preferences", methods=["POST"])
def save_filter_preferences():
    try:
        new_preferences = request.json
        if not new_preferences:
            return jsonify({"error": "No preferences provided"}), 400

        print(f"Received preferences: {new_preferences}")  # Debug log

        # Add timestamp to preferences
        new_preferences["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Save only the new preference (overwrite existing)
        preferences_data = {"saved_preferences": [new_preferences]}
        
        # Save updated preferences
        if save_preferences(preferences_data):
            return jsonify({"message": "Filter preferences saved successfully"})
        else:
            return jsonify({"error": "Failed to save preferences"}), 500
    
    except Exception as e:
        print(f"Error in save_filter_preferences: {str(e)}")  # Debug log
        return jsonify({"error": f"Error saving preferences: {str(e)}"}), 500

@app.route("/get_saved_preferences", methods=["GET"])
def get_saved_preferences():
    try:
        preferences_data = load_preferences()
        print(f"Retrieved preferences: {preferences_data}")  # Debug log
        return jsonify(preferences_data)
    except Exception as e:
        print(f"Error in get_saved_preferences: {str(e)}")  # Debug log
        return jsonify({"error": f"Error loading preferences: {str(e)}"}), 500

@app.route("/clear_preferences", methods=["POST"])
def clear_preferences():
    try:
        if save_preferences({"saved_preferences": []}):
            return jsonify({"message": "Preferences cleared successfully"})
        else:
            return jsonify({"error": "Failed to clear preferences"}), 500
    except Exception as e:
        print(f"Error in clear_preferences: {str(e)}")  # Debug log
        return jsonify({"error": f"Error clearing preferences: {str(e)}"}), 500

if __name__ == "__main__":
    # Initialize preferences file with proper permissions
    if not os.path.exists(PREFERENCES_FILE):
        os.makedirs(os.path.dirname(PREFERENCES_FILE), exist_ok=True)
        with open(PREFERENCES_FILE, 'w') as f:
            json.dump({"saved_preferences": []}, f, indent=4)
        os.chmod(PREFERENCES_FILE, 0o666)
    
    app.run(host="0.0.0.0", port=5003)