# Generated by Django 4.2.7 on 2023-12-13 12:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pythonL', '0012_alter_introcourse_name_alter_introcourse_title'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='introcourse',
            name='name',
        ),
    ]