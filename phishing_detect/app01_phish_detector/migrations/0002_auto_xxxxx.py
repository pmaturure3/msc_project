operations = [
    migrations.AddField(
        model_name='urlcheck',
        name='probability_legitimate',
        field=models.FloatField(null=True, blank=True),
    ),
    migrations.AddField(
        model_name='urlcheck',
        name='probability_phishing',
        field=models.FloatField(null=True, blank=True),
    ),
]
