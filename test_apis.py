import time
import requests

BASE_URL = "http://localhost:8000"

def wait_for_server():
    print("Waiting for server to start at", BASE_URL)
    for _ in range(15):
        try:
            res = requests.get(f"{BASE_URL}/")
            if res.status_code == 200:
                print("Server is up!")
                return True
        except requests.ConnectionError:
            time.sleep(1)
    print("Server did not start in time. Make sure it is running!")
    return False

def run_tests():
    if not wait_for_server():
        return

    print("\n=== STARTING API TESTS (SKIPPING AWS) ===")

    print("\n[TEST: POST /api/deploy (GitHub)]")
    res = requests.post(f"{BASE_URL}/api/deploy", json={"target": "test-backend", "ref": "main"})
    print("Status:", res.status_code, "=>", res.json())

    print("\n[TEST: POST /api/users (Snowflake Create)]")
    res = requests.post(f"{BASE_URL}/api/users", json={"username": "DEVFLOW_TEST_USER_XYZ", "role": "ANALYST"})
    print("Status:", res.status_code, "=>", res.json())

    print("\n[TEST: GET /api/users (Snowflake List)]")
    res = requests.get(f"{BASE_URL}/api/users")
    print("Status:", res.status_code, "=> Returned users count:", len(res.json().get('users', [])))

    print("\n[TEST: POST /api/users/reset (Snowflake Reset)]")
    res = requests.post(f"{BASE_URL}/api/users/reset", json={"username": "DEVFLOW_TEST_USER_XYZ"})
    print("Status:", res.status_code, "=>", res.json())

    print("\n=== STARTING SLACK COMMAND TESTS ===")
    
    # Simulate Slack payload (form data)
    print("\n[TEST: SLACK /slack/commands 'deploy backend']")
    payload1 = {"text": "deploy backend", "user_name": "tester", "command": "/devflow"}
    res = requests.post(f"{BASE_URL}/slack/commands", data=payload1)
    print("Status:", res.status_code, "=>", res.json())

    print("\n[TEST: SLACK /slack/commands 'create_user slack_jane ENGINEER']")
    payload2 = {"text": "create_user slack_jane ENGINEER", "user_name": "tester", "command": "/devflow"}
    res = requests.post(f"{BASE_URL}/slack/commands", data=payload2)
    print("Status:", res.status_code, "=>", res.json())

    print("\n[TEST: SLACK /slack/commands 'reset_password slack_jane']")
    payload3 = {"text": "reset_password slack_jane", "user_name": "tester", "command": "/devflow"}
    res = requests.post(f"{BASE_URL}/slack/commands", data=payload3)
    print("Status:", res.status_code, "=>", res.json())

    print("\n=== CHECKING LOGS ===")
    print("\n[TEST: GET /api/logs (Validate all actions were recorded)]")
    res = requests.get(f"{BASE_URL}/api/logs")
    logs = res.json()
    print("Status:", res.status_code, "=> Recorded Actions:", len(logs))
    for log in logs[:5]:  # Display last 5
        print(f" - [{log['source'].upper()}] {log['action']} ({log['status']})")

if __name__ == "__main__":
    run_tests()
