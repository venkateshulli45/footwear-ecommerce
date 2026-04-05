import uuid

from django.db import models
from django.contrib.auth.models import User


class BagItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bag_items')
    product_id = models.IntegerField()
    category = models.CharField(max_length=3)
    size = models.CharField(max_length=3, default='1')
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product_id', 'category', 'size')
        ordering = ['-added_at']


class Order(models.Model):
    """Placed order; payment is finalized in a later gateway step (payment_status)."""

    class Status(models.TextChoices):
        PENDING_PAYMENT = 'pending_payment', 'Pending payment'
        CONFIRMED = 'confirmed', 'Confirmed'
        PROCESSING = 'processing', 'Processing'
        SHIPPED = 'shipped', 'Shipped'
        DELIVERED = 'delivered', 'Delivered'
        CANCELLED = 'cancelled', 'Cancelled'

    class PaymentStatus(models.TextChoices):
        PENDING = 'pending', 'Payment pending'
        PAID = 'paid', 'Paid'
        FAILED = 'failed', 'Failed'
        COD = 'cod', 'Cash on delivery'

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    order_number = models.CharField(max_length=32, unique=True, editable=False)
    fullname = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    landmark = models.CharField(max_length=100, blank=True)
    pincode = models.CharField(max_length=10)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=32,
        choices=Status.choices,
        default=Status.PENDING_PAYMENT,
    )
    payment_status = models.CharField(
        max_length=32,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.order_number} — {self.user.username}'

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = uuid.uuid4().hex[:12].upper()
        super().save(*args, **kwargs)


class OrderLine(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='lines')
    category = models.CharField(max_length=3)
    product_id = models.IntegerField()
    product_label = models.CharField(max_length=255)
    size = models.CharField(max_length=3)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    line_total = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        ordering = ['id']


class Purchase(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) # Use a valid user ID as the default
    fullname = models.CharField(max_length=100)
    size = models.CharField(max_length=3)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    landmark = models.CharField(max_length=100, blank=True)
    pincode = models.CharField(max_length=10)
    product = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.product}"

class SizeAvailability(models.Model):
    size = models.CharField(max_length=3)
    quantity = models.IntegerField(default=0)

    class Meta:
        abstract = True

class WFMSizeAvailability(SizeAvailability):
    product = models.ForeignKey('WFM', on_delete=models.CASCADE, related_name='sizes')

    class Meta:
        verbose_name = "Women's Footwear Size"
        verbose_name_plural = "Women's Footwear Sizes"

class MFMSizeAvailability(SizeAvailability):
    product = models.ForeignKey('MFM', on_delete=models.CASCADE, related_name='sizes')

    class Meta:
        verbose_name = "Men's Footwear Size"
        verbose_name_plural = "Men's Footwear Sizes"

class KFMSizeAvailability(SizeAvailability):
    product = models.ForeignKey('KFM', on_delete=models.CASCADE, related_name='sizes')

    class Meta:
        verbose_name = "Kids' Footwear Size"
        verbose_name_plural = "Kids' Footwear Sizes"

class BaseProduct(models.Model):
    price = models.IntegerField()
    mrp = models.IntegerField(null=True, blank=True)
    rating = models.DecimalField(max_digits=2, decimal_places=1, null=True, blank=True)
    rating_count = models.PositiveIntegerField(default=0)
    model = models.TextField()
    company = models.CharField(max_length=100)
    img = models.ImageField(upload_to='pics')
    articleno = models.CharField(max_length=100)
    _available_sizes = None

    class Meta:
        abstract = True

    @property
    def available_sizes(self):
        if self._available_sizes is None:
            self._available_sizes = list(self.sizes.filter(quantity__gt=0).values_list('size', flat=True))
        return self._available_sizes

    def set_available_sizes(self, sizes):
        self._available_sizes = sizes

class WFM(BaseProduct):
    AVAILABLE_SIZES = ['4', '5', '6', '7', '8']

    class Meta:
        verbose_name = "Women's Footwear"
        verbose_name_plural = "Women's Footwear"

    def __str__(self):
        return f"{self.company} - {self.articleno}"

class MFM(BaseProduct):
    AVAILABLE_SIZES = ['6', '7', '8', '9', '10']

    class Meta:
        verbose_name = "Men's Footwear"
        verbose_name_plural = "Men's Footwear"

    def __str__(self):
        return f"{self.company} - {self.articleno}"

class KFM(BaseProduct):
    AVAILABLE_SIZES = ['1', '2', '3', '4', '5']

    class Meta:
        verbose_name = "Kids' Footwear"
        verbose_name_plural = "Kids' Footwear"

    def __str__(self):
        return f"{self.company} - {self.articleno}"
