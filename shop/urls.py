from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path("signup/",views.signup, name="SignUp"),
    path("login/",views.handlelogin, name="Login"),
    path("logout/",views.handlelogout, name="Logout"),
    path('changepassword/', views.PasswordChange, name='ChangePassword'),
    path("",views.index, name="ShopHome"),
    path("about/",views.about, name="AboutUs"),
    path("contact/",views.contact, name="ContactUs"),
    path("tracker/",views.tracker, name="TrackingStatus"),
    path("search/",views.search, name="Search"),
    path("products/<int:myid>",views.productView, name="ProductView"),
    path("checkout/",views.checkout, name="Checkout"),
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)