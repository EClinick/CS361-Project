import streamlit as st
import requests
import pandas as pd
import uuid

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
    st.info("**Benefits:** Provides a comprehensive overview of all your tasks, helping you manage them efficiently.")
    st.warning("**Costs:** Displaying a large number of tasks may make the interface cluttered and harder to navigate.")

    response = requests.get(f"{TASK_STATS_URL}/view_tasks")
    if response.ok:
        tasks = response.json()["tasks"]
        if tasks:
            df = pd.DataFrame(tasks)
            st.dataframe(df)
        else:
            st.info("No tasks available.")
    else:
        st.error("Error fetching tasks.")

def get_task_stats():
    st.header("View Stats")
    
    # Explain benefits and costs
    st.info("**Benefits:** Allows you to analyze your task data, providing insights into your productivity and task distribution.")
    st.warning("**Costs:** Relies on accurate and up-to-date task data, which requires consistent task management.")

    response = requests.get(f"{TASK_STATS_URL}/stats")
    if response.ok:
        stats = response.json()
        #Format this better than JSON
        
        st.json(stats)
    else:
        st.error("Error fetching stats.")

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
    st.title("Task Management App")
    tabs = st.tabs([
        "Add Task",
        "Mark Task Complete",
        "View Tasks",
        "Get Task Stats",
        "Productivity Analysis",
        "Filter Tasks",
        "Display Reminders"
    ])

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
        filter_tasks()
    with tabs[6]:
        display_reminders()

    st.sidebar.header("Actions")
    if st.sidebar.button("Undo Last Action"):
        undo_action()
    if st.sidebar.button("Redo Last Action"):
        redo_action()

if __name__ == "__main__":
    main()