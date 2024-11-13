import streamlit as st
import requests
import pandas as pd
import uuid
from datetime import datetime
# from streamlit_calendar import calendar
# import matplotlib.pyplot as plt

# Microservice URLs
TASK_STATS_URL = "http://task_stats:5001"
REMINDER_SERVICE_URL = "http://reminder_service:5002"
TASK_FILTER_URL = "http://task_filter:5003"
PRODUCTIVITY_ANALYSIS_URL = "http://productivity_analysis:5004"

# Initialize session state for undo and redo stacks
if "undo_stack" not in st.session_state:
    st.session_state["undo_stack"] = []
if "redo_stack" not in st.session_state:
    st.session_state["redo_stack"] = []

# Initialize session state for messages
if "add_task_form_message" not in st.session_state:
    st.session_state["add_task_form_message"] = ""
if "add_task_quick_message" not in st.session_state:
    st.session_state["add_task_quick_message"] = ""
if "mark_complete_message" not in st.session_state:
    st.session_state["mark_complete_message"] = ""
if "undo_message" not in st.session_state:
    st.session_state["undo_message"] = ""
if "redo_message" not in st.session_state:
    st.session_state["redo_message"] = ""

def reset_form():
    st.session_state['add_task_title_form'] = ''
    st.session_state['add_task_description_form'] = ''
    st.session_state['add_task_due_date_form'] = pd.to_datetime("today")
    st.session_state['add_task_priority_form'] = 'low'

def add_task_form():
    st.header("Add Task (Form)")
    
    # Explain benefits and costs
    st.info("**Benefits:** Helps you keep track of your tasks, ensuring nothing is overlooked.")
    st.warning("**Costs:** Requires time to input each task, which may be time-consuming if adding many tasks.")

    # Display success or error message for Add Task Form
    if st.session_state["add_task_form_message"]:
        st.success(st.session_state["add_task_form_message"])
        st.session_state["add_task_form_message"] = ""  # Clear message after displaying

    with st.form(key='add_task_form', clear_on_submit=True):  # Ensure clear_on_submit=True
        title = st.text_input("Enter task title:")
        description = st.text_area("Enter task description:")
        due_date = st.date_input("Enter due date:", value=pd.to_datetime("today"))
        priority_options = ["low", "medium", "high"]
        priority = st.selectbox("Select priority:", priority_options, index=0)
        submit_button = st.form_submit_button(label='Add Task (Form)')

    
    if submit_button:
        if not title and not description:
            st.session_state["add_task_form_message"] = "Task title and description cannot be empty."
            # st.write("Add Task Form: Title and Description are empty.")
            st.error(st.session_state["add_task_form_message"])
            st.session_state["add_task_form_message"] = ""
            return
        else:
            handle_add_task(title, description, due_date, priority, message_type="form")

def add_task_quick():
    st.header("Quick Add Task")
    
    # Explain benefits and costs
    st.info("**Benefits:** Quickly add tasks with minimal input for faster task management.")
    st.warning("**Costs:** Limited information is captured, which may result in less detailed task tracking.")
    

    # Display success or error message for Quick Add Task
    if st.session_state["add_task_quick_message"]:
        st.success(st.session_state["add_task_quick_message"])
        st.session_state["add_task_quick_message"] = ""  # Clear message after displaying

    with st.form(key='add_task_quick_form', clear_on_submit=True):  # Ensure clear_on_submit=True
        title = st.text_input("Enter task title:")
        submit_button = st.form_submit_button(label='Quick Add Task')

    if submit_button:
        # st.write("Quick Add Task: Submit button clicked")
        # st.write(f"Title entered: {title}")
        if not title:
            st.session_state["add_task_quick_message"] = "Task title cannot be empty."
            # st.write("Quick Add Task: Title is empty")
            st.error(st.session_state["add_task_quick_message"])
            st.session_state["add_task_quick_message"] = ""
        else:
            # st.write("Quick Add Task: Title provided")
            # Add due_date as today's date
            due_date = pd.to_datetime("today")
            handle_add_task(title, "", due_date, "low", message_type="quick")

def handle_add_task(title, description, due_date, priority, message_type):
    #st.write("Task title:\n", title, "\nTask description:", description, "\nDue date:", due_date, "Priority:", priority)
    if not title or not description and message_type == "form":
        # Set respective session message based on message_type

        st.session_state["add_task_form_message"] = "Task title/description cannot be empty."
        st.error(st.session_state["add_task_form_message"])
        st.session_state["add_task_form_message"] = ""
        return
    elif not title and message_type == "quick":
        st.session_state["add_task_quick_message"] = "Task title cannot be empty."
        st.error(st.session_state["add_task_quick_message"])
        st.session_state["add_task_form_message"] = ""
        return
    # if description=="":
    #     if message_type == "form":
    #         st.session_state["add_task_form_message"] = "Task description cannot be empty."
    #     else:
    #         st.write("Msg type",message_type)

    task_data = {
        "id": str(uuid.uuid4()),
        "title": title,
        "description": description,
        "due_date": due_date.strftime("%Y-%m-%d") if due_date else "",
        "priority": priority,
        "completed": False,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "stopped_at": None
    }

    response = requests.post(f"{TASK_STATS_URL}/add_task", json=task_data)
    if response.ok:
        success_message = f"Task '{title}' added successfully!"
        if message_type == "form":
            st.session_state["add_task_form_message"] = success_message
            st.success(st.session_state["add_task_form_message"])
            st.session_state["add_task_form_message"] = ""
        elif message_type == "quick":
            st.session_state["add_task_quick_message"] = success_message
            st.success(st.session_state["add_task_quick_message"])
            st.session_state["add_task_quick_message"] = ""
        # Log the action for undo functionality
        action = {"action": "add_task", "task": task_data}
        st.session_state["undo_stack"].append(action)
        # Clear the redo stack
        st.session_state["redo_stack"].clear()
    else:
        error_message = "Error adding task."
        if message_type == "form":
            st.session_state["add_task_form_message"] = error_message
        elif message_type == "quick":
            st.session_state["add_task_quick_message"] = error_message

def mark_task_complete_list():
    st.header("Mark Task Complete (List)")

    # Explain benefits and costs
    st.info("**Benefits:** Allows you to mark specific tasks as complete, helping you track your progress.")
    st.warning("**Costs:** Requires manual input of task ID, which might be prone to errors if IDs are mistyped.")

    # Display success or error message
    if st.session_state["mark_complete_message"]:
        st.success(st.session_state["mark_complete_message"])
        st.session_state["mark_complete_message"] = ""  # Clear message after displaying

    if st.session_state["undo_message"]:
        st.success(st.session_state["undo_message"])
        st.session_state["undo_message"] = ""
    if st.session_state["redo_message"]:
        st.success(st.session_state["redo_message"])
        st.session_state["redo_message"] = ""

    # Callback function for "Yes" button
    def confirm_yes():
        confirm_id = st.session_state.get("confirm_mark_complete_list")
        handle_mark_task_complete(confirm_id)
        # Reset the input field
        st.session_state["mark_complete_list_input"] = ""
        # Remove the confirmation flag
        del st.session_state["confirm_mark_complete_list"]

    # Callback function for "No" button
    def confirm_no():
        # Remove the confirmation flag
        del st.session_state["confirm_mark_complete_list"]

    # Assign a key to the text input for managing its state
    task_id = st.text_input("Enter task ID to mark as complete:", key="mark_complete_list_input")

    if st.button("Mark as Complete (List)"):
        if task_id:  # Ensure that task_id is not empty
            st.session_state["confirm_mark_complete_list"] = task_id
        else:
            st.error("Please enter a valid Task ID.")

    if "confirm_mark_complete_list" in st.session_state:
        confirm_id = st.session_state["confirm_mark_complete_list"]
        st.warning("Are you sure you want to mark this task as complete?")
        col1, col2 = st.columns(2)
        with col1:
            st.button("Yes", on_click=confirm_yes)
        with col2:
            st.button("No", on_click=confirm_no)

def mark_task_complete_checkbox():
    st.header("Mark Task Complete (Checkbox)")

    # Explain benefits and costs
    st.info("**Benefits:** Easily mark tasks as complete using checkboxes for a more interactive experience.")
    st.warning("**Costs:** May become cumbersome if there are a large number of tasks to mark.")

    # Display success or error messages
    if st.session_state["mark_complete_message"]:
        st.success(st.session_state["mark_complete_message"])
        st.session_state["mark_complete_message"] = ""  # Clear message after displaying

    if st.session_state["undo_message"]:
        st.success(st.session_state["undo_message"])
        st.session_state["undo_message"] = ""
    if st.session_state["redo_message"]:
        st.success(st.session_state["redo_message"])
        st.session_state["redo_message"] = ""

    # Callback function for "Yes" button
    def confirm_yes_checkbox(task_id):
        handle_mark_task_complete(task_id)
        # Remove the confirmation flag
        del st.session_state[f"confirm_mark_complete_{task_id}"]

    # Callback function for "No" button
    def confirm_no_checkbox(task_id):
        # Remove the confirmation flag
        del st.session_state[f"confirm_mark_complete_{task_id}"]

    response = requests.get(f"{TASK_STATS_URL}/view_tasks")
    if response.ok:
        tasks = response.json()["tasks"]
        for task in tasks:
            if not task.get("completed", False):
                checkbox_key = f"complete_{task['id']}"
                if st.checkbox(f"{task['title']} (ID: {task['id']})", key=checkbox_key):
                    st.session_state[f"confirm_mark_complete_{task['id']}"] = task["id"]

                    if f"confirm_mark_complete_{task['id']}" in st.session_state:
                        st.warning("Are you sure you want to mark this task as complete?")
                        col1, col2 = st.columns(2)
                        with col1:
                            st.button("Yes", on_click=confirm_yes_checkbox, args=(task["id"],))
                        with col2:
                            st.button("No", on_click=confirm_no_checkbox, args=(task["id"],))
    else:
        st.error("Error fetching tasks.")

def handle_mark_task_complete(task_id):
    if not task_id:
        st.session_state["mark_complete_message"] = "Task ID cannot be empty."
        return

    # Communicate with reminder_service to mark the task as complete
    response = requests.post(f"{REMINDER_SERVICE_URL}/mark_complete", json={"id": task_id})

    if response.ok:
        # Set success message in session state
        st.session_state["mark_complete_message"] = response.json().get("message", "Task marked as complete!")
        # Log the action for undo functionality
        action = {"action": "mark_complete", "task_id": task_id}
        st.session_state["undo_stack"].append(action)
        # Clear the redo stack
        st.session_state["redo_stack"].clear()
    else:
        # Set error message in session state
        st.session_state["mark_complete_message"] = "Error marking task as complete."

def view_tasks():
    st.header("View Tasks")
    
    # Explain benefits and costs
    st.info("**Benefits:** Provides a comprehensive overview of all your tasks, helping you manage them efficiently. Use the filter options to narrow down your tasks.")
    st.warning("**Costs:** Displaying a large number of tasks may make the interface cluttered and harder to navigate.")

    # Initialize session state if needed
    if "clear_filters" not in st.session_state:
        st.session_state.clear_filters = False

    # Load saved preferences
    saved_prefs_response = requests.get(f"{TASK_FILTER_URL}/get_saved_preferences")
    saved_preference = None
    if saved_prefs_response.ok:
        preferences_data = saved_prefs_response.json()
        if preferences_data.get("saved_preferences"):
            saved_preference = preferences_data["saved_preferences"][0]  # Get the single saved preference

    # Initialize filter values from saved preference or defaults
    default_priority = saved_preference.get("priority", "all") if saved_preference else "all"
    default_completed = saved_preference.get("completed", "all") if saved_preference else "all"
    default_date = None
    if saved_preference and saved_preference.get("due_date"):
        try:
            default_date = datetime.strptime(saved_preference["due_date"], "%Y-%m-%d").date()
        except ValueError:
            default_date = None

    # Filter section
    with st.expander("Filter Options"):
        # Create three columns for filters
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Create sub-columns for filter inputs
            filter_col1, filter_col2, filter_col3 = st.columns(3)
            with filter_col1:
                priority = st.selectbox(
                    "Priority Filter", 
                    ["all", "low", "medium", "high"],
                    index=["all", "low", "medium", "high"].index(default_priority)
                )
            
            with filter_col2:
                due_date = st.date_input(
                    "Due Date Filter",
                    value=default_date
                )
            
            with filter_col3:
                completed = st.selectbox(
                    "Completion Status",
                    ["all", "completed", "pending"],
                    index=["all", "completed", "pending"].index(default_completed)
                )
        
        with col2:
            # Add some spacing
            st.write("")
            st.write("")
            # Create a container for buttons with custom styling
            with st.container():
                # Use HTML and CSS for better-looking buttons
                st.markdown(
                    """
                    <style>
                    .stButton > button {
                        width: 100%;
                        margin-bottom: 5px;
                    }
                    .save-btn {
                        background-color: #4CAF50;
                        color: white;
                    }
                    .clear-btn {
                        background-color: #f44336;
                        color: white;
                    }
                    .reset-btn {
                        background-color: #2196F3;
                        color: white;
                    }
                    </style>
                    """,
                    unsafe_allow_html=True
                )
                
                if st.button("💾 Save Preferences", key="save_pref"):
                    preferences = {
                        "priority": priority,
                        "due_date": due_date.strftime("%Y-%m-%d") if due_date else None,
                        "completed": completed
                    }
                    response = requests.post(f"{TASK_FILTER_URL}/save_filter_preferences", json=preferences)
                    if response.ok:
                        st.success("Filter preferences saved!")
                        st.rerun()

                if st.button("🗑️ Clear Saved", key="clear_pref"):
                    response = requests.post(f"{TASK_FILTER_URL}/clear_preferences")
                    if response.ok:
                        st.success("Saved preferences cleared!")
                        st.rerun()
                
                # if st.button("🔄 Reset Filters", key="reset_filters"):
                #     st.rerun()

    # Fetch and display filtered tasks
    params = {}
    if priority != "all":
        params["priority"] = priority
    if due_date:
        params["due_date"] = due_date.strftime("%Y-%m-%d")
    if completed != "all":
        params["completed"] = "true" if completed == "completed" else "false"

    response = requests.get(f"{TASK_FILTER_URL}/filter_tasks", params=params)
    if response.ok:
        tasks = response.json()["filtered_tasks"]
        if tasks:
            df = pd.DataFrame(tasks)
            
            # Reorder and rename columns for better presentation
            columns_order = [
                'title', 'description', 'priority', 'due_date', 
                'completed', 'created_at', 'id'
            ]
            columns_rename = {
                'title': 'Title',
                'description': 'Description',
                'priority': 'Priority',
                'due_date': 'Due Date',
                'completed': 'Completed',
                'created_at': 'Created At',
                'id': 'ID'
            }
            
            # Reorder and select columns
            df = df[columns_order]
            
            # Rename columns
            df = df.rename(columns=columns_rename)
            
            # Format date columns
            df['Due Date'] = pd.to_datetime(df['Due Date']).dt.strftime('%Y-%m-%d')
            df['Created At'] = pd.to_datetime(df['Created At']).dt.strftime('%Y-%m-%d %H:%M')
            
            # Add custom styling
            st.markdown("""
                <style>
                .stDataFrame {
                    font-family: 'Arial', sans-serif;
                }
                .dataframe {
                    border-collapse: collapse;
                    margin: 25px 0;
                    font-size: 0.9em;
                    min-width: 400px;
                    border-radius: 5px 5px 0 0;
                    overflow: hidden;
                    box-shadow: 0 0 20px rgba(0, 0, 0, 0.15);
                }
                .dataframe thead tr {
                    background-color: #009879;
                    color: #ffffff;
                    text-align: left;
                    font-weight: bold;
                }
                .dataframe th,
                .dataframe td {
                    padding: 12px 15px;
                }
                .dataframe tbody tr {
                    border-bottom: 1px solid #dddddd;
                }
                .dataframe tbody tr:nth-of-type(even) {
                    background-color: #f3f3f3;
                }
                .dataframe tbody tr:last-of-type {
                    border-bottom: 2px solid #009879;
                }
                </style>
            """, unsafe_allow_html=True)
            
            # Display the styled dataframe
            st.dataframe(
                df,
                column_config={
                    "Title": st.column_config.TextColumn(
                        "Title",
                        width="small",
                        help="Task title"
                    ),
                    "Description": st.column_config.TextColumn(
                        "Description",
                        width="large",
                        help="Task description"
                    ),
                    "Priority": st.column_config.SelectboxColumn(
                        "Priority",
                        width="small",
                        options=["low", "medium", "high"],
                        help="Task priority level"
                    ),
                    "Due Date": st.column_config.DateColumn(
                        "Due Date",
                        width="small",
                        format="YYYY-MM-DD",
                        help="Task due date"
                    ),
                    "Completed": st.column_config.CheckboxColumn(
                        "Completed",
                        width="small",
                        help="Task completion status"
                    ),
                    "Created At": st.column_config.DatetimeColumn(
                        "Created At",
                        width="small",
                        format="YYYY-MM-DD HH:mm",
                        help="Task creation date and time"
                    ),
                    "ID": st.column_config.TextColumn(
                        "ID",
                        width="large",
                        help="Task unique identifier"
                    )
                },
                hide_index=True,
                use_container_width=True
            )
        else:
            st.info("No tasks match the current filters.")
    else:
        st.error("Error fetching tasks.")

def get_task_stats():
    st.title("📊 Task Statistics Overview")
    
    # Top containers for key stats
    col1, col2, col3 = st.columns(3)
    with col1:
        response = requests.get(f"{TASK_STATS_URL}/stats")
        if response.ok:
            stats = response.json()
            st.metric(label="Total Tasks", value=stats["total_tasks"])
            st.metric(label="Completed Tasks", value=stats["completed_tasks"])
            st.metric(label="Pending Tasks", value=stats["pending_tasks"])
            st.metric(label="Avg Completion Time", value=stats["avg_completion_time"])
        else:
            st.error("Error fetching stats.")

    # Stacked bar chart for task completion by priority
    st.markdown("### Task Completion by Priority")
    response = requests.get(f"{TASK_STATS_URL}/task_summary")
    if response.ok and response.json():  # Check if data exists
        summary = response.json()
        df = pd.DataFrame.from_dict(summary, orient="index")
        df.columns = ["Completed", "Not Completed"]
        
        # Display the stacked bar chart only if data is available
        with st.container():
            st.bar_chart(df)
    else:
        st.info("No data available for task completion by priority.")

    # Scatter plot for task completion times
    st.markdown("### Task Completion Times")
    response = requests.get(f"{TASK_STATS_URL}/completion_times")
    if response.ok and response.json():  # Check if data exists
        completion_times = response.json()
        completion_df = pd.DataFrame(completion_times)

        # Ensure that we have 'completion_time' column for scatter plot
        if 'completion_time' in completion_df.columns:
            with st.container():
                st.write("Completion times (in seconds) for completed tasks")
                st.scatter_chart(completion_df[['completion_time']])
    else:
        st.info("No data available for task completion times.")


def productivity_analysis():
    st.header("Productivity Analysis")
    
    # Explain benefits and costs
    st.info("**Benefits:** Helps you understand your work patterns and improve efficiency by analyzing your task completion rates.")
    st.warning("**Costs:** Productivity analysis requires all tasks to be accurately marked as complete for precise results.")

    # Display success or error message for Productivity Analysis
    # Removed referencing add_task_message to prevent interference
    if st.session_state["undo_message"]:
        st.success(st.session_state["undo_message"])
        st.session_state["undo_message"] = ""
    if st.session_state["redo_message"]:
        st.success(st.session_state["redo_message"])
        st.session_state["redo_message"] = ""

    if st.button("Get Productivity"):
        response = requests.get(f"{PRODUCTIVITY_ANALYSIS_URL}/productivity")
        if response.ok:
            data = response.json()
            # Display the productivity data not as st.write
            st.info(f"Productivity Percentage: {data['productivity_percentage']:.2f}%",icon="🚀")
            #st.write(f"Productivity Percentage: {data['productivity_percentage']:.2f}%")
        else:
            st.error("Error fetching productivity data.")

def filter_tasks():
    st.header("Filter Tasks")
    
    # Explain benefits and costs
    st.info("**Benefits:** Enables you to focus on tasks of a specific priority, enhancing task management efficiency.")
    st.warning("**Costs:** Filtering may exclude relevant tasks if priorities are not set accurately.")

    priority = st.selectbox("Select priority to filter tasks:", ["low", "medium", "high"])
    if st.button("Filter Tasks"):
        response = requests.get(f"{TASK_FILTER_URL}/filter_tasks", params={"priority": priority})
        if response.ok:
            tasks = response.json()["filtered_tasks"]
            if tasks:
                df = pd.DataFrame(tasks)
                st.dataframe(df)
            else:
                st.info("No tasks found with selected priority.")
        else:
            st.error("Error filtering tasks.")

def display_reminders():
    st.header("Upcoming Reminders")
    
    # Explain benefits and costs
    st.info("**Benefits:** Keeps you informed about upcoming deadlines, helping you stay on top of your tasks.")
    st.warning("**Costs:** Relies on accurate due dates; incorrect dates may lead to irrelevant reminders.")

    response = requests.get(f"{REMINDER_SERVICE_URL}/reminders")
    if response.ok:
        reminders = response.json()["upcoming_tasks"]
        if reminders:
            # Only display title, priority, and due date if the task is not completed
            if "completed" in reminders[0]:
                reminders = [task for task in reminders if not task["completed"]]
                # Show only priority, title, and due date
                reminders = [{"priority": task["priority"], "title": task["title"], "due_date": task["due_date"]} for task in reminders]
            if len(reminders) > 0:

                df = pd.DataFrame(reminders)
                st.dataframe(df)
            else:
                st.info("No upcoming tasks, you've completed all your tasks!🔥")
        else:
            st.info("No upcoming tasks within the next day.")
    else:
        st.error("Error fetching reminders.")

def undo_action():
    if not st.session_state["undo_stack"]:
        st.session_state["undo_message"] = "No actions to undo."
        return

    last_action = st.session_state["undo_stack"].pop()
    action_type = last_action["action"]

    if action_type == "add_task":
        task_id = last_action["task"]["id"]
        task_title = last_action["task"]["title"]
        # Communicate with task_stats to delete the task
        response = requests.post(f"{TASK_STATS_URL}/delete_task", json={"id": task_id})
        if response.ok:
            st.session_state["undo_message"] = f"Undo: Addition of task '{task_title}' has been reverted."
            # Add to redo stack
            st.session_state["redo_stack"].append(last_action)
        else:
            st.session_state["undo_message"] = "Error undoing add task action."
    elif action_type == "mark_complete":
        task_id = last_action["task_id"]
        # Revert task to incomplete in task_stats
        response = requests.post(f"{TASK_STATS_URL}/update_task", json={"id": task_id, "completed": False})
        if response.ok:
            st.session_state["undo_message"] = f"Undo: Completion of task ID '{task_id}' has been reverted."
            # Add to redo stack
            st.session_state["redo_stack"].append(last_action)
        else:
            st.session_state["undo_message"] = "Error undoing mark complete action."

def redo_action():
    if not st.session_state["redo_stack"]:
        st.session_state["redo_message"] = "No actions to redo."
        return

    last_action = st.session_state["redo_stack"].pop()
    action_type = last_action["action"]

    if action_type == "add_task":
        task_data = last_action["task"]
        task_title = task_data["title"]
        # Re-add the task via task_stats
        response = requests.post(f"{TASK_STATS_URL}/add_task", json=task_data)
        if response.ok:
            st.session_state["redo_message"] = f"Redo: Addition of task '{task_title}' has been reapplied."
            # Add back to undo stack
            st.session_state["undo_stack"].append(last_action)
        else:
            st.session_state["redo_message"] = "Error redoing add task action."
    elif action_type == "mark_complete":
        task_id = last_action["task_id"]
        # Mark the task as complete via reminder_service
        response = requests.post(f"{REMINDER_SERVICE_URL}/mark_complete", json={"id": task_id})
        if response.ok:
            st.session_state["redo_message"] = f"Redo: Completion of task ID '{task_id}' has been reapplied."
            # Add back to undo stack
            st.session_state["undo_stack"].append(last_action)
        else:
            st.session_state["redo_message"] = "Error redoing mark complete action."

def main():
    st.sidebar.title("🔧 Task Management Controls")
    st.sidebar.markdown("Use the buttons below for quick actions.")
    st.title("🌌 Task Management Dashboard")
    # page = st.sidebar.selectbox(
    #     "Select Page",
    #     ["📝 Add Task", "✅ Mark Complete", "📋 View Tasks", 
    #      "📊 Stats", "📈 Productivity", "⏰ Reminders"]
    # )
    tabs=st.tabs(
        ["📝 Add Task", "✅ Mark Complete", "📋 View Tasks",
         "📊 Stats", "📈 Productivity", "⏰ Reminders"]
    )
    with tabs[0]:
        add_task_form()
        add_task_quick()
    with tabs[1]:
        mark_task_complete_list()
        mark_task_complete_checkbox()
    with tabs[2]:
        view_tasks()
    with tabs[3]:
        get_task_stats()
    with tabs[4]:
        productivity_analysis()
    with tabs[5]:
        display_reminders()

    st.sidebar.header("Actions")
    if st.sidebar.button("Undo Last Action"):
        undo_action()
    if st.sidebar.button("Redo Last Action"):
        redo_action()

if __name__ == "__main__":
    main()
