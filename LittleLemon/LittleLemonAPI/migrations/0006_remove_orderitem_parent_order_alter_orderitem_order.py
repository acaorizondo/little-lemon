# Generated by Django 4.2.3 on 2023-07-23 04:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('LittleLemonAPI', '0005_remove_orderitem_order_items_orderitem_parent_order'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orderitem',
            name='parent_order',
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='LittleLemonAPI.order'),
        ),
    ]