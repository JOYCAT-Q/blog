# Generated by Django 4.2.14 on 2024-07-19 11:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('comments', '0004_alter_comment_body'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='body',
            field=models.TextField(max_length=300, verbose_name='正文'),
        ),
    ]
