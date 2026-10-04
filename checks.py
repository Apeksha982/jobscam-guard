

import re

FREE_MAIL = {"gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "aol.com",
             "icloud.com", "proton.me", "protonmail.com"}
RISKY_TLDS = (".xyz", ".top", ".click", ".icu", ".shop", ".live", ".work", ".buzz")

# (name, regex, weight, why it matters)
PATTERNS = [
    ("Asks you to pay money",
     r"(registration|training|equipment|processing|application|background check|starter kit)\s+fee"
     r"|gift card|bitcoin|crypto|zelle|cash ?app|wire (me|the) (money|funds)",
     4, "Real employers do not charge you to get hired."),
    ("Check or equipment scheme",
     r"cashier'?s check|send you a check|deposit (the|this) check|purchase (your )?equipment",
     4, "Fake-check scams send a check, then ask you to send money back before it bounces."),
    ("Asks for sensitive info too early",
     r"\bssn\b|social security|bank account|routing number|passport|driver'?s license",
     3, "Legitimate employers collect these only after a formal offer, through official HR."),
    ("Moves chat to a private app",
     r"telegram|whatsapp|signal|text me at|hangouts",
     2, "Scammers avoid official channels so they cannot be traced or reported."),
    ("No interview / instant hire",
     r"no interview|hired immediately|instantly hired|start today",
     2, "Real hiring involves screening or interviews."),
    ("Pressure or too-good-to-be-true language",
     r"act now|limited (slots|spots)|urgent(ly)? hiring|no experience (needed|required)|guaranteed",
     1, "Urgency is used to stop you from verifying."),
]


def find_emails(text):
    return re.findall(r"[\w.+-]+@([\w-]+(?:\.[\w-]+)+)", text.lower())


def run_checks(text, company_domain=None):
    t = text.lower()
    flags = []

    for name, pattern, weight, why in PATTERNS:
        m = re.search(pattern, t)
        if m:
            flags.append({"name": name, "weight": weight, "evidence": m.group(0), "why": why})

    for domain in set(find_emails(t)):
        if domain in FREE_MAIL:
            flags.append({"name": "Free email used for recruiting", "weight": 2,
                          "evidence": domain,
                          "why": "Companies recruit from their own domain, not Gmail or Yahoo."})
        elif company_domain and domain != company_domain.lower():
            flags.append({"name": "Sender domain does not match company", "weight": 3,
                          "evidence": f"{domain} vs {company_domain}",
                          "why": "Check the company's real website and compare the domain exactly."})
        if domain.endswith(RISKY_TLDS):
            flags.append({"name": "Unusual domain ending", "weight": 1, "evidence": domain,
                          "why": "Cheap domain endings are common in throwaway scam sites."})

    score = sum(f["weight"] for f in flags)
    level = "HIGH" if score >= 6 else "MEDIUM" if score >= 3 else "LOW"
    return {"score": score, "level": level, "flags": flags}
