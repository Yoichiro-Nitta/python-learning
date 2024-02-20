# Generated by Django 5.0 on 2024-02-14 13:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('python_learning_app', '0002_quartet_frame'),
    ]

    operations = [
        migrations.CreateModel(
            name='News',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(verbose_name='更新日')),
                ('comment', models.CharField(max_length=80, verbose_name='更新内容')),
            ],
        ),
    ]