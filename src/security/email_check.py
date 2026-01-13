import re

PHISHING_PATTERNS = [

    # Microsoft spoofing
    r"micr0soft",
    r"m1crosoft",
    r"rnicrosoft",
    r"micros0ft",
    r"microsoflt",
    r"micro-soft",

    # Google spoofing
    r"go0gle",
    r"g00gle",
    r"goog1e",
    r"goggle-security",

    # Apple spoofing
    r"app1e",
    r"appl3",
    r"appleid-secure",
    r"icloud-verify",

    # PayPal spoofing
    r"paypaI",
    r"paypai",
    r"paypall",
    r"paypal-secure",
    r"paypal-verification",

    # Amazon spoofing
    r"amaz0n",
    r"arnazon",
    r"amazon-security",
    r"amazon-support",

    # Meta / Facebook spoofing
    r"faceb00k",
    r"facbook",
    r"meta-security",
    r"facebook-verify",

    # Netflix spoofing
    r"netfIix",
    r"netflix-billing",
    r"netflix-support",

    # Instagram spoofing
    r"instagrarn",
    r"insta-verify",
    r"instagram-security",

    # LinkedIn spoofing
    r"linkedln",
    r"linkdin",
    r"linkedin-security",

    # Generic phishing words
    r"verify-account",
    r"secure-login",
    r"account-alert",
    r"billing-update",
    r"urgent-action",
    r"suspended-account",
]


def is_email_safe(email: str) -> bool:
    # format simple
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return False

    for pattern in PHISHING_PATTERNS:
        if re.search(pattern, email, re.IGNORECASE):
            return False

    return True
