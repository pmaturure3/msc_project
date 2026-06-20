import math
import re
from urllib.parse import urlparse
from collections import Counter

def _entropy(text):
    if not text:
        return 0.0
    counter = Counter(text)
    length = len(text)
    entropy = -sum((count / length) * math.log2(count / length) for count in counter.values())
    return entropy

def _is_ip_address(hostname):
    if not hostname:
        return 0
    pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    if re.match(pattern, hostname):
        parts = hostname.split('.')
        return 1 if all(0 <= int(p) <= 255 for p in parts) else 0
    return 0

def _get_tld(hostname):
    if not hostname:
        return ''
    parts = hostname.split('.')
    if len(parts) >= 3 and parts[-2] in ['co', 'com', 'org', 'net', 'gov', 'edu', 'ac']:
        return '.'.join(parts[-2:])
    return parts[-1] if parts else ''

def _get_domain(hostname):
    if not hostname:
        return ''
    parts = hostname.split('.')
    if len(parts) <= 2:
        return parts[-2] if len(parts) >= 2 else parts[0]
    if len(parts) >= 3 and parts[-2] in ['co', 'com', 'org', 'net', 'gov', 'edu', 'ac']:
        return parts[-3]
    return parts[-2]

def _get_subdomains(hostname):
    if not hostname:
        return []
    parts = hostname.split('.')
    if len(parts) <= 2:
        return []
    if len(parts) >= 3 and parts[-2] in ['co', 'com', 'org', 'net', 'gov', 'edu', 'ac']:
        return parts[:-2]
    return parts[:-1]

def extract_features(url):
    parsed = urlparse(url if '://' in url else 'http://' + url)
    hostname = parsed.hostname or ''
    path = parsed.path or ''
    query = parsed.query or ''
    full_url = url
    scheme = parsed.scheme

    tld = _get_tld(hostname)
    domain = _get_domain(hostname)
    subdomains = _get_subdomains(hostname)
    subdom_cnt = len(subdomains)

    letter_cnt = sum(c.isalpha() for c in full_url)
    digit_cnt = sum(c.isdigit() for c in full_url)
    special_chars = '!@#$%^&*()_+={}[]|\\:;"\'<>,.?/~`'
    special_cnt = sum(1 for c in full_url if c in special_chars)

    url_length = len(full_url)
    letter_ratio = letter_cnt / url_length if url_length > 0 else 0
    digit_ratio = digit_cnt / url_length if url_length > 0 else 0
    spec_ratio = special_cnt / url_length if url_length > 0 else 0

    features = {
        'url_len': url_length,
        'dom': domain,
        'dom_len': len(domain),
        'is_ip': _is_ip_address(hostname),
        'tld': tld,
        'tld_len': len(tld),
        'subdom_cnt': subdom_cnt,
        'letter_cnt': letter_cnt,
        'digit_cnt': digit_cnt,
        'special_cnt': special_cnt,
        'eq_cnt': full_url.count('='),
        'qm_cnt': full_url.count('?'),
        'amp_cnt': full_url.count('&'),
        'dot_cnt': full_url.count('.'),
        'dash_cnt': full_url.count('-'),
        'under_cnt': full_url.count('_'),
        'letter_ratio': letter_ratio,
        'digit_ratio': digit_ratio,
        'spec_ratio': spec_ratio,
        'is_https': 1 if scheme == 'https' else 0,
        'slash_cnt': full_url.count('/'),
        'entropy': _entropy(full_url),
        'path_len': len(path),
        'query_len': len(query),
    }

    return features