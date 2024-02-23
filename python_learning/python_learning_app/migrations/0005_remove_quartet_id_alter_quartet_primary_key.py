# Generated by Django 5.0 on 2024-02-21 16:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('python_learning_app', '0004_quartet_primary_key'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='quartet',
            name='id',
        ),
        migrations.AlterField(
            model_name='quartet',
            name='primary_key',
            field=models.PositiveIntegerField(primary_key=True, serialize=False, verbose_name='primary_key'),
        ),
    ]
