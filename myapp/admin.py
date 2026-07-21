from django.contrib import admin
from .models import *

# Register your models here.

class showregistermodel(admin.ModelAdmin):
    list_display = ["id","fullname","email","password","confirmpassword","phone","identy_card","Role"]

admin.site.register(registermodel,showregistermodel)

 # category
class showcategory(admin.ModelAdmin):
    list_display=["id","catname"]

admin.site.register(category,showcategory)

class showpackagecategory(admin.ModelAdmin):
    list_display=["id","Packcatname"]

admin.site.register(Packagecategory,showpackagecategory)

class showportfoliocategory(admin.ModelAdmin):
    list_display=["id","Portcatname"]

admin.site.register(Portfoliocategory,showportfoliocategory)

class showpackagemodel(admin.ModelAdmin):
    list_display = ["id","Designer_Name", "package_type" , "package_design_style", "package_category","BhkType","package_price","time_duration","package_desc", "package_images","ExtraServices","client_id","Designerid"]

admin.site.register(packages,showpackagemodel)

class showportfolio(admin.ModelAdmin):
    list_display = ["id","Designer_Name","catid","aboutyourself","designstyle","designerskill","experience","sample_design","client_id","Designerid"]

admin.site.register(portfolio,showportfolio)

class showbooking(admin.ModelAdmin):
    list_display = ["id","Client_Name","design_style","package_type","package_category","date_time","location","BHKType","propertySize","Time_duration","requirement","status","services","totalamount","package_id"]

admin.site.register(booking,showbooking)

class showcontact(admin.ModelAdmin):
    list_display = ["id","name","email","subject","phone_number","message","client_id","Designerid"]

admin.site.register(contact,showcontact)

class showreview(admin.ModelAdmin):
    list_display = ["id","name","star","review"]

admin.site.register(review,showreview)


class showpayment(admin.ModelAdmin):
    list_display = ["id","booking","amount","razorpay_order_id","status"]

admin.site.register(Payment,showpayment)