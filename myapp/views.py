from django.contrib import messages
import razorpay
from django.conf import settings
from calendar import month
from os import remove
from django.http import request
from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from django.contrib.auth.hashers import check_password
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from datetime import timedelta
import random
import base64
from django.db.models import Max
from django.core.files.base import ContentFile
from .ai_service import generate_room_design
from django.db.models import Q
from django.contrib.auth import login
from django.contrib.auth.models import User
from functools import wraps
from django.contrib.auth import login, logout as django_logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


def login_required_custom(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):

        if not request.session.get("log_id"):
            messages.error(request, "Please login first.")
            return redirect("login")

        return view_func(request, *args, **kwargs)

    return wrapper

def role_required(*allowed_roles):
    def decorator(view_func):

        @wraps(view_func)
        def wrapper(request, *args, **kwargs):

            if not request.session.get("log_id"):
                messages.error(request, "Please login first.")
                return redirect("login")

            user_role = request.session.get("log_role")

            if user_role not in allowed_roles:
                messages.error(
                    request,
                    "You do not have permission to access this page."
                )
                return redirect("showportfolio")

            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator

def base():
    packages = Packagecategory.objects.all()
    portfolio = Portfoliocategory.objects.all()
    context = {
        "package": packages,
        "portfolio": portfolio
    }
    return context


# Create your views here.
def registerpage(request):
    if request.session.get("log_id"):
        return redirect("showportfolio")

    context = base()
    return render(request, "Register.html", context)


def loginpage(request):
    if request.session.get("log_id"):
        return redirect("showportfolio")

    context = base()
    return render(request, "login.html", context)

def fetchregisterdata(request):

    fullname = request.POST.get("fullname")
    email = request.POST.get("email")
    raw_password = request.POST.get("password")
    confirm_password = request.POST.get("confirmpassword")
    phone = request.POST.get("phone")
    identyCard = request.FILES.get("Identy_Card")

    if raw_password != confirm_password:
        messages.error(request, "Passwords do not match.")
        return redirect("registerpage")

    # Public registration = CLIENT only
    role = "client"

    insertquery = registermodel(
        fullname=fullname,
        email=email,
        password=make_password(raw_password),
        phone=phone,
        Identy_Card=identyCard,
        Role=role
    )

    insertquery.save()

    messages.success(request, "Registration successful. Please login.")

    return redirect("login")




# register and login is same or not check to email and password

def checklogindata(request):

    useremail = request.POST.get("email")
    userpassword = request.POST.get("password")

    try:
        userdata = registermodel.objects.get(email=useremail)

    except registermodel.DoesNotExist:

        messages.error(request, "Invalid email or password")
        return render(request, "login.html")


    # if check_password(userpassword, userdata.password):

    #     request.session["log_id"] = userdata.id
    #     request.session["log_name"] = userdata.fullname
    #     request.session["log_email"] = userdata.email
    #     request.session["log_role"] = userdata.Role

    #     django_user = User.objects.filter(email=userdata.email).first()

    #     if not django_user:
    #         django_user = User.objects.create_user(
    #             username=userdata.email,
    #             email=userdata.email,
    #             first_name=userdata.fullname,
    #         )

    #     login(request, django_user)
    #     print("Login Successful")
    #     print("REGISTERMODEL ID:", userdata.id)
    #     print("DJANGO USER ID:", django_user.id)
    #     print("DJANGO USERNAME:", django_user.username)

    #     return redirect("showportfolio")

    if check_password(userpassword, userdata.password):

        request.session["log_id"] = userdata.id
        request.session["log_name"] = userdata.fullname
        request.session["log_email"] = userdata.email
        request.session["log_role"] = userdata.Role

        print("BEFORE DJANGO LOGIN:")
        print("log_id:", request.session.get("log_id"))
        print("log_name:", request.session.get("log_name"))
        print("log_email:", request.session.get("log_email"))
        print("log_role:", request.session.get("log_role"))

        django_user = User.objects.filter(email=userdata.email).first()

        if not django_user:
            django_user = User.objects.create_user(
                username=userdata.email,
                email=userdata.email,
                first_name=userdata.fullname,
            )

        login(request, django_user)

        print("AFTER DJANGO LOGIN:")
        print("log_id:", request.session.get("log_id"))
        print("log_name:", request.session.get("log_name"))
        print("log_email:", request.session.get("log_email"))
        print("log_role:", request.session.get("log_role"))

        print("AUTHENTICATED:", request.user.is_authenticated)

        return redirect("showportfolio")

    else:

        messages.error(request, "Invalid email or password")
        return render(request, "login.html")

def logout(request):
    django_logout(request)
    request.session.flush()

    return redirect("index")


def indexpage(request):
    context = base()
    print(context)
    return render(request, "index.html", context)


def aboutpage(request):
    context = base()
    print(context)
    return render(request, "about.html", context)


def Residentialpage(request):
    context = base()
    print(context)
    return render(request, "Residential.html", context)


def Commercialpage(request):
    context = base()
    print(context)
    return render(request, "Commercial.html", context)


@role_required("designer", "admin")
def addportfoliopage(request):
    context = base()
    print(context)
    return render(request, "addportfolio.html", context)


@role_required("designer", "admin")
def fetchportfoliodata(request):
    # fetch portfolio data
    Designer_Name = request.POST.get("Designer_Name")
    aboutyourself = request.POST.get("about")
    designstyle = request.POST.get("Design_style")
    designerskill = request.POST.get("skills")
    experience = request.POST.get("experience")
    sampleimage = request.FILES["work-upload"]

    # fetch sellerid from session variable
    Designerid = request.session["log_id"]

    # print portfolio data
    print("desinger name=", Designer_Name)
    print("aboutyourself=", aboutyourself)
    print("designstyle=", designstyle)
    print("category=", category)
    print("designerskill=", designerskill)
    print("experience=", experience)
    print("sampleimages", sampleimage)

    # query to store data into portfolio model

    insertquery = portfolio(Designer_Name=Designer_Name, aboutyourself=aboutyourself,
                            designstyle=Portfoliocategory(id=designstyle),
                            designerskill=designerskill, experience=experience, sampleimage=sampleimage,
                            Designerid=registermodel(id=Designerid))
    insertquery.save()
    messages.success(request, "Portfolio added successfully")

    print("success")

    return render(request, "addportfolio.html")


@role_required("designer", "admin")
def edit_portfolio(request, portfolio_id):

    if request.session.get("log_role") == "admin":
        edit_portfolio = get_object_or_404(
            portfolio,
            id=portfolio_id
        )
    else:
        edit_portfolio = get_object_or_404(
            portfolio,
            id=portfolio_id,
            Designerid=request.session["log_id"]
        )

    design_styles = Portfoliocategory.objects.all()

    return render(
        request,
        "editportfolio.html",
        {
            "edit_portfolio": edit_portfolio,
            "design_styles": design_styles,
        }
    )

@role_required("designer", "admin")
def update_portfolio(request, portfolio_id):

    if request.session.get("log_role") == "admin":

        edit_portfolio = get_object_or_404(
            portfolio,
            id=portfolio_id
        )

    else:

        edit_portfolio = get_object_or_404(
            portfolio,
            id=portfolio_id,
            Designerid=request.session["log_id"]
        )

    if request.method == "POST":

        edit_portfolio.Designer_Name = request.POST.get("Designer_Name")
        edit_portfolio.aboutyourself = request.POST.get("about")

        edit_portfolio.designstyle = get_object_or_404(
            Portfoliocategory,
            id=request.POST.get("Design_style")
        )

        edit_portfolio.category = request.POST.get("Category")
        edit_portfolio.designerskill = request.POST.get("skills")
        edit_portfolio.experience = request.POST.get("experience")

        if "work-upload" in request.FILES:
            edit_portfolio.sampleimage = request.FILES["work-upload"]

        edit_portfolio.save()

        messages.success(
            request,
            "Portfolio updated successfully!"
        )

        return redirect("manageportfolio")

    return render(
        request,
        "editportfolio.html",
        {
            "edit_portfolio": edit_portfolio
        }
    )

def showportfoliopage(request):
    # fetch portfolio data
    fetchportfolio = portfolio.objects.all()
    context = base()
    context.update({
        "Portfolio": fetchportfolio,
    })
    return render(request, "showportfolio.html", context)


def singleportfoliopage(request, id):
    # query to fetch single product data

    singledata = portfolio.objects.get(id=id)
    fetchdata = category.objects.all()
    context = base()
    context.update({
        "data": singledata,
        "category": fetchdata,
    })
    return render(request, "singleportfolio.html", context)


def categorywiseportfolio(request, id):
    fetchdata = portfolio.objects.filter(designstyle=id)
    fetchcatdata = category.objects.all()
    context = base()
    context.update({
        "data": fetchdata,
        "category": fetchcatdata,
    })
    return render(request, "categorywiseprotfolio.html", context)


@role_required("designer", "admin")
def manageportfoliopage(request):

    if request.session.get("log_role") == "admin":
        fetchdata = portfolio.objects.all()

    else:
        fetchdata = portfolio.objects.filter(
            Designerid=request.session["log_id"]
        )

    context = {"data": fetchdata,}

    return render(request,"manageportfolio.html",context)

@role_required("designer", "admin")
def deleteportfolio(request, id):

    if request.session.get("log_role") == "admin":

        portfolio_data = get_object_or_404(
            portfolio,
            id=id
        )

    else:

        portfolio_data = get_object_or_404(
            portfolio,
            id=id,
            Designerid=request.session["log_id"]
        )

    portfolio_data.delete()

    messages.success(
        request,
        "Portfolio deleted successfully."
    )

    return redirect("manageportfolio")

@role_required("designer", "admin")
def addpackagepage(request):
    context = base()
    return render(request, "addpackage.html", context)


@role_required("designer", "admin")
def fetchpackagedata(request):  # insert data into  packagemodel
    # fetch package data
    context = base()
    Designer_Name = request.POST.get("Designer_Name")
    packagetype = request.POST.get("Package-type")
    designstyle = request.POST.get("Design_style")
    packagecategory = request.POST.get("category")
    BhkType = request.POST.get("bhkType")
    price = request.POST.get("price")
    timeduration = request.POST.get("duration")
    desc = request.POST.get("Package-desc")
    packageimg = request.FILES["Package-Images"]
    ExtraServices = request.POST.getlist("services[]")

    # fetch sellerid from session variable
    Designerid = request.session["log_id"]

    # print package data
    print("Designer Name", Designer_Name)
    print("packagetype=", packagetype)
    print("pakage design style=", designstyle)
    print("package category =", packagecategory)
    print("bhkType=", BhkType)
    print("price=", price)
    print("Time Duration=", timeduration)
    print("description=", desc)
    print("package image=", packageimg)
    print("services", ExtraServices)

    # query to store data into package model
    insertquery = packages(Designer_Name=Designer_Name, package_type=Packagecategory(id=packagetype),
                           package_design_style=designstyle, package_category=packagecategory, BhkType=BhkType,
                           package_price=price, time_duration=timeduration, package_desc=desc, package_img=packageimg,
                           ExtraServices=ExtraServices, Designerid=registermodel(id=Designerid))
    insertquery.save()
    messages.success(request, "Package added successfully")

    print("data is inserted ")
    return render(request, "addpackage.html", context)

@role_required("designer", "admin")
def mypackages(request):
    uid = request.session["log_id"]
    # fetch package data
    context = base()
    fetchpackages = packages.objects.filter(Designerid=uid)  # package is a model name

    context.update({
        "packages": fetchpackages,
        # "category": fetchcategory,
    })

    return render(request, "showpackage.html", context)

@role_required("designer", "admin")
def myportfolios(request):
    uid = request.session["log_id"]
    # fetch package data
    context = base()
    fetchpackages = portfolio.objects.filter(Designerid=uid)  # package is a model name

    context.update({
        "Portfolio": fetchpackages,
    })

    return render(request, "showportfolio.html", context)


def showpackage(request):
    # fetch package data
    context = base()
    fetchpackages = packages.objects.all()  # package is a model name
    # fetchcategory = category.objects.all()
    context.update({
        "packages": fetchpackages,
        # "category": fetchcategory,
    })

    return render(request, "showpackage.html", context)






def singlepackagepage(request, id):
    context = base()
    # quary to fetch single package data
    singledata = packages.objects.get(
        id=id)  # package is a model name and id is required in a any one package differt id's are there
    fetchdata = category.objects.all()
    context.update({
        "data": singledata,
        "category": fetchdata,
    })
    print(context)
    return render(request, "singlepackage.html", context)


def categorywisepackagepage(request, id):
    # Quary to fetch products according to category
    fetchdata = packages.objects.filter(package_type=id)
    fetchcatdata = Packagecategory.objects.all()
    context = base()
    context.update({
        "data": fetchdata,
        "category": fetchcatdata,
    })
    return render(request, "categorywisepackage.html", context)


@role_required("designer", "admin")
def managepackagepage(request):

    if request.session.get("log_role") == "admin":

        fetchdata = packages.objects.all()

    else:

        fetchdata = packages.objects.filter(
            Designerid=request.session["log_id"]
        )

    context = {
        "data": fetchdata,
    }

    return render(
        request,
        "managepackage.html",
        context
    )

@role_required("designer", "admin")
def deletepackage(request, id):
    context = base()
    print(context)
    print(id)

    # delete from package where id=id
    packages.objects.get(id=id).delete()

    messages.success(request, "Package deleted successfully.")
    return redirect("/managepackage",context)

@role_required("designer", "admin")
def edit_package(request, package_id):

    if request.session.get("log_role") == "admin":

        package = get_object_or_404(
            packages,
            id=package_id
        )

    else:

        package = get_object_or_404(
            packages,
            id=package_id,
            Designerid=request.session["log_id"]
        )

    if request.method == "POST":

        package.Designer_Name = request.POST.get("Designer_Name")

        package.package_type = get_object_or_404(
            Packagecategory,
            id=request.POST.get("Package-type")
        )

        package.package_design_style = request.POST.get(
            "Design_style"
        )

        package.package_category = request.POST.get(
            "category"
        )

        package.BhkType = request.POST.get(
            "bhkType"
        )

        package.package_price = request.POST.get(
            "price"
        )

        package.time_duration = request.POST.get(
            "duration"
        )

        package.package_desc = request.POST.get(
            "Package-desc"
        )

        if "Package-Images" in request.FILES:
            package.package_img = request.FILES[
                "Package-Images"
            ]

        package.ExtraServices = request.POST.getlist(
            "services"
        )

        package.save()

        messages.success(
            request,
            "Package updated successfully"
        )

        return redirect("managepackage")

    return render(
        request,
        "editpackage.html",
        {
            "editpackage": package
        }
    )

@role_required("client")
def bookingpage(request, pack_id):
    context = base()
    packagesdetails = packages.objects.get(id=pack_id)
    context.update({
        "data": packagesdetails
    })
    print(context)
    return render(request, "booking.html", context)



# Initialize Razorpay client
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


@role_required("client")
def featchbooking(request):

    context = base()

    if request.method == "POST":

        package_id = request.POST.get("package_id")

        package = get_object_or_404(
            packages,
            id=package_id
        )

        client = get_object_or_404(
            registermodel,
            id=request.session["log_id"]
        )

        Client_Name = request.POST.get("Client_Name")
        packagetype = request.POST.get("Package-type")
        designstyle = request.POST.get("Design_style")
        packagecategory = request.POST.get("category")
        datetime = request.POST.get("date")
        location = request.POST.get("location")
        BHKType = request.POST.get("bhkType")
        propertySize = request.POST.get("propertySize")
        Time_duration = request.POST.get("Time_duration")
        requirment = request.POST.get("requirement")
        services = request.POST.getlist("services")
        total_package = request.POST.get("total_price")

        half_payment = float(total_package) / 2

        insertquery = booking(
            client_id=client,
            Client_Name=Client_Name,
            package_type=packagetype,
            design_style=designstyle,
            totalamount=total_package,
            package_category=packagecategory,
            date_time=datetime,
            location=location,
            BHKType=BHKType,
            propertySize=propertySize,
            Time_duration=Time_duration,
            status="Pending",
            requirement=requirment,
            services=",".join(services),
            package_id=package
        )

        insertquery.save()

        order_data = {
            "amount": int(half_payment * 100),
            "currency": "INR",
            "receipt": str(insertquery.id),
            "payment_capture": 1
        }

        razorpay_order = razorpay_client.order.create(
            order_data
        )

        payment = Payment(
            booking=insertquery,
            razorpay_order_id=razorpay_order["id"],
            amount=half_payment,
            status="Pending"
        )

        payment.save()

        return redirect(
            "payment_page",
            order_id=razorpay_order["id"]
        )

    return render(
        request,
        "booking.html",
        context
    )

@role_required("client", "admin")
def payment_history(request):

    context = base()

    if request.session.get("log_role") == "admin":

        payments = Payment.objects.all()

    else:

        payments = Payment.objects.filter(
            booking__client_id=request.session["log_id"]
        )

    context.update({
        "payments": payments
    })

    return render(
        request,
        "paymenthistory.html",
        context
    )

@role_required("client")
def managebookingpage(request):

    context = base()

    fetchdata = booking.objects.filter(
        client_id=request.session["log_id"]
    )

    context.update({
        "data": fetchdata,
    })

    return render(
        request,
        "managebooking.html",
        context
    )

@role_required("designer", "admin")
def desmanagebookingpage(request):
    context = base()
    client_id_loggedin = request.session["log_id"]
    fetchdata = booking.objects.filter(package_id__Designerid__id=client_id_loggedin)
    print(fetchdata)
    context = {
        "data": fetchdata,
    }

    return render(request, "managebooking.html", context)

@role_required("client")
def insertintobooking(request):
    context = base()
    print(context)
    package_id = request.POST.get("package_id")
    price = request.POST.get("price")
    quantity = request.POST.get("quantity")

    client_id = request.session["log_id"]
    totalamount = int(quantity) * float(price)

    try:
        fetchdata = booking.objects.get(client_id=client_id, package_id=package_id, bookingid=1)
    except:
        fetchdata = None

        if fetchdata is not None:
            fetchdata.quantity += int(quantity)
            fetchdata.total += int(totalamount)
            fetchdata.save()
        else:
            insertquery = booking(client_id=registermodel(id=client_id), package_id=packages(id=package_id),
                                  quantity=quantity, totalamount=totalamount, bookingstatus=1, bookingid=0)
            insertquery.save()
    return redirect("Booking.html",context)

@role_required("designer", "admin")
def showbooking(request):
    client_id = request.session["log_id"]
    fetchdata = booking.objects.filter(client_id=client_id)
    context = {
        "data": fetchdata,
    }

    return render(request, "booking.html", context)


@role_required("client", "admin")
def cancelbooking(request, id):

    if request.session.get("log_role") == "admin":

        bookingdata = get_object_or_404(
            booking,
            id=id
        )

    else:

        bookingdata = get_object_or_404(
            booking,
            id=id,
            client_id=request.session["log_id"]
        )

    bookingdata.status = "canceled"
    bookingdata.save(update_fields=["status"])

    messages.success(
        request,
        "Booking canceled successfully."
    )

    return redirect("managebooking")

def contactpage(request):
    context = base()
    print(context)
    return render(request, "contact.html", context)


def fetchcontactdata(request):  # fetch contact data
    name = request.POST.get("name")
    email = request.POST.get("email")
    subject = request.POST.get("subject")
    phoneno = request.POST.get("mno")
    message = request.POST.get("message")

    print("fullname=", name)
    print("email=", email)
    print("subject=", subject)
    print("phone number=", phoneno)
    print("message=", message)

    insertquery = contact(name=name, email=email, subject=subject, phone_number=phoneno, message=message)
    insertquery.save()
    messages.success(request, "contact added successfully")

    print("data is inserted ")
    return render(request, "contact.html")


def full_image_view(request, package_id):
    context = base()
    print(context)
    package = get_object_or_404(packages, id=package_id)  # Correct way to fetch the package
    return render(request, 'full_image.html', {'package': package},context)  # Use singular name

@role_required("client")
def reviewpage(request):
    context = base()
    print(context)
    return render(request, "Review.html",context)


@role_required("client")
def fetchreviewdata(request):

    context = base()

    if request.method == "POST":

        name = request.POST.get("name")
        star = request.POST.get("star")
        review_text = request.POST.get("review")

        client = get_object_or_404(
            registermodel,
            id=request.session["log_id"]
        )

        insertquery = review(
            client_id=client,
            name=name,
            star=int(star),
            review=review_text
        )

        insertquery.save()

        messages.success(
            request,
            "Review submitted successfully!"
        )

    return render(
        request,
        "Review.html",
        context
    )

@role_required("client")
def managereviewpage(request):
    client_id_loggedin = request.session["log_id"]
    fetchdata = review.objects.filter(client_id=client_id_loggedin)
    context = {
        "data": fetchdata,
    }

    return render(request, "managereview.html", context)


def thankyoupage(request):
    context = base()
    print(context)
    return render(request, "thankyoupage.html")


@csrf_exempt
@role_required("client")
def payment_success(request):
    if request.method == "POST":
        order_id = request.POST.get("razorpay_order_id")

        try:
            payment = Payment.objects.get(razorpay_order_id=order_id)
            params = {
                'razorpay_order_id': order_id,
            }

            # Verify payment signature
            payment.status = "Completed"
            payment.save()

            # Update booking status
            payment.booking.status = "Confirmed"
            payment.booking.save()

            messages.success(request, "Payment successful! Booking confirmed.")
            return redirect("featchbooking")  # Redirect to booking page or confirmation page

        except Payment.DoesNotExist:
            messages.error(request, "Payment record not found.")
            return redirect("featchbooking")

    return JsonResponse({"error": "Invalid request"}, status=400)

@role_required("client")
def payment_page(request, order_id):
    try:
        payment = Payment.objects.get(razorpay_order_id=order_id)
    except Payment.DoesNotExist:
        messages.error(request, "Invalid payment request.")
        return redirect("featchbooking")

    context = {
        "order_id": payment.razorpay_order_id,
        "amount": int(payment.amount * 100),
        "finalamount": int(payment.amount),  # Convert to paisa
        "key": settings.RAZORPAY_KEY_ID,  # Your Razorpay Key
    }
    return render(request, "payment_page.html", context)


def forgot_password(request):

    if request.method == "POST":

        email = request.POST.get("email")

        try:
            user = registermodel.objects.get(email=email)

        except registermodel.DoesNotExist:
            messages.error(request, "Email not registered")
            return redirect("forgot_password")

        otp = str(random.randint(100000, 999999))

        user.reset_otp = otp
        user.otp_created_at = timezone.now()
        user.save()

        send_mail(
            "Password Reset OTP",
            f"Your OTP is: {otp}\n\nThis OTP is valid for 5 minutes.",
            "modidev747@gmail.com",
            [email],
            fail_silently=False,
        )

        request.session["reset_email"] = email

        messages.success(request, "OTP sent successfully")

        return redirect("verify_otp")

    return render(request, "forgotpassword.html")


def verify_otp(request):

    email = request.session.get("reset_email")

    if not email:
        return redirect("forgot_password")

    user = registermodel.objects.get(email=email)

    if request.method == "POST":

        otp = request.POST.get("otp")

        if user.reset_otp != otp:
            messages.error(request, "Invalid OTP")
            return redirect("verify_otp")

        if timezone.now() > user.otp_created_at + timedelta(minutes=5):
            messages.error(request, "OTP expired")
            return redirect("forgot_password")

        request.session["otp_verified"] = True

        return redirect("new_password")

    return render(request, "verifyotp.html")

def new_password(request):

    if not request.session.get("otp_verified"):
        return redirect("forgot_password")

    email = request.session.get("reset_email")

    user = registermodel.objects.get(email=email)

    if request.method == "POST":

        password = request.POST.get("password")
        confirm = request.POST.get("confirm")

        if password != confirm:
            messages.error(request, "Passwords do not match")
            return redirect("new_password")

        user.password = make_password(password)
        user.reset_otp = None
        user.otp_created_at = None
        user.save()

        request.session.flush()

        messages.success(request, "Password changed successfully")

        return redirect("login")

    return render(request, "resetpassword.html")

def reset_password(request, uidb64, token):

    try:

        uid = urlsafe_base64_decode(
            uidb64
        ).decode()


        user = registermodel.objects.get(
            id=uid
        )


    except:

        user = None



    if user and default_token_generator.check_token(
        user,
        token
    ):


        if request.method == "POST":

            password = request.POST.get(
                "password"
            )


            user.password = make_password(
                password
            )


            user.save()


            messages.success(
                request,
                "Password changed successfully"
            )


            return redirect("login")



        return render(
            request,
            "resetpassword.html"
        )



    messages.error(
        request,
        "Invalid link"
    )

    return redirect(
        "forgot_password"
    )

def showreview(request):
    context = base()

    # Only prefetch client_id, not package (since it's not in your model)
    fetchreview = review.objects.select_related('client_id').all()

    # Optional: add a range for star rating display (like ⭐⭐⭐⭐)
    for r in fetchreview:
        r.star_range = range(r.star)

    context.update({
        "reviews": fetchreview,
    })

    return render(request, "showreview.html",context)

@role_required("client", "admin")
def ai_room_designer(request):

    if 'log_id' not in request.session:
        return redirect("login")

    if request.method == "POST":

        room_image = request.FILES.get("room_image")
        room_type = request.POST.get("room_type")
        design_style = request.POST.get("design_style")
        prompt = request.POST.get("prompt")
        color_theme = request.POST.get("color_theme")
        lighting = request.POST.get("lighting")
        budget = request.POST.get("budget")

        print("========== AI ROOM DESIGN ==========")
        print("Image:", room_image)
        print("Room Type:", room_type)
        print("Design Style:", design_style)
        print("Prompt:", prompt)
        print("User ID:", request.session["log_id"])
        print("====================================")

        if not room_image:

            messages.error(
                request,
                "Please upload an image of your room."
            )

            return redirect("ai_room_designer")

        design = None

        try:

            client = registermodel.objects.get(
                id=request.session["log_id"]
            )

            # Create database record
            design = AIRoomDesign.objects.create(
                client=client,
                original_image=room_image,
                room_type=room_type,
                design_style=design_style,
                color_theme=color_theme,
                lighting=lighting,
                budget=budget,
                prompt=prompt,
                status="processing",
                version=1,
                parent_design=None,
            )

            print("Design saved successfully!")
            print("Design ID:", design.id)

            # Generate image
            generated_image = generate_room_design(design)

            # Convert base64 → bytes
            image_bytes = base64.b64decode(
                generated_image
            )

            # Save generated image
            design.generated_image.save(
                f"room_design_{design.id}.png",
                ContentFile(image_bytes),
                save=False
            )

            design.status = "completed"

            design.save()

            print("====================================")
            print("AI DESIGN COMPLETED")
            print("Design ID:", design.id)
            print(
                "Generated:",
                design.generated_image.name
            )
            print("====================================")

            messages.success(
                request,
                "Your room design has been generated successfully!"
            )

            return redirect(
                "ai_room_result",
                design_id=design.id
            )

        except Exception as e:

            print("====================================")
            print("AI GENERATION ERROR")
            print(e)
            print("====================================")

            if design:

                design.status = "failed"

                design.save(
                    update_fields=["status"]
                )

            messages.error(
                request,
                "AI generation failed. Please try again."
            )

            return redirect("ai_room_designer")

    return render(
        request,
        "ai_room_designer.html"
    )

# def ai_room_result(request, design_id):

#     if 'log_id' not in request.session:
#         return redirect("login")

#     print("RESULT DESIGN ID:", design_id)
#     print("SESSION LOG ID:", request.session.get("log_id"))

#     design = AIRoomDesign.objects.get(
#         id=design_id,
#         client_id=request.session["log_id"]
#     )

#     versions = design.design_versions.all()

#     return render(
#         request,
#         "ai_room_result.html",
#         {
#             "design": design,
#             "versions": versions,
#         }
#     )

@role_required("client", "admin")
def ai_room_result(request, design_id):

    # Get the requested design with ownership protection
    if request.session.get("log_role") == "admin":
        design = get_object_or_404(
            AIRoomDesign,
            id=design_id
        )
    else:
        design = get_object_or_404(
            AIRoomDesign,
            id=design_id,
            client_id=request.session["log_id"]
        )

    # Find the root/original design
    root_design = design

    while root_design.parent_design:
        root_design = root_design.parent_design

    # Get all versions belonging to this design
    versions = AIRoomDesign.objects.filter(
        Q(id=root_design.id) |
        Q(parent_design=root_design)
    ).order_by("version")

    return render(request, "ai_room_result.html", {
        "design": design,
        "versions": versions,
        "root_design": root_design,
    })

@role_required("client", "admin")
def ai_room_history(request):

    if 'log_id' not in request.session:
        return redirect("login")
    
    print("HISTORY LOG ID:", request.session["log_id"])

    designs = AIRoomDesign.objects.filter(
        client_id=request.session["log_id"]
    ).order_by("-created_at")

    return render(
        request,
        "ai_room_history.html",
        {
            "designs": designs
        }
    )

@role_required("client", "admin")
def ai_room_edit(request, design_id):

    if request.session.get("log_role") == "admin":
        old_design = get_object_or_404(
            AIRoomDesign,
            id=design_id
        )
    else:
        old_design = get_object_or_404(
            AIRoomDesign,
            id=design_id,
            client_id=request.session["log_id"]
        )

    if request.method == "POST":

        edit_prompt = request.POST.get(
            "edit_prompt",
            ""
        ).strip()

        if not edit_prompt:
            messages.error(
                request,
                "Please enter what you want to change."
            )
            return redirect(
                "ai_room_edit",
                design_id=design_id
            )

        # -----------------------------------------
        # FIND ROOT DESIGN
        # -----------------------------------------

        root_design = old_design

        while root_design.parent_design:
            root_design = root_design.parent_design

        # -----------------------------------------
        # FIND NEXT VERSION
        # -----------------------------------------

        last_version = AIRoomDesign.objects.filter(
            parent_design=root_design
        ).order_by("-version").first()

        if last_version:
            next_version = last_version.version + 1
        else:
            next_version = old_design.version + 1

        # -----------------------------------------
        # CREATE NEW DESIGN VERSION
        # -----------------------------------------

        new_design = AIRoomDesign.objects.create(
            client=old_design.client,
            original_image=old_design.original_image,
            room_type=old_design.room_type,
            room_size=old_design.room_size,
            design_style=old_design.design_style,
            color_theme=old_design.color_theme,
            lighting=old_design.lighting,
            budget=old_design.budget,
            prompt=edit_prompt,
            status="processing",
            parent_design=root_design,
            version=next_version
        )

        try:

            # -----------------------------------------
            # GENERATE NEW IMAGE
            # -----------------------------------------

            image_base64 = generate_room_design(new_design)

            # -----------------------------------------
            # SAVE GENERATED IMAGE
            # -----------------------------------------

            image_data = base64.b64decode(image_base64)

            new_design.generated_image.save(
                f"room_design_{new_design.id}.png",
                ContentFile(image_data),
                save=False
            )

            # -----------------------------------------
            # MARK AS COMPLETED
            # -----------------------------------------

            new_design.status = "completed"

            new_design.save()

            messages.success(
                request,
                "Your room design has been updated successfully."
            )

            return redirect(
                "ai_room_result",
                design_id=new_design.id
            )

        except Exception as e:

            print("====================================")
            print("AI EDIT GENERATION ERROR")
            print(str(e))
            print("====================================")

            new_design.status = "failed"
            new_design.save(update_fields=["status"])

            messages.error(
                request,
                "Unable to generate the updated room design."
            )

            return redirect(
                "ai_room_edit",
                design_id=design_id
            )

    return render(request, "ai_room_edit.html", {
        "design": old_design
    })

# def ai_room_edit(request, design_id):

#     if 'log_id' not in request.session:
#         return redirect("login")

#     # ==========================================
#     # GET CURRENT DESIGN
#     # ==========================================

#     old_design = get_object_or_404(
#         AIRoomDesign,
#         id=design_id,
#         client_id=request.session["log_id"]
#     )

#     # ==========================================
#     # POST
#     # ==========================================

#     if request.method == "POST":

#         edit_prompt = request.POST.get(
#             "edit_prompt",
#             ""
#         ).strip()

#         if not edit_prompt:

#             messages.error(
#                 request,
#                 "Please enter what you want to change."
#             )

#             return redirect(
#                 "ai_room_edit",
#                 design_id=design_id
#             )

#         # ==========================================
#         # FIND ROOT DESIGN
#         # ==========================================

#         root_design = old_design

#         while root_design.parent_design:

#             root_design = root_design.parent_design

#         # ==========================================
#         # FIND NEXT VERSION
#         # ==========================================

#         last_version = AIRoomDesign.objects.filter(
#             parent_design=root_design
#         ).order_by("-version").first()

#         if last_version:

#             next_version = last_version.version + 1

#         else:

#             next_version = old_design.version + 1

#         # ==========================================
#         # CREATE NEW VERSION
#         # ==========================================

#         new_design = AIRoomDesign.objects.create(

#             client=old_design.client,

#             # Keep original room image
#             original_image=old_design.original_image,

#             room_type=old_design.room_type,

#             design_style=old_design.design_style,

#             color_theme=old_design.color_theme,

#             lighting=old_design.lighting,

#             budget=old_design.budget,

#             prompt=edit_prompt,

#             status="processing",

#             # ======================================
#             # VERSIONING
#             # ======================================

#             parent_design=root_design,

#             version=next_version
#         )

#         print("====================================")
#         print("AI VERSION GENERATION")
#         print("Root Design:", root_design.id)
#         print("Old Design:", old_design.id)
#         print("New Design:", new_design.id)
#         print("Version:", next_version)
#         print("Edit Prompt:", edit_prompt)
#         print("====================================")

#         try:

#             # ==========================================
#             # GENERATE IMAGE
#             # ==========================================

#             generated_image = generate_room_design(
#                 new_design
#             )

#             print(
#                 "AI image generated successfully"
#             )

#             # ==========================================
#             # BASE64 → BYTES
#             # ==========================================

#             image_bytes = base64.b64decode(
#                 generated_image
#             )

#             # ==========================================
#             # SAVE IMAGE
#             # ==========================================

#             new_design.generated_image.save(

#                 f"room_design_{new_design.id}.png",

#                 ContentFile(image_bytes),

#                 save=False
#             )

#             # ==========================================
#             # COMPLETE
#             # ==========================================

#             new_design.status = "completed"

#             new_design.save()

#             print("====================================")
#             print("AI VERSION COMPLETED")
#             print("Design ID:", new_design.id)
#             print("Version:", new_design.version)
#             print(
#                 "Generated:",
#                 new_design.generated_image.name
#             )
#             print("====================================")

#             messages.success(
#                 request,
#                 f"Design version {new_design.version} created successfully!"
#             )

#             return redirect(
#                 "ai_room_result",
#                 design_id=new_design.id
#             )

#         except Exception as e:

#             print("====================================")
#             print("AI VERSION ERROR")
#             print(e)
#             print("====================================")

#             new_design.status = "failed"

#             new_design.save(
#                 update_fields=["status"]
#             )

#             messages.error(
#                 request,
#                 "AI generation failed. Please try again."
#             )

#             return redirect(
#                 "ai_room_result",
#                 design_id=new_design.id
#             )

#     # ==========================================
#     # GET EDIT PAGE
#     # ==========================================

#     return render(
#         request,
#         "ai_room_edit.html",
#         {
#             "design": old_design
#         }
#     )

@role_required("client")
def save_ai_design(request, design_id):

    design = get_object_or_404(
        AIRoomDesign,
        id=design_id,
        client_id=request.session["log_id"]
    )

    design.is_saved = not design.is_saved

    design.save(update_fields=["is_saved"])

    if design.is_saved:
        messages.success(
            request,
            "Design saved successfully!"
        )
    else:
        messages.success(
            request,
            "Design removed from saved designs."
        )

    return redirect(
        "ai_room_result",
        design_id=design.id
    )

# def save_ai_design(request, design_id):

#     if 'log_id' not in request.session:
#         return redirect("login")

#     design = get_object_or_404(
#         AIRoomDesign,
#         id=design_id,
#         client_id=request.session["log_id"]
#     )

#     design.is_saved = not design.is_saved

#     design.save(
#         update_fields=["is_saved"]
#     )

#     if design.is_saved:

#         messages.success(
#             request,
#             "Design saved successfully!"
#         )

#     else:

#         messages.success(
#             request,
#             "Design removed from saved designs."
#         )

#     return redirect(
#         "ai_room_result",
#         design_id=design.id
#     )

@role_required("client")
def ai_saved_designs(request):

    designs = AIRoomDesign.objects.filter(
        client_id=request.session["log_id"],
        is_saved=True
    ).order_by("-created_at")

    return render(
        request,
        "ai_saved_designs.html",
        {
            "designs": designs
        }
    )

# def ai_saved_designs(request):

#     if 'log_id' not in request.session:
#         return redirect("login")

#     designs = AIRoomDesign.objects.filter(
#         client_id=request.session["log_id"],
#         is_saved=True
#     ).order_by("-created_at")

#     return render(
#         request,
#         "ai_saved_designs.html",
#         {
#             "designs": designs
#         }
#     )

@role_required("client", "admin")
def ai_room_versions(request, design_id):

    if request.session.get("log_role") == "admin":
        design = get_object_or_404(
            AIRoomDesign,
            id=design_id
        )
    else:
        design = get_object_or_404(
            AIRoomDesign,
            id=design_id,
            client_id=request.session["log_id"]
        )

    root_design = design

    while root_design.parent_design:
        root_design = root_design.parent_design

    versions = AIRoomDesign.objects.filter(
        Q(id=root_design.id) |
        Q(parent_design=root_design)
    ).order_by("version")

    return render(request, "ai_room_versions.html", {
        "design": root_design,
        "versions": versions
    })

# def ai_room_versions(request, design_id):

#     if 'log_id' not in request.session:
#         return redirect("login")

#     design = get_object_or_404(
#         AIRoomDesign,
#         id=design_id,
#         client_id=request.session["log_id"]
#     )

#     # ==========================================
#     # FIND ROOT DESIGN
#     # ==========================================

#     root_design = design

#     while root_design.parent_design:

#         root_design = root_design.parent_design

#     # ==========================================
#     # GET ALL VERSIONS
#     # ==========================================

#     versions = AIRoomDesign.objects.filter(
#         Q(id=root_design.id) |
#         Q(parent_design=root_design)
#     ).order_by("version")

#     return render(
#         request,
#         "ai_room_versions.html",
#         {
#             "design": root_design,
#             "versions": versions
#         }
#     )

@role_required("client")
def delete_ai_design(request, design_id):

    if 'log_id' not in request.session:
        return redirect("login")

    design = get_object_or_404(
        AIRoomDesign,
        id=design_id,
        client_id=request.session["log_id"]
    )

    if request.method == "POST":

        design.delete()

        messages.success(
            request,
            "Design deleted successfully."
        )

        return redirect("ai_room_history")

    return redirect(
        "ai_room_history"
    )

@role_required("client", "admin")
def restore_design_version(request, design_id, version_id):

    if "log_id" not in request.session:
        return redirect("login")

    design = get_object_or_404(
        AIRoomDesign,
        id=design_id,
        client_id=request.session["log_id"]
    )

    version = get_object_or_404(
        DesignVersion,
        id=version_id,
        design=design
    )

    # ---------------------------------
    # 1. Backup current design
    # ---------------------------------

    max_version = design.design_versions.aggregate(
        max_version=Max("version")
    )["max_version"]

    next_version = (max_version or 0) + 1

    backup_version = DesignVersion.objects.create(
        design=design,
        version=next_version,
        room_type=design.room_type,
        room_size=None,
        design_style=design.design_style,
        color_theme=design.color_theme,
        lighting=design.lighting,
        budget=design.budget,
        design_plan=design.prompt,
    )

    # Backup current image
    if design.generated_image:

        with design.generated_image.open("rb") as image_file:

            backup_version.generated_image.save(
                f"version_{next_version}.png",
                ContentFile(image_file.read()),
                save=True
            )

    # ---------------------------------
    # 2. Restore selected version
    # ---------------------------------

    design.room_type = version.room_type
    design.design_style = version.design_style
    design.color_theme = version.color_theme
    design.lighting = version.lighting
    design.budget = version.budget

    design.prompt = version.design_plan

    if version.generated_image:
        design.generated_image = version.generated_image

    design.status = "completed"

    design.save()

    return redirect(
        "ai_room_result",
        design_id=design.id
    )
