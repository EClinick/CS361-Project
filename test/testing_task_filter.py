"""
Task Filter Service Test Suite

This test suite validates the Task Filter microservice which handles:
1. Filtering tasks by various criteria (priority, completion status, due date)
2. Saving and managing filter preferences
3. Retrieving and clearing saved preferences

Microservice Endpoints Tested:
-----------------------------
Task Filter Service (http://localhost:5003):
    - GET /filter_tasks: Filters tasks based on query parameters
        - priority: 'low', 'medium', 'high'
        - completed: 'true', 'false'
        - due_date: 'YYYY-MM-DD'
    
    - POST /save_filter_preferences: Saves user's filter preferences
        - Accepts JSON body with filter criteria
        - Stores in filter_preferences.json
    
    - GET /get_saved_preferences: Retrieves saved filter preferences
        - Returns current saved preferences from filter_preferences.json
    
    - POST /clear_preferences: Clears all saved filter preferences
        - Resets filter_preferences.json to empty state

Task Stats Service (http://localhost:5001):
    - POST /add_task: Creates new tasks (used for test data)
    - GET /view_tasks: Retrieves all tasks
    - POST /delete_task: Removes tasks (used in cleanup)
"""

import requests
import json
import sys
import os
from datetime import datetime, timedelta
from colorama import init, Fore, Style

# Add parent directory to Python path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Initialize colorama for Windows compatibility
init()

# Base URLs for services
BASE_URL = "http://localhost:5003"
TASK_STATS_URL = "http://localhost:5001"

def validate_services():
    """
    Validates that required microservices are running and accessible.
    
    Tests connections to:
    - Task Filter service: Main service being tested
    - Task Stats service: Required for test data management
    """
    print(f"\n{Fore.CYAN}=== Validating Services ==={Style.RESET_ALL}")
    services = {
        "Task Filter": {"url": BASE_URL, "endpoint": "/filter_tasks"},
        "Task Stats": {"url": TASK_STATS_URL, "endpoint": "/view_tasks"}
    }
    
    all_services_up = True
    for name, service in services.items():
        try:
            response = requests.get(f"{service['url']}{service['endpoint']}")
            if response.ok:
                print(f"{Fore.GREEN}✓ {name} service is accessible{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}✗ {name} service returned error: {response.status_code}{Style.RESET_ALL}")
                all_services_up = False
        except requests.exceptions.ConnectionError:
            print(f"{Fore.RED}✗ Cannot connect to {name} service at {service['url']}{Style.RESET_ALL}")
            all_services_up = False
    return all_services_up

def setup_test_data():
    """
    Creates test data in Task Stats service for testing filters.
    
    Creates:
    - 1 completed high priority task
    - 1 pending high priority task
    - 1 pending low priority task
    
    Uses Task Stats service endpoint:
    - POST /add_task
    """
    print(f"\n{Fore.CYAN}=== Setting Up Test Data ==={Style.RESET_ALL}")
    test_tasks = [
        {
            "id": "test1",
            "title": "High Priority Complete",
            "description": "Test task 1",
            "priority": "high",
            "completed": True,
            "due_date": datetime.now().strftime("%Y-%m-%d"),
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        },
        {
            "id": "test2",
            "title": "High Priority Pending",
            "description": "Test task 2",
            "priority": "high",
            "completed": False,
            "due_date": datetime.now().strftime("%Y-%m-%d"),
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        },
        {
            "id": "test3",
            "title": "Low Priority Pending",
            "description": "Test task 3",
            "priority": "low",
            "completed": False,
            "due_date": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    ]
    
    success = True
    for task in test_tasks:
        response = requests.post(f"{TASK_STATS_URL}/add_task", json=task)
        if response.ok:
            print(f"{Fore.GREEN}✓ Added test task: {task['title']}{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}✗ Failed to add test task: {task['title']}{Style.RESET_ALL}")
            success = False
    return success

def print_test_result(passed: bool, test_name: str):
    """Helper function to print test results"""
    if passed:
        print(f"{Fore.GREEN}[PASS] {test_name}{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}[FAIL] {test_name}{Style.RESET_ALL}")

def test_filter_tasks():
    """
    Tests the task filtering functionality of the Task Filter service.
    
    Test Cases:
    1. Priority Filter:
       - Endpoint: GET /filter_tasks?priority=high
       - Expected: Returns only high priority tasks
       
    2. Completion Status:
       - Endpoint: GET /filter_tasks?completed=true
       - Expected: Returns only completed tasks
       
    3. Due Date Filter:
       - Endpoint: GET /filter_tasks?due_date=YYYY-MM-DD
       - Expected: Returns tasks due on specific date
    """
    print(f"\n{Fore.CYAN}=== Testing Filter Tasks Endpoint ==={Style.RESET_ALL}")
    all_tests_passed = True
    
    # Test 1: Filter by priority (high)
    print(f"\n{Fore.YELLOW}Test 1: Filter by priority (high){Style.RESET_ALL}")
    response = requests.get(f"{BASE_URL}/filter_tasks", params={"priority": "high"})
    if response.ok:
        tasks = response.json().get("filtered_tasks", [])
        expected_count = 2  # We expect 2 high priority tasks
        count_matches = len(tasks) == expected_count
        all_high = all(task['priority'] == 'high' for task in tasks)
        test_passed = count_matches and all_high
        
        print(f"Found {len(tasks)} high priority tasks (Expected: {expected_count})")
        print(f"All tasks have high priority: {all_high}")
        print_test_result(test_passed, "Priority Filter Test")
        all_tests_passed = all_tests_passed and test_passed
    
    # Test 2: Filter by completion status
    print(f"\n{Fore.YELLOW}Test 2: Filter completed tasks{Style.RESET_ALL}")
    response = requests.get(f"{BASE_URL}/filter_tasks", params={"completed": "true"})
    if response.ok:
        tasks = response.json().get("filtered_tasks", [])
        expected_count = 1  # We expect 1 completed task
        count_matches = len(tasks) == expected_count
        all_completed = all(task['completed'] for task in tasks)
        test_passed = count_matches and all_completed
        
        print(f"Found {len(tasks)} completed tasks (Expected: {expected_count})")
        print(f"All tasks are completed: {all_completed}")
        print_test_result(test_passed, "Completion Status Filter Test")
        all_tests_passed = all_tests_passed and test_passed
    
    # Test 3: Filter by due date
    today = datetime.now().strftime("%Y-%m-%d")
    print(f"\n{Fore.YELLOW}Test 3: Filter by due date (today: {today}){Style.RESET_ALL}")
    response = requests.get(f"{BASE_URL}/filter_tasks", params={"due_date": today})
    if response.ok:
        tasks = response.json().get("filtered_tasks", [])
        expected_count = 2  # We expect 2 tasks due today
        count_matches = len(tasks) == expected_count
        all_today = all(task['due_date'] == today for task in tasks)
        test_passed = count_matches and all_today
        
        print(f"Found {len(tasks)} tasks due today (Expected: {expected_count})")
        print(f"All tasks are due today: {all_today}")
        print_test_result(test_passed, "Due Date Filter Test")
        all_tests_passed = all_tests_passed and test_passed
    
    return all_tests_passed

def test_preferences():
    """
    Tests the preference management functionality.
    
    Test Cases:
    1. Save Preferences:
       - Endpoint: POST /save_filter_preferences
       - Payload: JSON with filter criteria
       - Expected: Successfully saves preferences to file
       
    2. Get Preferences:
       - Endpoint: GET /get_saved_preferences
       - Expected: Returns previously saved preferences
       
    3. Clear Preferences:
       - Endpoint: POST /clear_preferences
       - Expected: Removes all saved preferences
    """
    print(f"\n{Fore.CYAN}=== Testing Preferences Endpoints ==={Style.RESET_ALL}")
    all_tests_passed = True
    
    # Test 1: Save preferences
    print(f"\n{Fore.YELLOW}Test 1: Save preferences{Style.RESET_ALL}")
    test_preferences = {
        "priority": "high",
        "due_date": datetime.now().strftime("%Y-%m-%d"),
        "completed": "pending"
    }
    save_response = requests.post(f"{BASE_URL}/save_filter_preferences", json=test_preferences)
    save_success = save_response.ok and save_response.json().get("message") == "Filter preferences saved successfully"
    print(f"Attempted to save preferences: {test_preferences}")
    print_test_result(save_success, "Save Preferences Test")
    all_tests_passed = all_tests_passed and save_success
    
    # Test 2: Get saved preferences
    print(f"\n{Fore.YELLOW}Test 2: Get saved preferences{Style.RESET_ALL}")
    get_response = requests.get(f"{BASE_URL}/get_saved_preferences")
    if get_response.ok:
        saved_prefs = get_response.json().get("saved_preferences", [])
        has_prefs = len(saved_prefs) == 1 and saved_prefs[0].get("priority") == test_preferences["priority"]
        print(f"Retrieved preferences: {json.dumps(saved_prefs, indent=2)}")
        print_test_result(has_prefs, "Get Preferences Test")
        all_tests_passed = all_tests_passed and has_prefs
    
    # Test 3: Clear preferences
    print(f"\n{Fore.YELLOW}Test 3: Clear preferences{Style.RESET_ALL}")
    clear_response = requests.post(f"{BASE_URL}/clear_preferences")
    if clear_response.ok:
        verify_response = requests.get(f"{BASE_URL}/get_saved_preferences")
        if verify_response.ok:
            is_empty = len(verify_response.json().get("saved_preferences", [])) == 0
            print(f"Preferences after clearing: {verify_response.json()}")
            print_test_result(is_empty, "Clear Preferences Test")
            all_tests_passed = all_tests_passed and is_empty
    
    return all_tests_passed

def cleanup_test_data():
    """
    Removes all test data from Task Stats service.
    
    Uses Task Stats service endpoints:
    - GET /view_tasks: To find test tasks
    - POST /delete_task: To remove each test task
    """
    print(f"\n{Fore.CYAN}=== Cleaning Up Test Data ==={Style.RESET_ALL}")
    success = True
    response = requests.get(f"{TASK_STATS_URL}/view_tasks")
    if response.ok:
        tasks = response.json()["tasks"]
        for task in tasks:
            if task["id"].startswith("test"):
                delete_response = requests.post(f"{TASK_STATS_URL}/delete_task", 
                                             json={"id": task["id"]})
                if delete_response.ok:
                    print(f"{Fore.GREEN}✓ Removed test task: {task['title']}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}✗ Failed to remove test task: {task['title']}{Style.RESET_ALL}")
                    success = False
    return success

def display_documentation():
    """Displays documentation about the microservices and endpoints being tested"""
    print(f"\n{Fore.CYAN}=== Task Filter Service Test Documentation ==={Style.RESET_ALL}")
    print(f"\n{Fore.YELLOW}Microservices Tested:{Style.RESET_ALL}")
    
    # Task Filter Service Documentation
    print(f"\n{Fore.GREEN}1. Task Filter Service (http://localhost:5003){Style.RESET_ALL}")
    print("   Endpoints tested:")
    print("   └── GET /filter_tasks")
    print("       ├── Filters tasks based on query parameters")
    print("       ├── Parameters:")
    print("       │   ├── priority: 'low', 'medium', 'high'")
    print("       │   ├── completed: 'true', 'false'")
    print("       │   └── due_date: 'YYYY-MM-DD'")
    print("       └── Returns filtered list of tasks")
    
    print("\n   └── POST /save_filter_preferences")
    print("       ├── Saves user's filter preferences")
    print("       ├── Accepts JSON body with filter criteria")
    print("       └── Stores in filter_preferences.json")
    
    print("\n   └── GET /get_saved_preferences")
    print("       ├── Retrieves saved filter preferences")
    print("       └── Returns current saved preferences")
    
    print("\n   └── POST /clear_preferences")
    print("       ├── Clears all saved filter preferences")
    print("       └── Resets filter_preferences.json to empty state")
    
    # Task Stats Service Documentation
    print(f"\n{Fore.GREEN}2. Task Stats Service (http://localhost:5001){Style.RESET_ALL}")
    print("   Endpoints used:")
    print("   └── POST /add_task")
    print("       └── Creates new tasks (used for test data)")
    
    print("\n   └── GET /view_tasks")
    print("       └── Retrieves all tasks")
    
    print("\n   └── POST /delete_task")
    print("       └── Removes tasks (used in cleanup)")
    
    print(f"\n{Fore.YELLOW}Test Data:{Style.RESET_ALL}")
    print("The test suite creates the following test tasks:")
    print("1. High Priority Complete task (due today)")
    print("2. High Priority Pending task (due today)")
    print("3. Low Priority Pending task (due tomorrow)")
    
    print(f"\n{Fore.YELLOW}Test Flow:{Style.RESET_ALL}")
    print("1. Validates service accessibility")
    print("2. Sets up test data")
    print("3. Tests filter functionality")
    print("4. Tests preference management")
    print("5. Cleans up test data")
    
    print("\n" + "="*50 + "\n")

def run_all_tests():
    print(f"{Fore.CYAN}Starting Task Filter Service Tests{Style.RESET_ALL}")
    print(f"{Fore.CYAN}=================================={Style.RESET_ALL}")
    
    # Display documentation at the start
    display_documentation()
    
    try:
        if not validate_services():
            print_test_result(False, "Service Validation")
            return
        
        setup_success = setup_test_data()
        if not setup_success:
            print_test_result(False, "Test Setup")
            return
            
        filter_tests_passed = test_filter_tasks()
        preferences_tests_passed = test_preferences()
        cleanup_success = cleanup_test_data()
        
        all_passed = filter_tests_passed and preferences_tests_passed and cleanup_success
        print(f"\n{Fore.CYAN}=== Final Test Results ==={Style.RESET_ALL}")
        print_test_result(filter_tests_passed, "Filter Tests")
        print_test_result(preferences_tests_passed, "Preferences Tests")
        print_test_result(cleanup_success, "Cleanup")
        print_test_result(all_passed, "Overall Test Suite")
            
    except requests.exceptions.ConnectionError:
        print(f"\n{Fore.RED}✗ Error: Could not connect to the task_filter service.{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Make sure the service is running on http://localhost:5003{Style.RESET_ALL}")
        print_test_result(False, "Connection Test")
    except Exception as e:
        print(f"\n{Fore.RED}✗ Error during testing: {str(e)}{Style.RESET_ALL}")
        print_test_result(False, "Test Execution")
    finally:
        try:
            cleanup_test_data()
        except:
            print_test_result(False, "Final Cleanup")

if __name__ == "__main__":
    run_all_tests() 