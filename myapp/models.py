from django.db import models
from django.utils.safestring import mark_safe
from multiselectfield import MultiSelectField

# Create your models here.
class registermodel(models.Model):  # register model
    fullname = models.CharField(max_length=20)
    email = models.EmailField()
    password = models.CharField(max_length=10)
    confirmpassword = models.CharField(max_length=10)
    phone = models.BigIntegerField()
    Identy_Card = models.ImageField(upload_to="photos", default="")
    Role = models.CharField(max_length=10, null=False, default="designer")

    def identy_card(self):  # store a image , this fun name is same as in admin file
        return mark_safe('<img src="{}" width="100"/>'.format(self.Identy_Card.url))

    identy_card.allow_tags = True

    def _str_(self):  # return a name
        return self.fullname


class Packagecategory(models.Model):
    Packcatname = models.CharField(max_length=50)

    def __str__(self):
        return self.Packcatname

# add packagemodel
class packages(models.Model):

    SERVICE_CHOICES = [
        ('Color Combination', 'Color Combination'),
        ('WallPaper', 'Wall Paper'),
        ('POP Design', 'POP Design'),
        ('Wardrobe Furniture', 'Wardrobe Furniture'),
        ('Lighting Design', 'Lighting Design'),
        ('Space Planning', 'Space Planning'),
    ]

    # package_type=models.CharField(max_length=255)
    Designer_Name = models.CharField(max_length=20)
    package_design_style = models.CharField(max_length=10)
    package_type = models.ForeignKey(Packagecategory, on_delete=models.CASCADE, null=True)
    package_category = models.CharField(max_length=10)
    BhkType = models.CharField(max_length=10,null=True)
    package_price = models.FloatField()
    time_duration = models.CharField(max_length=10)
    package_desc = models.TextField()
    package_img = models.ImageField(upload_to="photos")
    ExtraServices = MultiSelectField(choices=SERVICE_CHOICES, max_length=200)
    client_id = models.ForeignKey(registermodel,on_delete=models.CASCADE,null=True,related_name='client_packages')
    Designerid = models.ForeignKey(registermodel,on_delete=models.CASCADE,null=True,related_name='designer_packages')

    def package_images(self):
        return mark_safe('<img src="{}" width="100"/>'.format(self.package_img.url))


    def __str__(self):
        return f'{self.Designer_Name}'


# category
class category(models.Model):
    catname = models.CharField(max_length=50)


# category
class Portfoliocategory(models.Model):
    Portcatname = models.CharField(max_length=50)

    def __str__(self):
        return self.Portcatname


# add portfolio
class portfolio(models.Model):
    Designer_Name = models.CharField(max_length=255, null=True)
    catid = models.ForeignKey(category, on_delete=models.CASCADE, null=True)
    aboutyourself = models.CharField(max_length=40)
    designstyle = models.ForeignKey(Portfoliocategory, on_delete=models.CASCADE, null=True)
    designerskill = models.TextField(max_length=20)
    experience = models.CharField(max_length=50)
    sampleimage = models.ImageField(upload_to="photos")
    client_id = models.ForeignKey(registermodel,on_delete=models.CASCADE,null=True,related_name='client_portfolios')
    Designerid = models.ForeignKey(registermodel,on_delete=models.CASCADE,null=True,related_name='designer_portfolios')

    def __str__(self):
        return self.Designer_Name

    def sample_design(self):
        return mark_safe('<img src="{}" width="100"/>'.format(self.sampleimage.url))

    sample_design.allow_tags = True



class booking(models.Model):
    SERVICE_CHOICES = [
        ('Color Combination', 'Color Combination'),
        ('WallPaper', 'Wall Paper'),
        ('POP Design', 'POP Design'),
        ('Wardrobe Furniture', 'Wardrobe Furniture'),
        ('Lighting Design', 'Lighting Design'),
        ('Space Planning', 'Space Planning'),
    ]

    Client_Name = models.CharField(max_length=20)
    design_style = models.CharField(max_length=10)
    package_type = models.CharField(max_length=10)
    package_category = models.CharField(max_length=10)
    quantity=models.IntegerField(null=True)
    totalamount=models.FloatField(null=True)
    date_time = models.DateTimeField()
    location = models.TextField()
    BHKType = models.CharField(max_length=10)
    propertySize = models.FloatField()
    Time_duration = models.CharField(max_length=10)
    requirement = models.TextField()
    status = models.CharField(max_length=10)
    services = MultiSelectField(choices=SERVICE_CHOICES, max_length=200)
    client_id = models.ForeignKey(registermodel,on_delete=models.CASCADE,null=True,related_name='client_bookings')
    Designerid = models.ForeignKey(registermodel,on_delete=models.CASCADE,null=True,related_name='designer_bookings')
    package_id = models.ForeignKey(packages,on_delete=models.CASCADE,null=True)

class contact(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    subject = models.TextField()
    phone_number = models.BigIntegerField()
    message = models.TextField()
    client_id = models.ForeignKey(registermodel,on_delete=models.CASCADE,null=True,related_name='client_contacts')
    Designerid = models.ForeignKey(registermodel,on_delete=models.CASCADE,null=True,related_name='designer_contacts')

    def __str__(self):
        return self.name

class review(models.Model):
    name = models.CharField(max_length=20)
    star = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    review = models.TextField()
    client_id = models.ForeignKey(registermodel,on_delete=models.CASCADE,null=True)


class Payment(models.Model):
    booking = models.ForeignKey(booking, on_delete=models.CASCADE)
    amount = models.FloatField()
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, default="Pending")
    created_at = models.DateTimeField(auto_now_add=True)