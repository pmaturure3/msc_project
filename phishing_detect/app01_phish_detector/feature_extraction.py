import re
from urllib.parse import urlparse
import math

def extract_features(url):

    features = []

    # 1 Having anchor
    features.append(1 if "<a>" in url else 0)

    # 2 Entropy
    prob = [float(url.count(c)) / len(url) for c in dict.fromkeys(list(url))]
    entropy = - sum([p * math.log(p) / math.log(2.0) for p in prob])
    features.append(entropy)

    # 3 Hyphen in subdomain
    features.append(1 if "-" in urlparse(url).netloc else 0)

    # 4 Number of %
    features.append(url.count('%'))

    # 5 Repeated digits in domain
    features.append(1 if re.search(r'(\d)\1', urlparse(url).netloc) else 0)

    # 6 Number of digits in URL
    features.append(sum(c.isdigit() for c in url))

    # 7 Repeated digits in URL
    features.append(1 if re.search(r'(\d)\1', url) else 0)

    # 8 Domain length
    features.append(len(urlparse(url).netloc))

    # 9 Digits in domain
    features.append(1 if any(c.isdigit() for c in urlparse(url).netloc) else 0)

    # 10 URL length
    features.append(len(url))

    # 11 Underline count
    features.append(url.count('_'))

    # 12 Having path
    features.append(1 if urlparse(url).path else 0)

    # 13 Number of dots in domain
    features.append(urlparse(url).netloc.count('.'))

    return features