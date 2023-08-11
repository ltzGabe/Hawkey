
from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User
from phonenumber_field.modelfields import PhoneNumberField
from django.db.models.deletion import CASCADE
from django_countries.fields import CountryField, TemporaryEscape
from django_countries import Countries
class supportedCountries(Countries):
    only = [
        'US', 'GB',
        
    ]
class Product(models.Model):
    productURL              =   models.URLField(max_length=60000, default="")
    productNAME             =   models.CharField(max_length=500,default="")
    productDATE             =   models.DateTimeField(auto_now_add=True)
    productIMAGE            =   models.URLField(max_length=10000, default="")
    productRRP              =   models.DecimalField(max_digits=10, decimal_places=2, default=0.00,null=True)
    productPRICE            =   models.DecimalField(max_digits=10, decimal_places=2, default=0.00,null=True)
    offersUsedProductPRICE  =   models.DecimalField(max_digits=10, decimal_places=2, default=0.00,null=True)
    offersNewProductPRICE   =   models.DecimalField(max_digits=10, decimal_places=2, default=0.00,null=True)
    productMANUFACTURE      =   models.CharField(max_length=9999999,default="", null=True)
    productBRAND            =   models.CharField(max_length=9999999,default="", null=True)
    productMODEL            =   models.CharField(max_length=9999999,default="", null=True)
    productCONDITON         =   models.CharField(max_length=9999999,default="", null=True)
    productMERCHANT         =   models.CharField(max_length=9999999,default="", null=True)
    productPRODUCTGROUP     =   models.CharField(max_length=9999999,default="", null=True)
    productASIN             =   models.CharField(max_length=9999999,default="", null=True)
    productCOUNTRY          =   CountryField(countries=supportedCountries,null=True, blank=False)
    def __str__(self):
        return self.productNAME

class Customer(models.Model):
    name                    =   models.OneToOneField(User, on_delete=models.CASCADE, default=0)
    numberTracking          =   models.IntegerField(default=1)
    
    
    
    def __str__(self):
        return str(self.name)
class Tracker(models.Model):
    product                 =   models.ForeignKey(Product, null=True, on_delete=CASCADE,blank=True)
    customer                =   models.ForeignKey(Customer, null=True, on_delete=CASCADE)
class Reminder(models.Model):
    product                 =   models.ForeignKey(Product, null=True, on_delete=CASCADE,blank=True)
    customer                =   models.ForeignKey(Customer, null=True, on_delete=CASCADE)
    reminderPriceDB           =   models.DecimalField(null=True,max_digits=10, decimal_places=2,blank=True)
    reminderTypeDB            =   models.CharField(blank=True,max_length=13,choices=(("Email","Email"),("Phone","Phone")))

