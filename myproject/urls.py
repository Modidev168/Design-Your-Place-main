"""
URL configuration for myproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from myapp import views

urlpatterns = [
path("admin/", admin.site.urls),
    path("Register", views.registerpage),
    path("login", views.loginpage),
    path("forgotpwd", views.forgotpwd),
    path("forgotpassword", views.forgotpassword),
    path("logout",views.logout),
    path("fetchregisterdata", views.fetchregisterdata),
    path("checklogindata", views.checklogindata),
    path("",views.indexpage),
    path("about/",views.aboutpage),
    path("Residential",views.Residentialpage),
    path("Commercial",views.Commercialpage),
    path("addpackage",views.addpackagepage),
    path("fetchpackagedata",views.fetchpackagedata),
    path("showpackage",views.showpackage),
    path("mypackages",views.mypackages),
    path("singlepackage/<int:id>",views.singlepackagepage),
    path("categorywisepackage/<int:id>",views.categorywisepackagepage),
    path("managepackage",views.managepackagepage),
    path("deletepackage/<int:id>",views.deletepackage),
    path("addportfolio", views.addportfoliopage),
    path("fetchportfoliodata", views.fetchportfoliodata),
    path("showportfolio/", views.showportfoliopage,name='showportfolio'),
    path("singleportfolio/<int:id>", views.singleportfoliopage),
    path("categorywiseportfolio/<int:id>",views.categorywiseportfolio),
    path("myportfolios",views.myportfolios),
    path("manageportfolio",views.manageportfoliopage),
    path("deleteportfolio/<int:id>",views.deleteportfolio),
    path("contact",views.contactpage),
    path("fetchcontactdata",views.fetchcontactdata),
    path("booking/<int:pack_id>",views.bookingpage),
    path("featchbooking",views.featchbooking),
    path('payment-success/', views.payment_success, name='payment-success'),
    path('payment-page/<str:order_id>/', views.payment_page, name='payment_page'),
    path("managebooking",views.managebookingpage),
    path("managebookings",views.desmanagebookingpage),
    path("insertintobooking",views.insertintobooking),
    path('full_image/<int:package_id>/', views.full_image_view, name='full_image'),
    path("Review",views.reviewpage),
    path("fetchratingpagedata",views.fetchreviewdata),
    path("managereview",views.managereviewpage),
    path("thankyou",views.thankyoupage),
    path('payment-history', views.payment_history, name='payment_history'),
    path('edit-package/<int:package_id>/', views.edit_package, name='edit_package'),
    path('editportfolio/<int:portfolio_id>/', views.edit_portfolio, name='editportfolio'),
    path('updateportfolio/<int:portfolio_id>/', views.update_portfolio, name='updateportfolio'),
    path("cancelbooking/<int:id>", views.cancelbooking, name="cancelbooking"),
    path("ShowReview",views.showreview),

]+ static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
