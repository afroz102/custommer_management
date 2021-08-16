from django.shortcuts import render, redirect
from django.forms import inlineformset_factory

# from django.contrib import messages

# from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
# from django.contrib.auth.models import Group

from .models import Customer, Order, Product
from .forms import OrderForm, CustomerForm, CreateOrderForm
from .filters import OrderFilter

# To restrict user to access/view some admin pages
from .decorators import allowed_users, admin_only

from django.core.paginator import Paginator


# Create your views here.

# User(Customer)'s home page
@login_required(login_url='login')
@allowed_users(allowed_roles=['customer'])
def userPage(request):
    context = {}

    orders = request.user.customer.order_set.all().order_by('-date_created')

    total_orders = orders.count()
    delivered = orders.filter(status='Delivered').count()
    pending = orders.filter(status='Pending').count()

    context = {
        'orders': orders,
        'total_orders': total_orders,
        'delivered': delivered,
        'pending': pending,
    }
    # except Exception as identifier:
    #     pass

    return render(request, 'accounts/user.html', context)


# Account setting of customer page
@login_required(login_url='login')
@allowed_users(allowed_roles=['customer'])
def accountSettings(request):
    customer = request.user.customer
    print('customer: ', customer)
    form = CustomerForm(instance=customer)

    if request.method == 'POST':
        form = CustomerForm(request.POST, request.FILES, instance=customer)
        if form.is_valid():
            form.save()

    context = {'form': form}
    return render(request, 'accounts/account_settings.html', context)


@login_required(login_url='login')
@admin_only  # Only admin will have access to this
def home(request):
    orders = Order.objects.all().order_by('-date_created')
    customers = Customer.objects.all()

    total_orders = orders.count()
    total_customers = customers.count()
    delivered = orders.filter(status='Delivered').count()
    pending = orders.filter(status='Pending').count()

    # print("Order Choises: ", type(Order.STATUS))

    # status_category = {'Pending', 'Out for delivery', 'Delivered'}

    form = OrderForm()

    context = {
        'orders': orders[0:5],
        'customers': customers,
        'total_orders': total_orders,
        'total_customers': total_customers,
        'delivered': delivered,
        'pending': pending,
        'form': form
        # 'order_status': status_category
    }

    return render(request, 'accounts/dashboard.html', context)


# Product related functions | crud operations
@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def products(request):
    products = Product.objects.all()
    return render(request, 'accounts/products.html', {'products': products})


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def createProduct(request):
    return redirect('product')


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def updateProduct(request):
    return redirect('product')


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def deleteProduct(request):
    return redirect('product')

# Customer related functions | crud operations


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def customer(request, customer_id):
    customer = Customer.objects.get(id=customer_id)

    orders = customer.order_set.all()
    order_count = orders.count()

    # filter ordered items as per query request
    myFilter = OrderFilter(request.GET, queryset=orders)
    print("Filter form: ", myFilter)
    orders = myFilter.qs  # filtered order

    context = {
        'customer': customer,
        'orders': orders,
        'order_count': order_count,
        'myFilter': myFilter
    }

    return render(request, 'accounts/customer.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def deleteCustomer(request, customer_id):
    return redirect('customer')


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def updateCustomer(request, customer_id):
    return redirect('customer')


# Order related functions crud operations
@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def orderDetails(request):
    orders = Order.objects.all().order_by('-date_created')
    customers = Customer.objects.all()

    paginator = Paginator(orders, 5)  # Show 5 contacts per page.

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    # return render(request, 'list.html', {'page_obj': page_obj})

    # filter ordered items as per query request
    myFilter = OrderFilter(request.GET, queryset=orders)
    orders = myFilter.qs  # filtered order

    context = {
        'orders': orders,
        'customers': customers,
        'myFilter': myFilter,
        'page_obj': page_obj
    }

    return render(request, 'accounts/order_details.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['customer'])
def create_order(request, customer_id):

    customer = Customer.objects.get(id=customer_id)

    #  for single form to order
    form = CreateOrderForm()

    if request.method == 'POST':
        # orderForm = Order.objects.create_user(username=username, email=email)
        # orderForm.save()

        # formData = request.POST
        # userInfo = {
        #     'customer': customer,
        #     'status': "Pending"
        # }

        # userInfo.update(formData)
        # formData.customer = customer
        # formData.status = "Pending"

        # print("form data: ", userInfo)

        orderForm = CreateOrderForm(request.POST)
        if orderForm.is_valid():
            # print(" form is valid")
            orderData = orderForm.save(commit=False)
            orderData.customer = customer
            orderData.status = "Pending"
            orderData.save()

            print("orderData: ", orderData)
            return redirect('/')

    context = {'form': form}

    print("didn't work")

    return render(request, 'accounts/create_order_form.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def delete_order(request, order_id):
    order = Order.objects.get(id=order_id)
    # print("Order: ", order)
    # context = {'item': order}

    if request.method == 'POST':
        print("Order delete data: ", request.POST)
        order.delete()
        return redirect('/')

    # return render(request, 'accounts/delete.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def update_order(request, order_id):
    order = Order.objects.get(id=order_id)
    form = OrderForm(instance=order)
    context = {
        'form': form,
        'order': order
    }

    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        if form.is_valid:
            form.save()
            return redirect('/')

    # return render(request, 'accounts/update_form.html', context)
