"""
Feature extraction module for phishing URL detection.
Extracts ALL features from a URL to match the training dataset columns.

Dataset: https://data.mendeley.com/datasets/6tm2d6sz7p/1
Published: 7 June 2023 (0=legitimate, 1=phishing)

IMPORTANT: This function returns a dictionary with every possible feature name
from the dataset. If feature_names.pkl contains a key not listed here, you will
get a KeyError. To debug, compare feature_names.pkl with the keys this function
returns and add any missing features.
"""

import math
import re
from urllib.parse import urlparse
from collections import Counter


def _entropy(text):
    """Calculate Shannon entropy of a string."""
    if not text:
        return 0.0
    counter = Counter(text)
    length = len(text)
    entropy = -sum((count / length) * math.log2(count / length) for count in counter.values())
    return entropy


def _count_char(text, char):
    """Count occurrences of a character in text."""
    return text.count(char)


def _has_repeated_digits(text):
    """Check if the text contains consecutive repeated digits (e.g., 11, 22, 333)."""
    if not text:
        return 0
    for i in range(len(text) - 1):
        if text[i].isdigit() and text[i] == text[i + 1]:
            return 1
    return 0


def _count_digits(text):
    """Count the number of digits in text."""
    return sum(1 for c in text if c.isdigit())


def _has_digits(text):
    """Check if text contains any digits."""
    return 1 if any(c.isdigit() for c in text) else 0


def _count_special_chars(text):
    """Count special characters (non-alphanumeric, excluding dots)."""
    return sum(1 for c in text if not c.isalnum() and c != '.')


def _get_subdomains(parsed_url):
    """Extract subdomains from the hostname."""
    hostname = parsed_url.hostname or ''
    parts = hostname.split('.')
    # If we have domain.tld, there are no subdomains
    # If we have sub.domain.tld, 'sub' is the subdomain
    if len(parts) <= 2:
        return []
    return parts[:-2]  # Everything except the main domain and TLD


def extract_features(url):
    """
    Extract all features from a URL.
    Returns a dictionary with feature names as keys.

    The features match the columns in Dataset.csv (excluding the 'Type' column).
    """

    # Parse the URL
    parsed = urlparse(url if '://' in url else 'http://' + url)

    hostname = parsed.hostname or ''
    path = parsed.path or ''
    query = parsed.query or ''
    fragment = parsed.fragment or ''
    full_url = url

    # Extract domain (hostname without subdomains)
    hostname_parts = hostname.split('.')
    if len(hostname_parts) >= 2:
        domain = '.'.join(hostname_parts[-2:])  # e.g., example.com
    else:
        domain = hostname

    # Extract subdomains
    subdomains = _get_subdomains(parsed)
    number_of_subdomains = len(subdomains)

    # Subdomain-level statistics
    subdomain_lengths = [len(s) for s in subdomains] if subdomains else [0]
    subdomain_dots = [s.count('.') for s in subdomains] if subdomains else [0]
    subdomain_hyphens = [s.count('-') for s in subdomains] if subdomains else [0]
    full_subdomain = '.'.join(subdomains) if subdomains else ''

    # ========================
    # EXTRACT ALL FEATURES
    # ========================

    features = {}

    # --- URL-level features ---
    features['url_length'] = len(full_url)
    features['number_of_dots_in_url'] = _count_char(full_url, '.')
    features['having_repeated_digits_in_url'] = _has_repeated_digits(full_url)
    features['number_of_digits_in_url'] = _count_digits(full_url)
    features['number_of_special_char_in_url'] = sum(1 for c in full_url if not c.isalnum() and c not in './-:_?=&#@')
    features['number_of_hyphens_in_url'] = _count_char(full_url, '-')
    features['number_of_underline_in_url'] = _count_char(full_url, '_')
    features['number_of_slash_in_url'] = _count_char(full_url, '/')
    features['number_of_questionmark_in_url'] = _count_char(full_url, '?')
    features['number_of_equal_in_url'] = _count_char(full_url, '=')
    features['number_of_at_in_url'] = _count_char(full_url, '@')
    features['number_of_dollar_in_url'] = _count_char(full_url, '$')
    features['number_of_exclamation_in_url'] = _count_char(full_url, '!')
    features['number_of_hashtag_in_url'] = _count_char(full_url, '#')
    features['number_of_percent_in_url'] = _count_char(full_url, '%')

    # --- Domain-level features ---
    features['domain_length'] = len(domain)
    features['number_of_dots_in_domain'] = _count_char(domain, '.')
    features['number_of_digits_in_domain'] = _count_digits(domain)
    features['having_digits_in_domain'] = _has_digits(domain)
    features['having_repeated_digits_in_domain'] = _has_repeated_digits(domain)
    features['number_of_hyphens_in_domain'] = _count_char(domain, '-')
    features['number_of_special_characters_in_domain'] = _count_special_chars(domain)
    features['having_special_characters_in_domain'] = 1 if _count_special_chars(domain) > 0 else 0

    # --- Subdomain-level features ---
    features['number_of_subdomains'] = number_of_subdomains
    features['having_dot_in_subdomain'] = 1 if '.' in full_subdomain else 0
    features['having_hyphen_in_subdomain'] = 1 if '-' in full_subdomain else 0
    features['average_subdomain_length'] = sum(subdomain_lengths) / len(subdomain_lengths) if subdomain_lengths else 0
    features['average_number_of_dots_in_subdomain'] = sum(subdomain_dots) / len(subdomain_dots) if subdomain_dots else 0
    features['average_number_of_hyphens_in_subdomain'] = sum(subdomain_hyphens) / len(subdomain_hyphens) if subdomain_hyphens else 0
    features['having_special_characters_in_subdomain'] = 1 if any(not c.isalnum() and c not in '.-' for c in full_subdomain) else 0
    features['number_of_special_characters_in_subdomain'] = sum(1 for c in full_subdomain if not c.isalnum() and c not in '.-')

    # --- Subdomain digits features ---
    features['number_of_digits_in_subdomain'] = _count_digits(full_subdomain)
    features['having_digits_in_subdomain'] = _has_digits(full_subdomain)
    features['having_repeated_digits_in_subdomain'] = _has_repeated_digits(full_subdomain)

    # --- Path, query, fragment, anchor features ---
    features['having_path'] = 1 if path and path != '/' else 0
    features['path_length'] = len(path)
    features['having_query'] = 1 if query else 0
    features['having_fragment'] = 1 if fragment else 0
    features['having_anchor'] = 1 if '#' in full_url else 0

    # --- Entropy features ---
    features['entropy_of_url'] = _entropy(full_url)
    features['entropy_of_domain'] = _entropy(domain)

    # --- Hostname-level features (in case dataset uses hostname instead of domain) ---
    features['hostname_length'] = len(hostname)
    features['number_of_dots_in_hostname'] = _count_char(hostname, '.')
    features['number_of_hyphens_in_hostname'] = _count_char(hostname, '-')

    return features