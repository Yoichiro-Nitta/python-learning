# Generated by Django 4.2.7 on 2023-12-08 16:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pythonL', '0003_alter_basis_e_answer'),
    ]

    operations = [
        migrations.AddField(
            model_name='basis',
            name='title',
            field=models.CharField(default='タイトル', max_length=60, verbose_name='タイトル'),
        ),
    ]
