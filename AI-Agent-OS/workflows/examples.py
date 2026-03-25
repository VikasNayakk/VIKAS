"""
Example workflows for AI-Agent-OS

These are high-level task definitions that can be executed
"""

# Example 1: Send message to contact
SEND_MESSAGE_WORKFLOW = {
    "name": "send_message",
    "description": "Send message to contact",
    "steps": [
        {"action": "open_app", "target": "teams"},
        {"action": "wait", "duration": 2},
        {"action": "screenshot"},
        {"action": "find_contact", "name": "himanshu"},
        {"action": "click", "target": "contact"},
        {"action": "type", "text": "hello"},
        {"action": "send_message"}
    ]
}

# Example 2: Search on browser
SEARCH_WORKFLOW = {
    "name": "web_search",
    "description": "Search on browser",
    "steps": [
        {"action": "open_app", "target": "chrome"},
        {"action": "wait", "duration": 2},
        {"action": "click", "target": "search_bar"},
        {"action": "type", "text": "python tutorial"},
        {"action": "press_key", "key": "enter"},
        {"action": "wait", "duration": 1},
        {"action": "screenshot"}
    ]
}

# Example 3: Create file
CREATE_FILE_WORKFLOW = {
    "name": "create_file",
    "description": "Create new file",
    "steps": [
        {"action": "open_app", "target": "notepad"},
        {"action": "wait", "duration": 1},
        {"action": "type", "text": "hello world"},
        {"action": "save_file", "filename": "test.txt"}
    ]
}
