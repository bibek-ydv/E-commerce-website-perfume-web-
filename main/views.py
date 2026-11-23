from django.db.models import Count
from django.shortcuts import render, redirect,  get_object_or_404
from django.http import JsonResponse,HttpResponse
from django.views import View
from . models import Product,Cart,Customer,OrderPlaced
from . forms import CustomerRegistrationForm, CustomerProfileForm,Customer
from django.contrib import messages
from django.db.models import Q
import requests
from django.conf import settings







# Create your views here.
def home(request):
    return render(request,"main/home.html")

def about(request):
    totalitem=0
    if request.user.is_authenticated:
        totalitem=len(Cart.objects.filter(user=request.user))
    return render(request,"main/about.html")

def contact(request):
    totalitem=0
    if request.user.is_authenticated:
        totalitem=len(Cart.objects.filter(user=request.user))
    return render(request,"main/contact.html")

class CategoryView(View):
    def get(self,request,val):
        product=Product.objects.filter(category=val)
        title=Product.objects.filter(category=val).values('title')
        return render(request,"main/category.html",locals())



class CategoryTitle(View):
    def get(self,request,val):
        product=Product.objects.filter(title=val)
        title=Product.objects.filter(category=product[0].category).values('title')
        return render(request,"main/category.html",locals())



class ProductDetail(View):
    def get(self,request,pk):
        product=Product.objects.get(pk=pk)
        return render(request,"main/productdetail.html",locals())
    
class CustomerRegistrationView(View):
    def get(self,request):
        form=CustomerRegistrationForm()
        return render(request,"main/customerregistration.html",locals())
    def post(self,request):
        form=CustomerRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,"Congratulations! User Register Successfully")
        else:
            messages.warning(request,"Invalid Input Data")
        return render(request,"main/customerregistration.html",locals())  

class ProfileView(View):
    def get(self,request):
        form=CustomerProfileForm()
        return render(request,"main/profile.html",locals())
    def post(self,request):
        form=CustomerProfileForm(request.POST)
        if form.is_valid():
            user=request.user
            name=form.cleaned_data['name']
            locality=form.cleaned_data['locality']
            city=form.cleaned_data['city']
            mobile=form.cleaned_data['mobile']  
            state=form.cleaned_data['state']
            zipcode=form.cleaned_data['zipcode']

            reg=Customer(user=user,name=name,locality=locality,mobile=mobile,city=city,state=state,zipcode=zipcode)
            reg.save()
            messages.success(request,"Congratulation! Profile Saved Successfully")
        else:
            messages.warning(request,"Invalid Input Data")
        return render(request,"main/profile.html",locals())
        
def address(request):
    add=Customer.objects.filter(user=request.user)
    return render(request,'main/address.html',locals())     

class updateAddress(View):
    def get(self,request,pk):
        add=Customer.objects.get(pk=pk)
        form=CustomerProfileForm(instance=add)
        return render(request,'main/updateAddress.html',locals())  
    def post(self,request,pk):
        form=CustomerProfileForm(request.POST)
        if form.is_valid():
            add=Customer.objects.get(pk=pk)
            add.name=form.cleaned_data['name']
            add.locality=form.cleaned_data['locality']
            add.city=form.cleaned_data['city']
            add.mobile=form.cleaned_data['mobile']  
            add.state=form.cleaned_data['state']
            add.zipcode=form.cleaned_data['zipcode']

            add.save()
            messages.success(request,"Congratulation! Profile updated Successfully")
        else:
            messages.warning(request,"Invalid Input Data")
        return redirect("address")              
def add_to_cart(request):
    user = request.user
    product_id = request.GET.get('prod_id')

    if product_id:
        product_id = product_id.strip('/')  # removes trailing or leading slashes

        try:
            product = Product.objects.get(id=int(product_id))

            cart_item, created = Cart.objects.get_or_create(
                user=user,
                product=product
            )

            if not created:
                cart_item.quantity += 1
                cart_item.save()

        except (ValueError, Product.DoesNotExist):
            return redirect("/cart")

    return redirect("/cart")



def show_cart(request):
    user=request.user
    cart=Cart.objects.filter(user=user)
    amount=0
    for p in cart:
        value=p.quantity*p.product.discounted_price
        amount=amount+value
    totalamount=amount+40    
    return render(request,'main/addtocart.html',locals())  

class checkout(View):
    def get(self,request):
        user=request.user
        add=Customer.objects.filter(user=user)
        cart_items=Cart.objects.filter(user=user)
        famount=0
        for p in cart_items:
            value=p.quantity*p.product.discounted_price
            famount=famount+value
        totalamount=famount+40    
        return render(request,'main/checkout.html',locals())  



KHALTI_PUBLIC_KEY = "test_public_key_dc74b7f6a7b34355844d9e5adf46a8a5"
KHALTI_SECRET_KEY = "test_secret_key_52b9a0b2b45048e1a30b6da3d0f1f9b1"
def verify_khalti_payment(token, amount):
    url = "https://test-admin.khalti.com/api/v2/payment/verify/"
    headers = {
        "Authorization": f"Key {settings.KHALTI_SECRET_KEY}"
    }
    data = {
        "token": token,
        "amount": amount
    }
    response = requests.post(url, data=data, headers=headers)
    return response.json()



def orders(request):
    order_placed=OrderPlaced.objects.filter(user=request.user)
    return render(request,'main/orders.html',locals())
    



def plus_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        c = Cart.objects.filter(Q(product=prod_id) & Q(user=request.user)).first()
       
        if c:
           c.quantity += 1
           c.save()

        else:
            c=Cart.objects.create(user=request.user,product=prod_id,quantity=1)   

        user = request.user
        cart = Cart.objects.filter(user=user)
        amount = 0
        for p in cart:
            amount += p.quantity * p.product.discounted_price
        totalamount = amount + 40

        data = {
            'quantity': c.quantity,
            'amount': amount,
            'totalamount': totalamount
        }
        return JsonResponse(data)
    
def minus_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        c = Cart.objects.filter(Q(product=prod_id) & Q(user=request.user)).first()
        c.quantity -= 1
        c.save()

        user = request.user
        cart = Cart.objects.filter(user=user)
        amount = 0
        for p in cart:
            amount += p.quantity * p.product.discounted_price
        totalamount = amount + 40

        data = {
            'quantity': c.quantity,
            'amount': amount,
            'totalamount': totalamount
        }
        return JsonResponse(data) 

def remove_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        c = Cart.objects.filter(Q(product=prod_id) & Q(user=request.user)).first()
        c.quantity += 1
        c.delete()

        user = request.user
        cart = Cart.objects.filter(user=user)
        amount = 0
        for p in cart:
            amount += p.quantity * p.product.discounted_price
        totalamount = amount + 40

        data = {

            'amount': amount,
            'totalamount': totalamount
        }
        return JsonResponse(data)
def Shop_Collection(request):
    products = Product.objects.all()
    return render(request, 'main/Shop_Collection.html', {'products': products})


    
    



    

