from django.db import models


# Create your models here.
class Contact(models.Model):
    # contact_id=models.AutoField(primary_key=True)
    name=models.CharField(max_length=50)
    email=models.EmailField()
    desc=models.TextField(max_length=500)
    phonenumber=models.IntegerField()

    def __int__(self):
        return self.id


class Product(models.Model):
    product_id = models.AutoField
    brand= models.CharField(max_length=100)
    product_name = models.CharField(max_length=100)
    category = models.CharField(max_length=100, default="")
    subcategory = models.CharField(max_length=50, default="")
    price = models.IntegerField(default=0)
    short_desc = models.CharField(max_length=300)
    long_desc = models.CharField(max_length=300000)
    image = models.ImageField(upload_to='images/images')

    def __str__(self):
        return self.product_name



class Orders(models.Model):
    order_id = models.AutoField(primary_key=True)
    items_json =  models.CharField(max_length=5000)
    amount = models.CharField(max_length=90)
    name = models.CharField(max_length=90)
    email = models.CharField(max_length=90)
    user_email= models.CharField(max_length=90,blank=True,null=True,default=False)
    address1 = models.CharField(max_length=200)
    address2 = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=100)    
    payment_id = models.CharField(max_length=1000,blank=True,null=True)    
    signature_id = models.CharField(max_length=1000,blank=True,null=True)    
    signature_id = models.CharField(max_length=1000,blank=True,null=True)   
    payment_status  = models.CharField(max_length=1000,blank=True,null=True)   
    oid=models.CharField(max_length=150,blank=True)
    amountpaid=models.CharField(max_length=500,blank=True,null=True)
    paymentstatus=models.CharField(max_length=20,blank=True)
    phone = models.CharField(max_length=100,default="")
    update_description = models.CharField(default=False, max_length=5000)
    isdelivered=models.BooleanField(default=False)
    def __str__(self):
        return self.name
