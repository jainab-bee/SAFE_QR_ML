from urllib.parse import urlparse


def extract_features(url):
    features = []
    features.append(len(url))                          # URL length
    features.append(url.count('.'))                    # Dot count
    features.append(1 if 'https' in url else 0)        # HTTPS check
    features.append(1 if '@' in url else 0)            # @ symbol check
    features.append(url.count('-'))                    # Hyphen count
    features.append(url.count('/'))                    # Slash count
    suspicious_words = ['login', 'verify', 'bank', 'secure', 'update']
    features.append(sum(word in url.lower() for word in suspicious_words))  # Suspicious words
    parsed_url = url
    if not parsed_url.startswith('http://') and not parsed_url.startswith('https://'):
        parsed_url = 'http://' + parsed_url
    domain = urlparse(parsed_url).netloc
    features.append(len(domain))                       # Domain length
    return features
