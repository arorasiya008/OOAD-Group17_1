from django.db import models
from django.utils import timezone

# completed - change if necessary. 
# cannot use postgre therefore no array implementation possible. For array we are using JsonField with list default

def user_upload_path_items(instance, filename):
    # Upload to "media/Category_<categoryName>/<filename>"
    return f'Category_{instance.categoryName}/{filename}'

def user_upload_path_category(instance, filename):
     # Upload to "media/Category_<categoryId>/<filename>"
     return f'Category_/{filename}'


class Users(models.Model):
    userId = models.AutoField(primary_key=True)
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    walletAddress = models.CharField(max_length=255)
    email = models.EmailField(max_length=254) #use validate_email inbuilt validator for emails

class Payments(models.Model):
    itemId = models.IntegerField()
    paymentId = models.AutoField(primary_key=True)
    status = models.BooleanField(default=False)
    userId = models.IntegerField()
    amount = models.DecimalField(max_digits=100, decimal_places=2)
    
class Items(models.Model):
    itemId = models.AutoField(primary_key=True)
    itemName = models.CharField(max_length=40)
    userId = models.IntegerField()
    description = models.CharField(max_length=255)
    auctionStartTime = models.DateTimeField()
    auctionEndTime = models.DateTimeField()
    timeBuffer = models.DateTimeField(default = timezone.now())
    startingBid = models.PositiveBigIntegerField()
    saleStatus = models.BooleanField(default=False)
    costPrice = models.IntegerField(blank=True, null=True)
    itemImage = models.ImageField(upload_to=user_upload_path_items) #add upload_to='folder where uploaded images will be stored'
    categoryName = models.CharField(max_length=40)
    bidders = models.JSONField(null=True, blank=True, default=list)  

    #method to get image url
    def get_image_url(self):
            if self.itemImage:
                return self.itemImage.url
            return None

class Bids(models.Model):
    bidId = models.AutoField(primary_key=True)
    itemId = models.IntegerField()
    contribution = models.JSONField()
    amount = models.DecimalField(max_digits=100, decimal_places=2, null=True,blank=True )  
    bidPlacedTime = models.DateTimeField(auto_now_add=True)
    
class Category(models.Model):
    categoryId = models.AutoField(primary_key=True)
    categoryName = models.CharField(max_length=255)
    categoryDescription = models.CharField(max_length=255)
    categoryImage = models.ImageField(upload_to=user_upload_path_category) #add upload_to='folder where uploaded images will be stored'
    
    #method to get image url
    def get_image_url(self):
            if self.categoryImage:
                return self.categoryImage.url
            return None


