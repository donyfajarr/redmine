# Generated by Django 5.0.2 on 2024-03-07 04:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0002_dept'),
    ]

    operations = [
        migrations.CreateModel(
            name='priority',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='status',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=30)),
            ],
        ),
    ]
