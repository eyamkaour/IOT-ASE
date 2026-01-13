POLICY = {
    "classifier": {
        "use": {"guest", "user", "admin"}
    },
    "agent": {
        "use": {"user", "admin"}
    },
    "admin_panel": {
        "use": {"admin"}
    }
}

def is_allowed(roles, resource, action):
    allowed = POLICY.get(resource, {}).get(action, set())
    return any(role in allowed for role in roles)
