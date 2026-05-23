import re
from urllib.parse import urlparse
from config import SAFE_DOMAINS, BAD_TLDS, UPI_HANDLES


def get_root_domain(hostname):
    parts = hostname.split(".")
    if len(parts) >= 2:
        return ".".join(parts[-2:])
    return hostname


def is_upi(url):
    return url.lower().startswith("upi://")


def fix_url(text):
    text = text.strip()
    if text and not text.startswith(("http://", "https://", "ftp://", "upi://")):
        text = "https://" + text
    return text


def check_url_safety(url):
    results = []

    if is_upi(url):
        results.append({"name": "Protocol", "status": "pass", "detail": "UPI payment link (legitimate protocol)"})

        url_lower = url.lower()
        if any(handle in url_lower for handle in UPI_HANDLES):
            results.append({"name": "UPI Handle", "status": "pass", "detail": "Known trusted UPI handle"})
        else:
            results.append({"name": "UPI Handle", "status": "warn", "detail": "UPI handle not in known list"})

        if "pa=" in url:
            results.append({"name": "UPI Payee", "status": "pass", "detail": "Payee address present"})
        else:
            results.append({"name": "UPI Payee", "status": "fail", "detail": "Missing payee address (pa=)"})

        if "pn=" in url:
            results.append({"name": "UPI Payee Name", "status": "pass", "detail": "Payee name present"})
        else:
            results.append({"name": "UPI Payee Name", "status": "warn", "detail": "Payee name missing"})

        bad_words = ['login', 'verify', 'password', 'update', 'suspended', 'winner', 'free', 'claim']
        found = [w for w in bad_words if w in url_lower]
        if found:
            results.append({"name": "Suspicious Content", "status": "fail", "detail": f"Found: {', '.join(found)}"})
        else:
            results.append({"name": "Suspicious Content", "status": "pass", "detail": "No suspicious keywords"})

        if len(url) > 200:
            results.append({"name": "URL Length", "status": "warn", "detail": f"Long UPI URL ({len(url)} chars)"})
        else:
            results.append({"name": "URL Length", "status": "pass", "detail": f"Normal ({len(url)} chars)"})

        return results

    try:
        parsed = urlparse(url)
        hostname = parsed.hostname or ""
        scheme = parsed.scheme or ""
    except:
        return [{"name": "URL Parsing", "status": "fail", "detail": "Could not parse URL"}]

    domain = get_root_domain(hostname)

    if scheme == "https":
        results.append({"name": "HTTPS Encryption", "status": "pass", "detail": "Encrypted with HTTPS"})
    else:
        results.append({"name": "HTTPS Encryption", "status": "fail", "detail": f"Uses {scheme.upper() or 'NO PROTOCOL'}"})

    if domain in SAFE_DOMAINS:
        results.append({"name": "Domain Reputation", "status": "pass", "detail": f"'{domain}' is trusted"})
    else:
        results.append({"name": "Domain Reputation", "status": "warn", "detail": f"'{domain}' not in trusted list"})

    bad_tld_found = False
    for tld in BAD_TLDS:
        if hostname.endswith(tld):
            results.append({"name": "Domain Extension", "status": "fail", "detail": f"Suspicious TLD: {tld}"})
            bad_tld_found = True
            break
    if not bad_tld_found:
        results.append({"name": "Domain Extension", "status": "pass", "detail": "Normal extension"})

    if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", hostname):
        results.append({"name": "IP Address", "status": "fail", "detail": "Uses raw IP instead of domain"})
    else:
        results.append({"name": "IP Address", "status": "pass", "detail": "Uses proper domain name"})

    if "@" in url:
        results.append({"name": "@ Symbol", "status": "fail", "detail": "Contains @ — can redirect"})
    else:
        results.append({"name": "@ Symbol", "status": "pass", "detail": "No suspicious @ symbol"})

    bad_words = ['login', 'verify', 'bank', 'secure', 'update', 'account', 'password', 'free', 'winner', 'claim']
    found = [w for w in bad_words if w in url.lower()]
    if found:
        results.append({"name": "Phishing Keywords", "status": "fail", "detail": f"Found: {', '.join(found)}"})
    else:
        results.append({"name": "Phishing Keywords", "status": "pass", "detail": "None detected"})

    if len(url) > 100:
        results.append({"name": "URL Length", "status": "warn", "detail": f"Long URL ({len(url)} chars)"})
    else:
        results.append({"name": "URL Length", "status": "pass", "detail": f"Normal ({len(url)} chars)"})

    if hostname.count("-") > 2:
        results.append({"name": "Domain Hyphens", "status": "fail", "detail": f"{hostname.count('-')} hyphens"})
    else:
        results.append({"name": "Domain Hyphens", "status": "pass", "detail": "Normal"})

    return results
