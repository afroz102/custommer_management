from .decorators import unauthenticated_user
from .forms import CreateUserForm
from django.shortcuts import render, redirect
from django.contrib.auth.models import Group, User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from accounts.models import Customer

# new imposr starts
from django.shortcuts import render, redirect
# from django.views.generic import View

# # to flash succes or error messages
from django.conf import settings
# to validate forms
from validate_email import validate_email
#  to get urls of the current site
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_text, DjangoUnicodeDecodeError
from django.core.mail import EmailMessage
from .utils import generate_token
from django.contrib.auth.tokens import PasswordResetTokenGenerator
import threading

# # new imports ends


# Create your views here.


# To sppedup the sending email
class EmailThread(threading.Thread):

    def __init__(self, email_message):
        self.email_message = email_message
        threading.Thread.__init__(self)

    def run(self):
        self.email_message.send()


@unauthenticated_user
def register_user(request):
    if request.method == 'GET':
        return render(request, 'auth/register.html')
    if request.method == 'POST':
        context = {
            'data': request.POST,
            'has_error': False
        }

        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        if (username is None or username == '') or (email is None or email == '') or (password is None or password == '') or (password2 is None or password2 == ''):
            messages.add_message(request, messages.ERROR,
                                 'Please fill the all fields.')
            context['has_error'] = True

            return render(request, 'auth/register.html', context, status=400)

        if not validate_email(email):
            messages.add_message(request, messages.ERROR,
                                 'Please provide a valid email')
            context['has_error'] = True

            return render(request, 'auth/register.html', context, status=400)

        if len(password) < 6:
            messages.add_message(request, messages.ERROR,
                                 'passwords should be atleast 6 characters long')
            context['has_error'] = True

        if password is None or password != password2:
            messages.add_message(request, messages.ERROR,
                                 'passwords dont match')
            context['has_error'] = True
            return render(request, 'auth/register.html', context, status=400)

        try:
            if User.objects.get(email=email):
                messages.add_message(request, messages.ERROR, 'Email is taken')
                context['has_error'] = True
                return render(request, 'auth/register.html', context, status=400)

        except Exception as identifier:
            pass

        try:
            if User.objects.get(username=username):
                messages.add_message(
                    request, messages.ERROR, 'Username is taken')
                context['has_error'] = True
                return render(request, 'auth/register.html', context, status=400)

        except Exception as identifier:
            pass

        if context['has_error']:
            return render(request, 'auth/register.html', context, status=400)

        user = User.objects.create_user(username=username, email=email)
        user.set_password(password)
        user.is_active = False
        user.save()

        # Add user to admin group
        group = Group.objects.get(name='customer')
        user.groups.add(group)
        # Assigning the user to customer model
        Customer.objects.create(
            user=user,
            name=user.username,
        )

        current_site = get_current_site(request)
        email_subject = 'Activate your Account'

        message = render_to_string('auth/activate.html', {
            'user': user,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': generate_token.make_token(user)
        })

        email_message = EmailMessage(
            email_subject,
            message,
            settings.EMAIL_HOST_USER,
            [email]
        )

        EmailThread(email_message).start()
        messages.add_message(request, messages.SUCCESS,
                             'A link has been sent to your email. click on the link to activate your account.')

        return redirect('login')


# @unauthenticated_user
# def registerPage(request):

#     form = CreateUserForm()

#     if request.method == 'POST':
#         form = CreateUserForm(request.POST)

#         if form.is_valid():
#             user = form.save()
#             # getting username from form and sending a flash message to login
#             # page
#             username = form.cleaned_data.get('username')
#             messages.success(request, 'Account create for ' + username)

#             # add user to customer group
#             group = Group.objects.get(name='customer')
#             user.groups.add(group)

#             # Assigning the user to customer model
#             Customer.objects.create(
#                 user=user,
#                 name=user.username,
#             )

#             return redirect('login')

#     context = {'form': form}

#     return render(request, 'users/register.html', context)


def activate_account(request, uidb64, token):
    try:
        # decode if the uid is same as user.id sent from the host
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)

    except Exception as identifier:
        user = None

    # if id matches set user as verified and save
    if user is not None and generate_token.check_token(user, token):
        user.is_active = True
        user.save()
        messages.add_message(request, messages.SUCCESS,
                             'account activated successfully')
        return redirect('login')

    # else return to activation failed page to show error message
    return render(request, 'auth/activate_failed.html', status=401)


@unauthenticated_user
def login_user(request):
    if request.method == "GET":
        return render(request, 'auth/login.html')

    if request.method == "POST":
        context = {
            'data': request.POST,
            'has_error': False
        }

        username = request.POST.get('username')
        password = request.POST.get('password')

        if username == '':
            messages.add_message(request, messages.ERROR,
                                 'Username is required')
            context['has_error'] = True
        if password == '':
            messages.add_message(request, messages.ERROR,
                                 'Password is required')
            context['has_error'] = True

        user = authenticate(request, username=username, password=password)

        if not user and not context['has_error']:
            messages.add_message(request, messages.ERROR, 'Invalid login')
            context['has_error'] = True

        if context['has_error']:
            return render(request, 'auth/login.html', status=401, context=context)

        login(request, user)

        return redirect('home')

# @unauthenticated_user
# def loginPage(request):
#     # if request.user.is_authenticated:
#     #     return redirect('home')

#     context = {}
#     if request.method == 'POST':
#         username = request.POST.get('username')
#         password = request.POST.get('password')
#         user = authenticate(request, username=username, password=password)

#         if user is not None:
#             login(request, user)
#             return redirect('home')
#         else:
#             messages.info(request, 'Username OR Password is incorrect')
#             return render(request, 'users/login.html', context)

#     return render(request, 'users/login.html', context)


def logoutUser(request):
    logout(request)
    return redirect('login')
