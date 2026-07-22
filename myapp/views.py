from calendar import month
from os import remove

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import *


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
    context = base()
    print(context)
    return render(request, "Register.html", context)


def fetchregisterdata(request):  # insert data into model
    fullname = request.POST.get("fullname")
    email = request.POST.get("email")
    password = request.POST.get("password")
    confirmpassword = request.POST.get("confirmpassword")
    phone = request.POST.get("phone")
    identyCard = request.FILES["Identy_Card"]
    role = request.POST["role"]

    # from to varrible
    print("fullname=", fullname)
    print("email=", email)
    print("password=", password)
    print("confirmpassword=", confirmpassword)
    print("phone=", phone)
    print("identitycard=", identyCard)
    print("role", role)

    # varriable to database
    insertquery = registermodel(fullname=fullname, email=email, password=password, confirmpassword=confirmpassword,
                                phone=phone, Identy_Card=identyCard, Role=role)
    insertquery.save()  # saved to quary

    print("registerd")
    return render(request, "login.html")  # succesful register after rebder to login page


def loginpage(request):
    context = base()
    print(context)
    return render(request, "login.html", context)


# register and login is same or not check to email and password
def checklogindata(request):
    useremail = request.POST.get("email")
    userpassword = request.POST.get("password")

    print(useremail)
    print(userpassword)
    print("Success")
    # query to check data into model

    try:
        userdata = registermodel.objects.get(email=useremail, password=userpassword)  # select query
        print(userdata)
        print("success")

        # Store data into Session

        request.session["log_id"] = userdata.id  # Keyword after . is field name
        request.session["log_name"] = userdata.fullname
        request.session["log_email"] = userdata.email
        request.session["log_role"] = userdata.Role

        print("Session name=", request.session["log_name"])

    except:
        print("failure")
        userdata = None

        # navigation based on query result

    if userdata is not None:
        return redirect("showportfolio")  # Ensure "showpackage" is a named URL in urls.py

    # Authentication failed case
    print("Invalid email or password")
    messages.error(request, "Invalid email or password")

    return render(request, "login.html")


def logout(request):
    context = base()
    print(context)

    try:
        del request.session["log_id"]
        del request.session["log_name"]
        del request.session["log_email"]
        del request.session["log_role"]

    except:
        pass

    return render(request, "index.html", context)


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


def addportfoliopage(request):
    context = base()
    print(context)
    return render(request, "addportfolio.html", context)


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


def edit_portfolio(request, portfolio_id):
    edit_portfolio = get_object_or_404(portfolio, id=portfolio_id)

    # Fetch all portfolio categories for dropdowns
    design_styles = Portfoliocategory.objects.all()

    return render(request, "editportfolio.html", {
        "edit_portfolio": edit_portfolio,
        "design_styles": design_styles,
    })


def update_portfolio(request, portfolio_id):
    edit_portfolio = get_object_or_404(portfolio, id=portfolio_id)

    if request.method == "POST":
        edit_portfolio.Designer_Name = request.POST.get("Designer_Name")
        edit_portfolio.aboutyourself = request.POST.get("about")
        edit_portfolio.designstyle = Portfoliocategory.objects.get(id=request.POST.get("Design_style"))
        edit_portfolio.category = request.POST.get("Category")
        edit_portfolio.designerskill = request.POST.get("skills")
        edit_portfolio.experience = request.POST.get("experience")

        # If a new image is uploaded, update it
        if "work-upload" in request.FILES:
            edit_portfolio.sampleimage = request.FILES["work-upload"]

        edit_portfolio.save()
        messages.success(request, "Portfolio updated successfully!")

        return redirect(manageportfoliopage)

    return render(request, "editportfolio.html", {"edit_portfolio": edit_portfolio})


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


def manageportfoliopage(request):
    designer_id_loggedin = request.session["log_id"]
    fetchdata = portfolio.objects.filter(Designerid=designer_id_loggedin)
    context = {
        "data": fetchdata,
    }
    return render(request, "manageportfolio.html", context)


def deleteportfolio(request, id):
    context = base()
    print(context)
    print(id)

    # delete from portfolio where id=id
    portfolio.objects.get(id=id).delete()

    messages.success(request, "Portfolio deleted successfully.")
    return redirect("/manageportfolio",context)


def addpackagepage(request):
    context = base()
    return render(request, "addpackage.html", context)


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


def managepackagepage(request):
    designer_id_loggedin = request.session["log_id"]

    fetchdata = packages.objects.filter(Designerid=designer_id_loggedin)
    context = {
        "data": fetchdata,
    }
    return render(request, "managepackage.html", context)


def deletepackage(request, id):
    context = base()
    print(context)
    print(id)

    # delete from package where id=id
    packages.objects.get(id=id).delete()

    messages.success(request, "Package deleted successfully.")
    return redirect("/managepackage",context)


def bookingpage(request, pack_id):
    context = base()
    packagesdetails = packages.objects.get(id=pack_id)
    context.update({
        "data": packagesdetails
    })
    print(context)
    return render(request, "booking.html", context)


from django.shortcuts import render, redirect
from django.contrib import messages
from .models import booking, packages, Payment
import razorpay
from django.conf import settings

# Initialize Razorpay client
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


def featchbooking(request):
    context = base()
    if request.method == "POST":
        # Fetch package data
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
        package_id = request.POST.get("package_id")
        total_package = request.POST.get("total_price")

        package = packages.objects.get(id=package_id)
        half_payment = float(total_package) / 2  # Calculate 50% payment

        # Insert booking
        insertquery = booking(Client_Name=Client_Name, package_type=packagetype, design_style=designstyle,
                              totalamount=total_package,
                              package_category=packagecategory, date_time=datetime, location=location,
                              BHKType=BHKType, propertySize=propertySize, Time_duration=Time_duration,
                              status="Pending", requirement=requirment, services=",".join(services), package_id=package)
        insertquery.save()

        # Create Razorpay Order
        order_data = {
            "amount": int(half_payment * 100),  # Convert to paisa
            "currency": "INR",
            "receipt": str(insertquery.id),
            "payment_capture": 1  # Auto capture payment
        }
        razorpay_order = razorpay_client.order.create(order_data)

        # Save payment record
        payment = Payment(booking=insertquery, razorpay_order_id=razorpay_order['id'], amount=half_payment,
                          status="Pending")
        payment.save()

        return redirect("payment_page", order_id=razorpay_order['id'])

    return render(request, "booking.html", context)


def payment_history(request):
    context = base()
    payments = Payment.objects.filter(booking__Client_Name=request.session["log_name"])  # Filter payments for this user
    context.update({'payments': payments})
    return render(request, 'paymenthistory.html', context)


def managebookingpage(request):
    context = base()

    fetchdata = booking.objects.filter(Client_Name=request.session["log_name"])
    print(fetchdata)
    context.update({
        "data": fetchdata,
    })

    return render(request, "managebooking.html", context)


def desmanagebookingpage(request):
    context = base()
    client_id_loggedin = request.session["log_id"]
    fetchdata = booking.objects.filter(package_id__Designerid__id=client_id_loggedin)
    print(fetchdata)
    context = {
        "data": fetchdata,
    }

    return render(request, "managebooking.html", context)


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


def showbooking(request):
    client_id = request.session["log_id"]
    fetchdata = booking.objects.filter(client_id=client_id)
    context = {
        "data": fetchdata,
    }

    return render(request, "booking.html", context)


def cancelbooking(request, id):
    context = base()
    bookingdata = booking.objects.get(id=id)
    bookingdata.status = "canceled"
    bookingdata.save()
    return redirect(indexpage)


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


def reviewpage(request):
    context = base()
    print(context)
    return render(request, "Review.html",context)


def fetchreviewdata(request):
    context = base()
    name = request.POST.get("name")
    star = request.POST.get("star")
    review_text = request.POST.get("review")  # ✅ Rename variable to avoid conflicts

    print(name)
    print(star)
    print(review_text)

    insertquery = review(name=name, star=int(star), review=review_text)  # ✅ Use correct model name
    insertquery.save()

    messages.success(request, "Review submitted successfully!")

    return render(request, "Review.html",context)


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


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
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


def edit_package(request, package_id):
    package = get_object_or_404(packages, id=package_id)

    if request.method == "POST":
        package.Designer_Name = request.POST.get("Designer_Name")
        package.package_type = Packagecategory.objects.get(id=request.POST.get("Package-type"))
        package.package_design_style = request.POST.get("Design_style")
        package.package_category = request.POST.get("category")
        package.BhkType = request.POST.get("bhkType")
        package.package_price = request.POST.get("price")
        package.time_duration = request.POST.get("duration")
        package.package_desc = request.POST.get("Package-desc")

        if "Package-Images" in request.FILES:
            package.package_img = request.FILES["Package-Images"]

        package.ExtraServices = request.POST.getlist("services")
        package.save()

        messages.success(request, "Package updated successfully")
        return redirect(managepackagepage)  # Redirect to a package list or detail page

    return render(request, "editpackage.html", {"editpackage": package})


def forgotpwd(request):
    context = base()
    print(context)
    return render(request, "forgotpassword.html",context)


def forgotpassword(request):
    if request.method == 'POST':
        username = request.POST.get('email')

        try:
            user = registermodel.objects.get(email=username)

        except registermodel.DoesNotExist:
            user = None

        if user is not None:
            #################### Password Generation ##########################
            import random
            letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's',
                       't', 'u', 'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L',
                       'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
            numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
            symbols = ['!', '#', '$', '%', '&', '(', ')', '*', '+']

            nr_letters = 6
            nr_symbols = 1
            nr_numbers = 3
            password_list = []

            for char in range(1, nr_letters + 1):
                password_list.append(random.choice(letters))

            for char in range(1, nr_symbols + 1):
                password_list += random.choice(symbols)

            for char in range(1, nr_numbers + 1):
                password_list += random.choice(numbers)

            print(password_list)
            random.shuffle(password_list)
            print(password_list)

            password = ""  # we will get final password in this var.
            for char in password_list:
                password += char

            ##############################################################

            msg = "hello here it is your new password  " + password  # this variable will be passed as message in mail

            ############ code for sending mail ########################

            from django.core.mail import send_mail

            send_mail(
                'Your New Password',
                msg,
                'modidev747@gmail.com',
                [username],
                fail_silently=False,
            )

            # now update the password in model
            cuser = registermodel.objects.get(email=username)
            cuser.password = password
            cuser.confirmpassword = password
            cuser.save(update_fields=['password'])

            print('Mail sent')
            messages.info(request, 'mail is sent successfully to your registered email')
            return redirect(indexpage)
        else:
            messages.info(request, 'This account does not exist')
    return redirect(indexpage)

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



