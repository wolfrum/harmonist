# Generated by Django 5.1.7 on 2025-03-24 12:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_artist_popularity'),
    ]

    operations = [
        migrations.AddField(
            model_name='artist',
            name='followers',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='artist',
            name='uri',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='album',
            name='release_date',
            field=models.CharField(blank=True, max_length=32, null=True),
        ),
        migrations.AlterField(
            model_name='artist',
            name='name',
            field=models.CharField(db_index=True, max_length=200),
        ),
    ]
