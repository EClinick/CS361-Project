# Task Management API

This project is a microservices-based Task Management application that allows users to add, view, update, and analyze tasks. The application is built using Flask for backend services and Streamlit for the frontend interface. Docker Compose is used to orchestrate the services.

## Table of Contents

1. [Microservices](#microservices)
2. [Inclusivity Heuristics Justification](#inclusivity-heuristics-justification)
3. [Setup Instructions](#setup-instructions)
4. [Future Enhancements](#future-enhancements)

## Microservices

### Implemented Microservices

#### 1. Task Stats Service
- **Description:** Manages tasks and provides statistics.
- **Endpoints:**
  - **Get Statistics**
    - **URL:** `/stats`
    - **Method:** `GET`
    - **Description:** Returns the total number of tasks, the number of completed tasks, and the number of pending tasks.
  - **Add Task**
    - **URL:** `/add_task`
    - **Method:** `POST`
    - **Description:** Adds a new task.
    - **Request Body:** JSON object representing the task.
  - **View Tasks**
    - **URL:** `/view_tasks`
    - **Method:** `GET`
    - **Description:** Returns a list of all tasks.
  - **Update Task**
    - **URL:** `/update_task`
    - **Method:** `POST`
    - **Description:** Updates an existing task.
    - **Request Body:** JSON object with the updated task data.

#### 2. Reminder Service
- **Description:** Provides reminders for upcoming tasks.
- **Endpoints:**
  - **Get Reminders**
    - **URL:** `/reminders`
    - **Method:** `GET`
    - **Description:** Returns tasks that are due within the next day.
  - **Mark Complete**
    - **URL:** `/mark_complete`
    - **Method:** `POST`
    - **Description:** Marks a task as complete.
    - **Request Body:** JSON object with the task ID.

#### 3. Task Filter Service
- **Description:** Filters tasks based on priority.
- **Endpoints:**
  - **Filter Tasks**
    - **URL:** `/filter_tasks`
    - **Method:** `GET`
    - **Description:** Returns tasks filtered by priority.
    - **Query Parameter:** `priority` (low, medium, high)

#### 4. Productivity Analysis Service
- **Description:** Analyzes productivity based on task completion.
- **Endpoints:**
  - **Productivity**
    - **URL:** `/productivity`
    - **Method:** `GET`
    - **Description:** Returns the productivity percentage based on completed tasks.

### Planned Microservices

#### 5. User Data Service
- **Description:** Manages user data, including authentication and user-specific task management.
- **Endpoints:**
  - **User Registration**
    - **URL:** `/register`
    - **Method:** `POST`
    - **Description:** Registers a new user.
    - **Request Body:** JSON object with user credentials.
  - **User Login**
    - **URL:** `/login`
    - **Method:** `POST`
    - **Description:** Authenticates a user and provides a token.
    - **Request Body:** JSON object with user credentials.
  - **User Profile**
    - **URL:** `/profile`
    - **Method:** `GET`
    - **Description:** Retrieves user profile information.
    - **Headers:** Authentication token.

## Inclusivity Heuristics Justification

•	How your design correctly reflects heuristic 1 (“Explain (to users) the benefits of using new and existing features”): 
•	How your design correctly reflects heuristic 2 (“Explain (to users) the costs of using new and existing features”): 
•	How your design correctly reflects heuristic 3 (“Let people gather as much information as they want, and no more than they want”): 
•	How your design correctly reflects heuristic 4 (“Keep familiar features available”):
•	How your design correctly reflects heuristic 5 (“Make undo/redo and backtracking available”):
•	How your design correctly reflects heuristic 6 (“Provide an explicit path through the task”): 
•	How your design correctly reflects heuristic 7 (“Provide ways to try out different approaches”):
•	How your design correctly reflects heuristic 8 (“Encourage tinkerers to tinker mindfully”): 


## Setup Instructions

### Prerequisites
- **Docker:** Ensure Docker is installed on your machine. You can download it from [here](https://www.docker.com/get-started).
- **Docker Compose:** Comes bundled with Docker Desktop.

### Steps

1. **Clone the Repository:**
    ```bash
    git clone https://github.com/yourusername/task-management-api.git
    cd task-management-api
    ```

2. **Build and Run the Services:**
    ```bash
    docker-compose up --build
    ```
    This command will build the Docker images and start all the services defined in the `docker-compose.yml` file.

3. **Access the Application:**
    - **Frontend Interface:** Open your browser and navigate to `http://localhost:8501` to access the Streamlit frontend.
    - **API Services:** Each service can be accessed via their respective ports as defined in the `docker-compose.yml`:
        - **Task Stats Service:** `http://localhost:5001`
        - **Reminder Service:** `http://localhost:5002`
        - **Task Filter Service:** `http://localhost:5003`
        - **Productivity Analysis Service:** `http://localhost:5004`

4. **Stopping the Services:**
    ```bash
    docker-compose down
    ```

### Troubleshooting
- **Port Conflicts:** Ensure that the ports `8501`, `5001`, `5002`, `5003`, and `5004` are not being used by other applications.
- **Docker Permissions:** If you encounter permission issues, ensure that your user has the necessary permissions to run Docker commands.

## Future Enhancements

- **Undo/Redo Functionality:** Implement undo and redo features to allow users to revert or reapply actions.
- **User Authentication:** Add user accounts to manage tasks across different users.
- **Enhanced UI/UX:** Improve the frontend interface with better designs and user interactions.
- **Notifications:** Implement email or push notifications for task reminders.
- **Database Integration:** Replace in-memory task storage with a persistent database like PostgreSQL or MongoDB.
- **User Data Service:** Fully implement the User Data Service to handle user registrations, logins, and profile management.

---

**Note:** This project adheres to Microsoft's content policies and ensures that all content respects copyright laws.