# Generated by Django 4.2.7 on 2023-12-08 17:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pythonL', '0004_basis_title'),
    ]

    operations = [
        migrations.AlterField(
            model_name='basis',
            name='title',
            field=models.CharField(max_length=80, verbose_name='タイトル'),
        ),
    ]
