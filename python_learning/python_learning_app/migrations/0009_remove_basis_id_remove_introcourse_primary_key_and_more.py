# Generated by Django 5.0 on 2024-03-05 23:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('python_learning_app', '0008_basis_primary_key_introcourse_primary_key'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='basis',
            name='id',
        ),
        migrations.RemoveField(
            model_name='introcourse',
            name='primary_key',
        ),
        migrations.AlterField(
            model_name='basis',
            name='primary_key',
            field=models.PositiveIntegerField(primary_key=True, serialize=False, verbose_name='primary_key'),
        ),
    ]
