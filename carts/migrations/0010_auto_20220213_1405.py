# Generated by Django 3.1 on 2022-02-13 07:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('carts', '0009_auto_20220213_1404'),
    ]

    operations = [
        migrations.RenameField(
            model_name='cartitem',
            old_name='variation',
            new_name='variations',
        ),
    ]