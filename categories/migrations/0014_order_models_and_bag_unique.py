# Generated manually for Order / OrderLine and BagItem constraints

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('categoryc', '0013_bagitem_size'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='bagitem',
            unique_together=set(),
        ),
        migrations.AlterField(
            model_name='bagitem',
            name='quantity',
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AlterField(
            model_name='bagitem',
            name='size',
            field=models.CharField(default='1', max_length=3),
        ),
        migrations.AlterField(
            model_name='bagitem',
            name='user',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='bag_items',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterUniqueTogether(
            name='bagitem',
            unique_together={('user', 'product_id', 'category', 'size')},
        ),
        migrations.AlterModelOptions(
            name='bagitem',
            options={'ordering': ['-added_at']},
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_number', models.CharField(editable=False, max_length=32, unique=True)),
                ('fullname', models.CharField(max_length=100)),
                ('phone', models.CharField(max_length=15)),
                ('address', models.TextField()),
                ('landmark', models.CharField(blank=True, max_length=100)),
                ('pincode', models.CharField(max_length=10)),
                ('subtotal', models.DecimalField(decimal_places=2, max_digits=10)),
                ('shipping_fee', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('total', models.DecimalField(decimal_places=2, max_digits=10)),
                (
                    'status',
                    models.CharField(
                        choices=[
                            ('pending_payment', 'Pending payment'),
                            ('confirmed', 'Confirmed'),
                            ('processing', 'Processing'),
                            ('shipped', 'Shipped'),
                            ('delivered', 'Delivered'),
                            ('cancelled', 'Cancelled'),
                        ],
                        default='pending_payment',
                        max_length=32,
                    ),
                ),
                (
                    'payment_status',
                    models.CharField(
                        choices=[
                            ('pending', 'Payment pending'),
                            ('paid', 'Paid'),
                            ('failed', 'Failed'),
                            ('cod', 'Cash on delivery'),
                        ],
                        default='pending',
                        max_length=32,
                    ),
                ),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                (
                    'user',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='orders',
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='OrderLine',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(max_length=3)),
                ('product_id', models.IntegerField()),
                ('product_label', models.CharField(max_length=255)),
                ('size', models.CharField(max_length=3)),
                ('quantity', models.PositiveIntegerField()),
                ('unit_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('line_total', models.DecimalField(decimal_places=2, max_digits=10)),
                (
                    'order',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='lines',
                        to='categoryc.order',
                    ),
                ),
            ],
            options={
                'ordering': ['id'],
            },
        ),
    ]
