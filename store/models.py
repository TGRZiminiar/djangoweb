from accounts.models import Account
from category.models import category
from django.db import models
from django.urls import reverse
from django.db.models import Avg,Count
# Create your models here.

class Product(models.Model):
    product_name    = models.CharField(max_length=200,unique=True)
    slug            = models.SlugField(max_length=200,unique=True)
    description     = models.TextField(max_length=500,blank=True)
    price           = models.IntegerField()
    images          = models.ImageField(upload_to = 'photos/products')
    stock           = models.IntegerField()
    is_avaliable    = models.BooleanField(default=True)
    category        = models.ForeignKey(category , on_delete=models.CASCADE)#เมื่อลบcategory สินค้าที่อยุ่ในแทคนี้จะโดนลบไปด้วย
    created_date    = models.DateTimeField(auto_now_add=True)
    modified_date   = models.DateTimeField(auto_now = True)
    
    
    def get_url(self):
        return reverse('product_detail', args=[self.category.slug, self.slug])

    def __str__(self):
        return self.product_name

    def AverageReview(self):
        review = ReviewRating.objects.filter(product = self,status = True).aggregate(average=Avg('rating'))
        #.aggregate(average=Avg('rating')) คือการเอาค่าเฉลี่ยของสินค้านั้นจาก rating ของ class ReviewRating
        avg = 0
        if review['average'] is not None:
            avg = float(review['average'])
            return avg

    def CountReview(self):
        review = ReviewRating.objects.filter(product = self,status = True).aggregate(count=Count('id'))
        count = 0
        if review['count'] is not None:
            count = int(review['count'])
            return count

class VariationManager(models.Manager): #class เอาไว้แยก variation category ระหว่างสีกับไซส์
    def colors(self):
        return super(VariationManager,self).filter(variation_category = 'color',is_active = True)

    def sizes(self):
        return super(VariationManager,self).filter(variation_category = 'size',is_active = True)

variation_category_choice = {
    ('color','color'),
    ('size','size'),
}

class Variation(models.Model):
    product = models.ForeignKey(Product,on_delete = models.CASCADE)
    variation_category = models.CharField(max_length=100,choices=variation_category_choice)
    variation_value = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now=True)
    objects = VariationManager()


    def __str__(self) :
        return self.variation_value

class ReviewRating(models.Model):
    product = models.ForeignKey(Product,on_delete=models.CASCADE) #ถ้าสินค้าถูกลบ review ถูกลบด้วยเพราะใช้ CASCADE
    user    = models.ForeignKey(Account,on_delete=models.CASCADE) 
    subject = models.CharField(max_length=100,blank=True)
    review  = models.TextField(max_length=500,blank=True)
    rating  = models.FloatField()
    ip      = models.CharField(max_length=20,blank=True)
    status  = models.BooleanField(default=True) #เอาไว้เปิดปิดreview
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self) :
        return self.subject