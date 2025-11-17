from django.shortcuts import redirect, render
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from accounts.forms import RegisterForm
from accounts.models import Account

# Email Verification Library
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage

from carts.models import Cart, CartItem
from carts.views import _cart_id
import requests



def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            username = email.split("@")[0]

            try:
                user = Account.objects.create_user(first_name=first_name, last_name=last_name, email=email, username=username, password=password)
                user.phone_number = phone_number
                user.save()

                # User Activation
                current_site = get_current_site(request)
                mail_subject = "Please activate your account"
                message = render_to_string('accounts/emails/account_verification_email.html', {
                    'user': user,
                    'domain': current_site,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': default_token_generator.make_token(user),
                })
                to_email = email
                send_email = EmailMessage(mail_subject, message, to=[to_email])
                send_email.send()

                # messages.success(request, 'Registration successful! Check your email for verification link.')
                return redirect('/auth/login/?command=verification&email='+email)
            except Exception as e:
                messages.error(request, 'Registration failed. Please try again.')
        else:
            if form.errors:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, error)
    else:
        form = RegisterForm()
    context = {
        'form': form,
    }
    return render(request, 'accounts/register.html', context)



def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(email=email, password=password)

        if user is not None:
            _merge_session_cart_with_user_cart(request, user)
            auth.login(request, user)
            messages.success(request, 'Logged in successfully')
            
            # Check session for next URL (saved from GET request)
            next_url = request.session.get('next_url') or 'dashboard'
            
            # Clear it from session after use
            if 'next_url' in request.session:
                del request.session['next_url']
            
            return redirect(next_url)
        else:
            messages.error(request, 'Username or password not correct!')
            return redirect('login')
    else:
        # GET request - save 'next' to session for POST
        next_url = request.GET.get('next')
        if next_url:
            request.session['next_url'] = next_url
    
    return render(request, 'accounts/login.html')


def _merge_session_cart_with_user_cart(request, user):
    """
    Merges anonymous session cart items with authenticated user's cart.
    If same product+variations exist, increases quantity. Otherwise, transfers item.
    """
    try:
        # Get anonymous session cart
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_item = CartItem.objects.filter(cart=cart)
        
        if not cart_item.exists():
            return
        
        # Get user's existing cart items
        user_cart_items = CartItem.objects.filter(user=user)
        
        # Build lookup dict: variation_ids (sorted tuple) -> user cart item
        user_variation_map = {}
        for item in user_cart_items:
            variation_ids = tuple(sorted(item.variations.values_list('id', flat=True)))
            user_variation_map[variation_ids] = item
        
        # Process each session cart item
        for item in cart_item:
            # Get variation IDs for current item
            variation_ids = tuple(sorted(item.variations.values_list('id', flat=True)))
            
            # Check if user already has this product+variation combo
            if variation_ids in user_variation_map:
                # Increase quantity of existing user cart item
                existing_item = user_variation_map[variation_ids]
                existing_item.quantity += item.quantity
                existing_item.save()
                
                # Delete session cart item (merged)
                item.delete()
            else:
                # Transfer session cart item to user
                item.user = user
                item.cart = None  # Disconnect from session cart
                item.save()
        
        # Optional: Delete empty session cart
        if not CartItem.objects.filter(cart=cart).exists():
            cart.delete()
            
    except Cart.DoesNotExist:
        # No session cart exists, nothing to merge
        pass


@login_required(login_url = 'login')
def logout(request):
    auth.logout(request)
    messages.success(request, "You're logged out!")
    return redirect('login')


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)

    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Congrats, your account is successfully verified. You can login to your acount and start shopping!")
        return redirect('login')
    
    else:
        messages.error(request, 'Invalid activation link')
        return redirect('register')
    


@login_required(login_url='login')
def dashboard(request):
    return render(request, 'accounts/dashboard/dashboard.html')



def forgot_password(request):
    if request.method == 'POST':
        email = request.POST['email']
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)

            # Reset Password Email
            current_site = get_current_site(request)
            mail_subject = "Reset Your Password"
            message = render_to_string('accounts/emails/forgot_password_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()

            messages.success(request, "Check email address for password reset link")
            return redirect('login')
        else:
            messages.error(request, "Account does not exist!")
            return redirect('password_reset')
    return render(request, 'accounts/forgot_password.html')


def password_reset_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)

    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, "Please reset your password")
        return redirect('reset_password')
    else:
        messages.error(request, "Link expired!")
        return redirect('login')
    
def reset_password(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request, "Password reset successfully")
            return redirect('login')

        
        else:
            messages.error(request, "Password doesn't match!")
            return redirect('reset_password')
        
    else:
        return render(request, 'accounts/reset_password.html')