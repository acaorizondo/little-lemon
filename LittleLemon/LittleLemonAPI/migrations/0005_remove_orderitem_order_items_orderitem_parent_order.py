# Generated by Django 4.2.3 on 2023-07-22 17:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('LittleLemonAPI', '0004_orderitem_order_items'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orderitem',
            name='order_items',
        ),
        migrations.AddField(
            model_name='orderitem',
            name='parent_order',
            field=models.ForeignKey(default=30, on_delete=django.db.models.deletion.CASCADE, related_name='items', to='LittleLemonAPI.order'),
            preserve_default=False,
        ),
    ]
