# Generated by Django 5.0 on 2024-03-05 23:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('python_learning_app', '0010_news_detail'),
    ]

    operations = [
        migrations.AlterField(
            model_name='news',
            name='detail',
            field=models.TextField(blank=True, verbose_name='詳細'),
        ),
    ]