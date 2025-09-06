from django.db import models
from django.utils.text import slugify
from django.core.validators import FileExtensionValidator

# Create your models here.
class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        abstract =True

class Restaurant(TimeStampedModel):
    name = models.CharField(max_length=150,unique=True)
    slug = models.SlugField(max_length=160,unique=True,blank=True)
    description = models.CharField(max_length=1000,blank=True)
    address = models.CharField(max_length=260,blank=True)
    city = models.CharField(max_length=100,blank=True)
    phone = models.CharField(max_length=15,blank=True)
    email = models.EmailField(blank=True,null=True)
    website = models.URLField(blank=True,null=True)
    opening_time = models.DateTimeField(blank=True,null=True)
    closing_time = models.DateTimeField(blank=True,null=True)
    
    class Meta:
        ordering = ["name"]
    
    def save(self,*args,**kargs):
        self.name = self.name.lower()
        if not self.slug:
            self.slug = slugify(self.name)[:160]
        super().save(*args,**kargs)
    
    def __str__(self):
        return self.name


class Category(TimeStampedModel):
    restaurant = models.ForeignKey(Restaurant,on_delete=models.CASCADE,related_name="categories")
    name = models.CharField(max_length=120,unique=True)
    slug = models.SlugField(max_length=150,unique=True,blank=True)
    description = models.CharField(max_length=500,blank=True)
    
    class Meta:
        ordering = ["name"]
        unique_together = [("name","restaurant")]
        
    
    def save(self,*args,**kwargs):
        self.name=self.name.lower()
        if not self.slug:
            self.slug = slugify(self.name)[:140]
        super().save(*args,**kwargs)
    def __str__(self):
        return self.name
    

def profile_image_upload_to(instance,filename):
    return f"menuItems/{instance.slug}-{filename}"
    
class MenuItem(TimeStampedModel):
    category = models.ForeignKey(Category,on_delete=models.CASCADE,related_name="items")
    name= models.CharField(max_length=200)
    slug = models.SlugField(max_length=220,unique=True,blank=True,db_index=True)
    description = models.CharField(max_length=270,blank=True)
    is_vegetarian = models.BooleanField(default=True)
    
    price = models.DecimalField(max_digits=7,decimal_places=2)
    is_available = models.BooleanField(default=True)
    serving_size =models.CharField(max_length=100, blank=True, help_text="1/peice")
    image = models.ImageField(upload_to=profile_image_upload_to,blank=True,null=True,
                              validators=[FileExtensionValidator(allowed_extensions=["jpg","jpeg","png","webp"])])
    
    class Meta:
        ordering = [ "category", "name"]
        indexes = [models.Index(fields=["slug"])]
        
    def save(self,*args,**kwargs):
        self.name= self.name.lower()
        if not self.slug:
            self.slug = slugify(self.name)[:220]
        super().save(*args,**kwargs)
    def __str__(self):
        return f"{self.name}"
    