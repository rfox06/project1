from django.db import models
import uuid
from apps.category.models import Category
from django.urls import reverse
from apps.accounts.models import Account
from django.db.models import Avg, Count

#apps terceros

from ckeditor_uploader.fields import RichTextUploadingField
from django.conf import settings

class Author(models.Model):
    name = models.CharField(max_length=90)
    last_name = models.CharField(max_length=90)
    nationality = models.CharField(max_length=100)
    class Meta:
        ordering = ['name']
    def __str__(self):
        return str(self.id) + ' - ' + self.name + ' - ' + self.last_name 


class Tag(models.Model):
    name = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now_add=True)
    id = models.UUIDField(default=uuid.uuid4, unique=True,
                          primary_key=True, editable = False)
    def __str__(self):
        return self.name

class Product(models.Model):
    product_name    = models.CharField(max_length=200, unique=True)
    
    slug            = models.SlugField(max_length=200, unique=True)
    description     = RichTextUploadingField(blank=True)
    link            = models.URLField(max_length=300)
    images          = models.ImageField(upload_to='photos/products')
    author          = models.ManyToManyField(Author)
    is_available    = models.BooleanField(default=True)
    tags            = models.ManyToManyField('Tag', blank=True)
    category        = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_date    = models.DateTimeField(auto_now_add=True)
    modified_date   = models.DateTimeField(auto_now=True)

    def get_url(self):
        return reverse('product_detail', args=[self.category.slug, self.slug])
        #return reverse('product_detail', args=[self.category.slug, self.slug])

    def __str__(self):
        return self.product_name

    def averageReview(self):
        reviews = ReviewRating.objects.filter(product=self, status=True).aggregate(average=Avg('rating'))
        avg = 0
        if reviews['average'] is not None:
            avg = float(reviews['average'])
        return avg

    def countReview(self):
        reviews = ReviewRating.objects.filter(product=self, status=True).aggregate(count=Count('id'))
        count = 0
        if reviews['count'] is not None:
            count = int(reviews['count'])
        return count


class ReviewRating(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100, blank=True)
    review = models.TextField(max_length=500, blank=True)
    rating = models.FloatField()
    ip = models.CharField(max_length=20, blank=True)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.subject

