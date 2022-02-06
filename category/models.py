from pyexpat import model
from tabnanny import verbose
from unittest.util import _MAX_LENGTH
from django.db import models
from django.urls import reverse

# Create your models here.
class category(models.Model):
    category_name = models.CharField(max_length=50,unique=True)
    
    #ใส่ slugfield เพื่อให้มันเขียนที่slugเหมือนเขียนชื่อ
    slug = models.SlugField(max_length=100,unique=True)
    
    description = models.TextField(max_length=255,blank=True)
    cat_image = models.ImageField(upload_to='photos/categories',blank=True)

    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'categories'


    def get_url(self):
        return reverse('products_by_category', args=[self.slug]) #เรียก url ของ category บางตัว


    def __str__(self) :
        return self.category_name
    