# Generated by Django 5.0 on 2024-03-07 02:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('python_learning_app', '0011_alter_news_detail'),
    ]

    operations = [
        migrations.AlterField(
            model_name='introcourse',
            name='content',
            field=models.TextField(blank=True, verbose_name='内容[&nbsp;]'),
        ),
    ]