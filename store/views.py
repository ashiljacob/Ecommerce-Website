from django.shortcuts import render
from .models import *
from django.http import JsonResponse
import json
import datetime
from .utils import cartData,guestOrder
import logging

logger = logging.getLogger(__name__)

# Create your views here.

def login(request):
    logger.info("Inside Login")
    if request.method == 'POST':
        logger.info("Inside Login")
        if User.objects.filter(username=request.POST['username'], password=request.POST['password']).exists():
            user = User.objects.get(username=request.POST['username'], password=request.POST['password'])
            # request.session['user'] = user.name

            logger.info("user :"+user)
            return render(request, 'store/store.html', {'user': user})

        else:
            return render(request, 'index.html')


# Registration Page
def registration(request):
    return render(request, 'reg.html')


# user Registration
def registration_upload(request):
    if request.method == 'POST':
        if request.POST['password'] == request.POST['password1']:

            reg = User(name=request.POST['name'], username=request.POST['username']
                       , password=request.POST['password'])
            reg.save()
            return render(request, 'index.html')
        else:
            return HttpResponse("<script>alert('Password didnt match')</script>")
            return redirect('/')
    else:
        return HttpResponse("<h1>Error While Registering.. TRy Again..</h1>")





def logout(request):
    if request.method == "POST":
        act = Activity.objects.get(id=request.session['id'])
        act.log_out = datetime.now()
        act.save()
        return render(request,'index.html')
    else:
        return HttpResponse("<h1>Error While LogOut..!!</h1>")

def store(request):
    data = cartData(request)
    cartItem = data['cartItems']
       
    product = Product.objects.all()
    context = {'products':product,'cartItem':cartItem}
    return render(request,'store\store.html',context)

def cart(request):
    data = cartData(request)
    cartItem = data['cartItems']
    order    = data['order']
    items    = data['items']

    context = {'items':items,'order':order,'cartItem':cartItem}
    return render(request,'store\cart.html',context)

def checkout(request):
    data = cartData(request)
    cartItem = data['cartItems']
    order    = data['order']
    items    = data['items']
        
    context = {'items':items,'order':order,'cartItem':cartItem}
    return render(request,'store\checkout.html',context)

def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    print('Action:', action)
    print('Product:', productId)

    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)

    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('Item was Added',safe=False)

def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)

        
    else:
        customer , order = guestOrder(request,data)
    # total = float(data['form']['total'])
    # order.transaction_id = transaction_id
    
    total = float(data['form']['total'])
    order.transaction_id = transaction_id
    
    if total == float(order.get_cart_total):
        order.complete = True
    order.save()
    
    if order.shipping == True:
        ShippingAddress.objects.create(
            customer=customer,
            order=order,
            address=data['shipping']['address'],
            city=data['shipping']['city'],
            state=data['shipping']['state'],
            zipcode=data['shipping']['zipcode'],
        )


    return JsonResponse('Payment Complete',safe=False)
