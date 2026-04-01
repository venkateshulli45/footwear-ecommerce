from django.db import models

# Create your models here.
class Destination(models.Model):
    discount=models.IntegerField()
    category=models.TextField()
    title=models.CharField(max_length=100)
    link=models.TextField()
    offer=models.BooleanField(default=False)
    img=models.ImageField(upload_to='pics')
    
    def __str__(self):
        return self.category