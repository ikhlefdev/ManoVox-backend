# Generated migration for adding video_url to SignPredictionHistory

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0010_signpredictionhistory'),
    ]

    operations = [
        migrations.AddField(
            model_name='signpredictionhistory',
            name='video_url',
            field=models.URLField(blank=True, max_length=500, null=True),
        ),
    ]
