# Generated by Django 5.0 on 2024-03-05 21:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('python_learning_app', '0007_alter_comperesult_result_alter_quartetresult_result'),
    ]

    operations = [
        migrations.AddField(
            model_name='basis',
            name='primary_key',
            field=models.PositiveIntegerField(default=1, verbose_name='primary_key'),
        ),
        migrations.AddField(
            model_name='introcourse',
            name='primary_key',
            field=models.PositiveIntegerField(default=1, verbose_name='primary_key'),
        ),
    ]