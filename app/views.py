from math import ceil
from urllib.request import HTTPBasicAuthHandler

import requests
from eComm import settings
from django.shortcuts import redirect, render
import razorpay
from django.contrib import messages
from app.models import Orders, Product
from django.views.decorators.csrf import csrf_exempt

# authorize razorpay client with API Keys.
razorpay_client = razorpay.Client(
    auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
# Create your views here.

#Index Page
def index(request):
    allProds = []
    catprods = Product.objects.values('category', 'id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        if cat == "Deals on Laptops" or cat == "Best Sellers in Computers & Accessories":
            prod = Product.objects.filter(category=cat)
            n = len(prod)
            nSlides = n // 4 + ceil((n / 4) - (n // 4))
            allProds.append([prod, range(1, nSlides), nSlides])
    params = {'allProds': allProds}
    return render(request, "index.html", params)

# Single View Product
def product(request, id):
    product = Product.objects.filter(id=id).values()
    params = {'allProds': product}
    return render(request, "product.html", params)

# Product By Category Name
def Productlist(request, name):
    catprods = Product.objects.filter(subcategory=name)
    params = {'allProds': catprods}
    return render(request, "products.html", params)


# About Us Page
def about(request):
    return render(request, "about.html")

# Team Page
def team(request):
    return render(request, "team.html")

# Checkout Page
def checkout(request):
    if not request.user.is_authenticated:
        messages.warning(request, "Login & Try Again")
        return redirect('/auth/login')

    if request.method == "POST":
        items_json = request.POST.get('itemsJson', '')
        name = request.POST.get('name', '')
        amount = request.POST.get('amt')
        email = request.POST.get('email', '')
        address1 = request.POST.get('address1', '')
        address2 = request.POST.get('address2', '')
        city = request.POST.get('city', '')
        state = request.POST.get('state', '')
        zip_code = request.POST.get('zip_code', '')
        phone = request.POST.get('phone', '')
        Order = Orders(items_json=items_json, name=name, user_email=request.user.email, amount=amount, email=email,
                       address1=address1, address2=address2, city=city, state=state, zip_code=zip_code, phone=phone)
        Order.save()
# # RAZOR PAY INTEGRATION
        order_id = Order.order_id
        order_amount = int(amount)*100  # 9900
        new_order_response = razorpay_client.order.create({
            "amount": order_amount,
            "currency": "INR",
                        "payment_capture": "1"
        })
        # param_dict['CHECKSUMHASH'] = Checksum.generate_checksum(param_dict, MERCHANT_KEY)
        return render(
            request,
            "payment.html",
            {
                "callback_url": settings.DOMAIN + "/callback/",
                "razorpay_key": settings.RAZORPAY_KEY_ID,
                "order": new_order_response,
                "order_id": order_id
            },
        )

    return render(request, 'checkout.html')

# Razor Pay Callback
@csrf_exempt
def callback(request):
    data = {}
    try:
        razorpay_payment_id = request.POST.get('razorpay_payment_id', '')
        orderid = request.POST.get('order_id', '')
        callUrl = "https://api.razorpay.com/v1/payments/"+razorpay_payment_id
        response = requests.get(callUrl, auth=HTTPBasicAuthHandler(
            settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        print(response)
        if response.status_code == 200:
            Order = Orders.objects.get(orderid=orderid)
            Order.payment_id = razorpay_payment_id
            Order.save()
            data = response.json()

        else:
            print('Error:', response.status_code)

        # verify the payment signature.

        return render(request, "paymentstatus.html", {'response': data})
    except:
        return render(request, "paymentstatus.html", {'response': data})