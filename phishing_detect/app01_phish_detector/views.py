import logging
import os

import joblib
import numpy as np
from django.conf import settings
from django.shortcuts import render

from .feature_extraction import (
    FEATURE_NAMES,
    FEATURE_VERSION,
    features_vector,
    normalise_url,
)
from .models import URLCheck

logger = logging.getLogger(__name__)

MODEL_PATH = os.path.join(
    settings.BASE_DIR, 'app01_phish_detector', 'trained_models', 'phishing_model.pkl'
)
TEMPLATE_RESULT = 'app01_phish_detector/result.html'


def _load_bundle(path):
    """Load the bundle saved by the notebook and refuse to start if it doesn't match this code."""
    bundle = joblib.load(path)
    if not isinstance(bundle, dict) or 'model' not in bundle:
        raise RuntimeError(
            f"{path} is not a deployment bundle. Re-run the notebook and copy "
            "deploy/app01_phish_detector/trained_models/phishing_model.pkl here "
            "(models from the old notebook are not compatible)."
        )
    if bundle['feature_version'] != FEATURE_VERSION:
        raise RuntimeError(
            f"Model was trained with feature_extraction v{bundle['feature_version']}, "
            f"app has v{FEATURE_VERSION}. Copy the same feature_extraction.py used in training."
        )
    if list(bundle['feature_names']) != list(FEATURE_NAMES):
        raise RuntimeError("Feature names/order differ between the model and feature_extraction.py.")
    return bundle


BUNDLE = _load_bundle(MODEL_PATH)
MODEL = BUNDLE['model']
MODEL_NAME = BUNDLE['model_name']
# Threshold chosen on the validation set in the notebook; override in settings.py if needed.
THRESHOLD = float(getattr(settings, 'PHISHING_THRESHOLD', BUNDLE['threshold']))

logger.info("Loaded phishing model %s (threshold %.3f, features v%s)",
            MODEL_NAME, THRESHOLD, FEATURE_VERSION)


def index(request):
    return render(request, 'app01_phish_detector/index.html', {'page_title': 'Home'})


METRIC_LABELS = [
    ('Phish precision', 'Precision (phishing)', 'Of the URLs flagged as phishing, the share that really were phishing.'),
    ('Phish recall', 'Recall (phishing)', 'Of the real phishing URLs, the share the model caught.'),
    ('Phish F1', 'F1-score (phishing)', 'Balance of precision and recall for the phishing class.'),
    ('MCC', 'Matthews correlation', 'Overall quality on imbalanced data (1 = perfect, 0 = random).'),
    ('PR-AUC', 'PR-AUC', 'Ranking quality across all thresholds, focused on phishing.'),
    ('Balanced acc', 'Balanced accuracy', 'Average of the accuracy on each class.'),
    ('Accuracy', 'Accuracy', 'Share of all URLs classified correctly (inflated by class imbalance).'),
]


def about(request):
    test_metrics = BUNDLE.get('test_metrics', {}) or {}
    metrics = []
    for key, label, help_text in METRIC_LABELS:
        value = test_metrics.get(key)
        if value is not None:
            metrics.append({
                'label': label,
                'help': help_text,
                'value': value,
                'percent': round(max(0.0, min(1.0, value)) * 100, 1),
            })
    return render(request, 'app01_phish_detector/about.html', {
        'page_title': 'About',
        'model_name': MODEL_NAME,
        'threshold': THRESHOLD,
        'metrics': metrics,
        'trained_at': BUNDLE.get('trained_at', ''),
        'split': BUNDLE.get('split', ''),
        'n_features': len(FEATURE_NAMES),
        'feature_names': FEATURE_NAMES,
    })


def result(request):
    page_title = 'Result'
    raw_url = request.GET.get('url', '').strip()

    if not raw_url:
        return render(request, TEMPLATE_RESULT, {
            'page_title': page_title,
            'error': 'No URL provided.',
        })

    # 1. Normalise + extract features (same code path as training)
    try:
        url = normalise_url(raw_url)
        x = np.array([features_vector(url)], dtype=float)
    except ValueError as e:
        return render(request, TEMPLATE_RESULT, {
            'page_title': page_title,
            'error': f'Invalid URL: {e}',
            'url': raw_url,
        })
    except Exception:
        logger.exception("Feature extraction failed for %r", raw_url)
        return render(request, TEMPLATE_RESULT, {
            'page_title': page_title,
            'error': 'Could not analyse that URL.',
            'url': raw_url,
        })

    # 2. Predict with the tuned threshold (not model.predict(), which uses 0.5)
    try:
        prob_legitimate, prob_phishing = (float(p) for p in MODEL.predict_proba(x)[0])
    except Exception:
        logger.exception("Prediction failed for %r", url)
        return render(request, TEMPLATE_RESULT, {
            'page_title': page_title,
            'error': 'Prediction failed. See server logs.',
            'url': url,
        })

    is_phishing = prob_phishing >= THRESHOLD
    logger.debug("url=%s p_phish=%.4f threshold=%.3f features=%s",
                 url, prob_phishing, THRESHOLD, dict(zip(FEATURE_NAMES, x[0])))

    URLCheck.objects.create(
        url=url,
        is_phishing=is_phishing,
        probability_legitimate=prob_legitimate,
        probability_phishing=prob_phishing,
    )

    return render(request, TEMPLATE_RESULT, {
        'page_title': page_title,
        'ans': int(is_phishing),
        'url': url,
        'prob_legitimate': prob_legitimate,
        'prob_phishing': prob_phishing,
        'threshold': THRESHOLD,
        'model_name': MODEL_NAME,
    })