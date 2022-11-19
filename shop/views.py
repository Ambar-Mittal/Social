from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, response
from .forms import ChangePasswordForm
from .models import Product, Contact, Order, OrderUpdate
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from math import ceil
import json

# Create your views here.
def signup(request):   
   if request.method=="POST":
      # Get the post parameters
      username=request.POST['username']
      email=request.POST['email']
      fname=request.POST['fname']
      lname=request.POST['lname']
      pass1=request.POST['password1']
      pass2=request.POST['password2']
      
      punctuations='''!()/[]{}:;'",<>/?\~`$^&%*-=+'''
      # check for errorneous input
      if len(username)> 20:
         messages.error(request,"Username must be under 20 characters!!")
         return redirect('SignUp')
      
      for char in username:
         if char in punctuations:
            messages.error(request,"Username should only contain letters and number!! ")
            return redirect('SignUp')

      if User.objects.filter(username=username).exists(): 
         messages.error(request,"Username already exists!! Try some different name. ")
         return redirect('SignUp')    

      if User.objects.filter(email=email).exists(): 
         messages.error(request,"An account is already registered with the same email id!!")
         return redirect('SignUp')    

      if len(pass1)<8:
         messages.error(request,"Password length should be atleast 8 characters!!")
         return redirect('SignUp')
         
      if pass1!=pass2:
         messages.error(request,"Passwords do not match!!")
         return redirect('SignUp')

  
      # Create the user
      myuser = User.objects.create_user(username, email, pass1)
      myuser.first_name= fname
      myuser.last_name= lname
      myuser.save()
      messages.success(request, " Your Account has been successfully created.")
      return redirect('ShopHome')
   else:
      return render (request,'shop/signup.html')

def handlelogin(request):
    if request.method =='POST':
        loginusername=request.POST.get('LoginUsername')
        loginpassword=request.POST.get('LoginPassword')
        user= authenticate(request, username=loginusername,password=loginpassword)

        if user is not None:
            login(request, user)
            messages.success(request, "Logged In Successfully  .")
            return redirect('ShopHome')
        else:
            messages.error(request, 'Invalid Credentials, Please try again.')
            return redirect('Login')
    else:
       return render (request,'shop/login.html')

@login_required(login_url='/login/')
def handlelogout(request):
    logout(request)
    messages.info(request,"Logged Out Successfully.")
    return redirect('Login')

def index(request):
    products = Product.objects.all()
    allProds = []
    catprods = Product.objects.values('category')
    cats = {item["category"] for item in catprods}
    for cat in cats:
        prod = Product.objects.filter(category=cat)
        n = len(prod)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        allProds.append([prod, range(1, nSlides), nSlides])

    params = {'allProds': allProds}
    return render(request, "shop/index.html", params)

@login_required(login_url='/login/')
def PasswordChange(request):
	user = request.user
	if request.method == 'POST':
		form = ChangePasswordForm(request.POST)
		if form.is_valid():
			new_password = form.cleaned_data.get('new_password')
			user.set_password(new_password)
			user.save()
			update_session_auth_hash(request, user)
			messages.success(request, "Password Updated Successfully.")
	else:
		form = ChangePasswordForm(instance=user)

	context = {
		'form':form,
	}

	return render(request, 'shop/change-password.html', context)

def about(request):
    return render(request, 'shop/about.html')


def contact(request):
    if request.method == "POST":
        Name = request.POST.get('name', '')
        Email = request.POST.get('email', '')
        Phone = request.POST.get('phone', '')
        Desc = request.POST.get('desc', '')

        contact = Contact(name=Name, email=Email, phone=Phone, desc=Desc)
        print(type(contact))
        contact.save()
    return render(request, 'shop/contact.html')


def tracker(request):
    if request.method == "POST":
        orderid = request.POST.get('orderId', '')
        Email = request.POST.get('email', '')
        try:
            order = Order.objects.filter(order_id=orderid, email=Email)
            if len(order) > 0:
                Update = OrderUpdate.objects.filter(order_id=orderid)
                updates = []
                for item in Update:
                    updates.append(
                        {'text': item.update_desc, 'time': item.timestamp})
                    response = json.dumps([updates,order[0].items_json], default=str)
                return HttpResponse(response)
            else:
                return HttpResponse('{}')
        except Exception as e:
            return HttpResponse('{}')
    return render(request, 'shop/tracker.html')


def searchMatch(query,item):
    print("Item is1", item)
    if query.lower() in (item.desc.lower()) or query.lower() in (item.product_name.lower()) or  query.lower() in(item.category.lower()) or query.lower() in   (item.subcategory.lower()): 
        print("Item is", item)
        return True
    else:    
        return False

def search(request):
    query=request.GET.get('search')
    allProds = []
    catprods = Product.objects.values('category')
    cats = {item["category"] for item in catprods}
    for cat in cats:
        prodtemp = Product.objects.filter(category=cat)
        prod=[item for item in prodtemp if searchMatch(query, item)]
        print("prod is",prod) 
        print(query) 
        n = len(prod)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        if n != 0:
            allProds.append([prod, range(1, nSlides), nSlides])

    params = {'allProds': allProds}
    return render(request, "shop/index.html", params)


def productView(request, myid):
    product = Product.objects.filter(id=myid)
    return render(request, 'shop/prodView.html', {'Vproduct': product[0]})


def checkout(request):
    if request.method == "POST":
        items_json = request.POST.get('itemsJson', '')
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        address = request.POST.get('address1', '') + \
            " " + request.POST.get('address2', '')
        city = request.POST.get('city', '')
        state = request.POST.get('state', '')
        zip_code = request.POST.get('zip_code', '')
        phone = request.POST.get('phone', '')

        checkout = Order(items_json=items_json, name=name, email=email,
                         address=address, city=city, state=state, zip_code=zip_code, phone=phone)
        checkout.save()
        update = OrderUpdate(order_id=checkout.order_id,
                             update_desc="The order has been placed")
        update.save()
        thank = True
        id = checkout.order_id
        print(type(checkout))
        return render(request, 'shop/checkout.html',{'thank': thank, 'id': id})
    return render(request, 'shop/checkout.html')

# def index(request):
#     return HttpResponse('This is index')
