from django.db import models

class URLCheck(models.Model):
    url = models.URLField(max_length=2048)
    is_phishing = models.BooleanField()
    checked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-checked_at']

    def __str__(self):
        label = "Phishing" if self.is_phishing else "Legitimate"
        return f"{self.url} — {label}"