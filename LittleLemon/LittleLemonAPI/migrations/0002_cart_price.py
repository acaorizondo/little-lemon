# Generated by Django 4.2.3 on 2023-07-20 23:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('LittleLemonAPI', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='cart',
            name='price',
            field=models.DecimalField(decimal_places=2, default=1, max_digits=6),
            preserve_default=False,
        ),
    ]
