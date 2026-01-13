DANGEROUS_KEYWORDS = [

    # SQL Injection
    "select *",
    "union select",
    "or 1=1",
    "drop table",
    "delete from",
    "insert into",
    "update set",
    "--",
    ";--",

    # System / Command Injection
    "rm -rf",
    "shutdown",
    "reboot",
    "sudo",
    "chmod",
    "chown",
    "wget",
    "curl",
    "system(",
    "os.system",
    "subprocess",

    # Destructive commands
    "format disk",
    "mkfs",
    "dd if=",
    "kill -9",
    "erase all",

    # Prompt Injection (AI / Agents)
    "ignore previous instructions",
    "forget all rules",
    "system prompt",
    "developer mode",
    "reveal your instructions",
    "bypass security",
    "you are admin",

    # Code Injection
    "eval(",
    "exec(",
    "__import__",
    "<script>",
    "javascript:",

    # Recon / Network attacks
    "nmap",
    "port scan",
    "whoami",
    "ifconfig",
    "netstat",

    # Credential attacks
    "hashdump",
    "/etc/passwd",
    "dump credentials"
]

def is_request_safe(text: str) -> bool:
    text = text.lower()
    return not any(k in text for k in DANGEROUS_KEYWORDS)
