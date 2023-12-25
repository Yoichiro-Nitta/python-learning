# Generated by Django 4.2.7 on 2023-12-18 22:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pythonL', '0019_remove_basis_u_title_basis_major_h_basis_minor_h_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='basis',
            name='c_output',
            field=models.TextField(blank=True, verbose_name='範囲の範囲/要求出力/nct/'),
        ),
        migrations.AlterField(
            model_name='basis',
            name='e_answer',
            field=models.TextField(blank=True, verbose_name='解答例/nct/'),
        ),
        migrations.AlterField(
            model_name='basis',
            name='i_range',
            field=models.TextField(blank=True, verbose_name='範囲[]'),
        ),
        migrations.AlterField(
            model_name='basis',
            name='q_data',
            field=models.TextField(blank=True, verbose_name='出題データ/nct/'),
        ),
    ]