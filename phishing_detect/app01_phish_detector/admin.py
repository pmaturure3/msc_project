from django.contrib import admin
from .models import URLCheck

@admin.register(URLCheck)
class URLCheckAdmin(admin.ModelAdmin):
    list_display = ('url', 'is_phishing', 'probability_legitimate', 'probability_phishing', 'checked_at')
    list_filter = ('is_phishing', 'checked_at')
    search_fields = ('url',)