"""
Shared URL feature extraction for the phishing detector.

This one file is used by BOTH the training notebook and the Django app,
so training and serving compute features identically.
Copy it unchanged to: app01_phish_detector/feature_extraction.py
"""
import math
import re
from collections import Counter
from urllib.parse import urlsplit, urlunsplit

import tldextract

FEATURE_VERSION = "2.0"

# Offline public-suffix list bundled with tldextract: no network calls, no cache files
# (cache_dir=None keeps it quiet in containers where the home dir is read-only)
_EXTRACT = tldextract.TLDExtract(suffix_list_urls=(), cache_dir=None)

_IPV4 = re.compile(r"^\d{1,3}(\.\d{1,3}){3}$")

# Order matters: the model is trained on exactly this column order.
FEATURE_NAMES = [
    "url_len", "dom_len", "is_ip", "tld_len", "subdom_cnt",
    "letter_cnt", "digit_cnt", "special_cnt",
    "eq_cnt", "qm_cnt", "amp_cnt", "dot_cnt", "dash_cnt", "under_cnt",
    "letter_ratio", "digit_ratio", "spec_ratio",
    "is_https", "slash_cnt", "entropy", "path_len", "query_len",
]

MAX_URL_LEN = 2048


def normalise_url(raw: str) -> str:
    """
    Canonical form used for training AND prediction:
      - strip whitespace
      - add http:// if no scheme
      - lowercase scheme and host
      - empty path becomes "/"  (so "https://x.com" == "https://x.com/")
    """
    url = (raw or "").strip()
    if not url:
        raise ValueError("Empty URL")
    if "://" not in url:
        url = "http://" + url
    parts = urlsplit(url)
    if not parts.netloc:
        raise ValueError(f"Could not find a host in URL: {raw!r}")
    path = parts.path or "/"
    return urlunsplit((parts.scheme.lower(), parts.netloc.lower(), path,
                       parts.query, parts.fragment))


def _shannon_entropy(s: str) -> float:
    n = len(s)
    if n == 0:
        return 0.0
    return -sum((c / n) * math.log2(c / n) for c in Counter(s).values())


def registered_domain(url: str) -> str:
    """e.g. https://www.rmit.edu.au/x -> rmit.edu.au (used for grouping in train/test split)."""
    host = urlsplit(normalise_url(url)).hostname or ""
    e = _EXTRACT(host)
    return f"{e.domain}.{e.suffix}" if e.suffix else (e.domain or host)


def extract_features(raw_url: str) -> dict:
    """Return a dict of numeric features, keys == FEATURE_NAMES."""
    url = normalise_url(raw_url)
    if len(url) > MAX_URL_LEN:
        raise ValueError(f"URL longer than {MAX_URL_LEN} characters")

    parts = urlsplit(url)
    host = parts.hostname or ""
    e = _EXTRACT(host)
    is_ip = int(bool(_IPV4.match(host)))
    if is_ip:
        dom, suffix, sub = host, "", ""
    else:
        dom = f"{e.domain}.{e.suffix}" if e.suffix else e.domain
        suffix, sub = e.suffix, e.subdomain

    n = len(url)
    letters = sum(ch.isalpha() for ch in url)
    digits = sum(ch.isdigit() for ch in url)
    special = n - letters - digits

    feats = {
        "url_len": n,
        "dom_len": len(dom),
        "is_ip": is_ip,
        "tld_len": len(suffix),
        "subdom_cnt": len(sub.split(".")) if sub else 0,
        "letter_cnt": letters,
        "digit_cnt": digits,
        "special_cnt": special,
        "eq_cnt": url.count("="),
        "qm_cnt": url.count("?"),
        "amp_cnt": url.count("&"),
        "dot_cnt": url.count("."),
        "dash_cnt": url.count("-"),
        "under_cnt": url.count("_"),
        "letter_ratio": letters / n,
        "digit_ratio": digits / n,
        "spec_ratio": special / n,
        "is_https": int(parts.scheme == "https"),
        "slash_cnt": url.count("/"),
        "entropy": _shannon_entropy(url),
        "path_len": len(parts.path),
        "query_len": len(parts.query),
    }
    return {k: feats[k] for k in FEATURE_NAMES}


def features_vector(raw_url: str) -> list:
    f = extract_features(raw_url)
    return [float(f[k]) for k in FEATURE_NAMES]