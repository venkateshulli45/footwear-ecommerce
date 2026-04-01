from django.db import models
from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.models import User


class BagItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product_id = models.IntegerField()
    category = models.CharField(max_length=3)  
    size = models.CharField(max_length=3,default=1)
    quantity = models.IntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product_id', 'category')


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
