# Generated by Django 5.0 on 2024-03-05 23:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('python_learning_app', '0009_remove_basis_id_remove_introcourse_primary_key_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='news',
            name='detail',
            field=models.TextField(blank=True, verbose_name='更新内容'),
        ),
    ]
