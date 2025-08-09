from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm

from apps.marketplace.models import Product


def register_view(request):
    context = {}
    if request.method == "POST":
        username = (request.POST.get("username") or "").strip()
        email = (request.POST.get("email") or "").strip()
        password = request.POST.get("password") or ""
        password2 = request.POST.get("password2") or ""
        role = request.POST.get("role")  # <-- get role from form

        context = {"username": username, "email": email, "role": role}

        if not username or not password:
            messages.error(request, "Username and password are required.")
        elif password != password2:
            messages.error(request, "Passwords do not match.")
        elif User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
        else:
            user = User.objects.create_user(username=username, email=email, password=password)
            # Set role in profile
            if hasattr(user, "profile"):
                user.profile.role = role
                user.profile.save()
            login(request, user)
            messages.success(request, "Registration successful. Welcome!")
            return redirect("marketplace:home")

    return render(request, "accounts/register.html", context)


def login_view(request):
    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            next_url = request.GET.get("next") or request.POST.get("next") or "accounts:customer_dashboard"
            return redirect(next_url)
        messages.error(request, "Invalid username or password.")
    return render(request, "accounts/login.html", {"form": form})


def logout_view(request):
    logout(request)
    messages.info(request, "Logged out.")
    return redirect("accounts:login")


@login_required
def customer_dashboard(request):
    profile = getattr(request.user, "profile", None)

    # Cart summary
    cart = request.session.get("cart", {})
    cart_items, cart_total = [], 0
    if cart:
        ids = [int(k) for k in cart.keys()]
        for p in Product.objects.filter(pk__in=ids):
            qty = int(cart[str(p.pk)])
            line = float(p.price) * qty
            cart_total += line
            cart_items.append({"product": p, "qty": qty, "line_total": line})

    # Suggestions
    suggestions = Product.objects.order_by("-id")[:6]

    # Farmer's own products (if role exists and is FARMER)
    my_products = []
    if profile and getattr(profile, "role", "") == "FARMER":
        my_products = Product.objects.filter(owner=request.user).order_by("-id")

    return render(
        request,
        "accounts/customer_dashboard.html",
        {
            "profile": profile,
            "cart_items": cart_items,
            "cart_total": cart_total,
            "suggestions": suggestions,
            "my_products": my_products,
        },
    )
