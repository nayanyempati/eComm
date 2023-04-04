from urllib.request import HTTPBasicAuthHandler
from django.shortcuts import render, redirect
import razorpay
import requests

from django.contrib import messages
from math import ceil
from app import keys
from django.conf import settings
import json
from django.views.decorators.csrf import csrf_exempt

from app.models import Contact, Orders, Product

# authorize razorpay client with API Keys.
razorpay_client = razorpay.Client(
    auth=(keys.RAZORPAY_KEY_ID, keys.RAZORPAY_KEY_SECRET))

# Create your views here.


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

# Create your views here.


def list(request, name):
    catprods = Product.objects.filter(subcategory=name)
    params = {'allProds': catprods}
    return render(request, "products.html", params)


def product(request, id):
    product = Product.objects.filter(id=id).values()
    params = {'allProds': product}
    return render(request, "product.html", params)


def products(request, id):
    product = Product.objects.filter(id=id).values()
    params = {'allProds': product}
    return render(request, "products.html", params)


def contact(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        desc = request.POST.get("desc")
        pnumber = request.POST.get("pnumber")
        myquery = Contact(name=name, email=email,
                          desc=desc, phonenumber=pnumber)
        myquery.save()
        messages.info(request, "we will get back to you soon..")
        return render(request, "contact.html")

    return render(request, "contact.html")


def about(request):
    return render(request, "about.html")


def team(request):
    return render(request, "team.html")


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
        thank = True


# # RAZOR PAY INTEGRATION

        order_id = Order.order_id
        print(order_id)
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
                "callback_url": keys.DOMAIN + "/callback/",
                "razorpay_key": keys.RAZORPAY_KEY_ID,
                "order": new_order_response,
                "order_id": order_id
            },
        )

    return render(request, 'checkout.html')


@csrf_exempt
def handlerequest(request):
    # paytm will send you post request here
    form = request.POST
    response_dict = {}
    for i in form.keys():
        response_dict[i] = form[i]
        if i == 'CHECKSUMHASH':
            checksum = form[i]

    verify = ""
    if verify:
        if response_dict['RESPCODE'] == '01':
            print('order successful')
            a = response_dict['ORDERID']
            b = response_dict['TXNAMOUNT']
            rid = a.replace("ShopyCart", "")

            print(rid)
            filter2 = Orders.objects.filter(order_id=rid)
            print(filter2)
            print(a, b)
            for post1 in filter2:

                post1.oid = a
                post1.amountpaid = b
                post1.paymentstatus = "PAID"
                post1.save()
            print("run agede function")
        else:
            print('order was not successful because' +
                  response_dict['RESPMSG'])
    return render(request, 'paymentstatus.html', {'response': response_dict})


@csrf_exempt
def callback(request):
    data = {}
    try:
        razorpay_payment_id = request.POST.get('razorpay_payment_id', '')
        orderid = request.POST.get('order_id', '')
        callUrl = "https://api.razorpay.com/v1/payments/"+razorpay_payment_id
        response = requests.get(callUrl, auth=HTTPBasicAuthHandler(
            keys.RAZORPAY_KEY_ID, keys.RAZORPAY_KEY_SECRET))
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


def myorders(request):
    if not request.user.is_authenticated:
        messages.warning(request, "Login & Try Again")
        return redirect('/auth/login')
    currentuser = request.user.email
    items = Orders.objects.filter(email=currentuser)
    params = {'allProds': items}
    print(dict(params))
    return render(request, "orders.html", params)
