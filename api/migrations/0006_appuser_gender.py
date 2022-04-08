# Generated by Django 4.0.2 on 2022-04-08 06:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_appuser_is_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='appuser',
            name='gender',
            field=models.CharField(blank=True, choices=[('male', 'male'), ('female', 'female'), ('human', 'human')], default='human', max_length=10, null=True),
        ),
    ]