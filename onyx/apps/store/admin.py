
from django.contrib import admin
from .models import Product, Author, Tag ,ReviewRating


class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'category', 'link', 'modified_date', 'created_date', 'is_available',)
    prepopulated_fields = {'slug': ('product_name',)}

    search_fields = ('product_name',)
    list_filter = ('category', 'author', 'modified_date', 'created_date',)

    filter_horizontal= ( 'author', 'tags',)

class AuthorAdmin(admin.ModelAdmin):
    list_display = ('name', 'last_name', 'nationality',)
    
    search_fields = ('name', 'last_name',)
    
admin.site.register(Product, ProductAdmin)
admin.site.register(Author, AuthorAdmin)
admin.site.register(Tag)
admin.site.register(ReviewRating)



