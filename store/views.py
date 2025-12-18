from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Category
from .cart import Cart
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .forms import CheckoutForm
from .models import Product, Category, Order, OrderItem
from django.db.models import Q

def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)

    # Filter by category
    if category_slug:
        category = Category.objects.get(slug=category_slug)
        products = products.filter(category=category)

    # Search
    query = request.GET.get('q')
    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query)
        )

    # Filter theo giá
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)

    # Sort
    sort = request.GET.get('sort')
    if sort == 'price_asc':
        products = products.order_by('price')
    elif sort == 'price_desc':
        products = products.order_by('-price')
    elif sort == 'newest':
        products = products.order_by('-created')
    else:
        products = products.order_by('-created')

    # Pagination
    paginator = Paginator(products, 8)
    page = request.GET.get('page')
    products = paginator.get_page(page)

    return render(request, 'store/product_list.html', {
        'category': category,
        'categories': categories,
        'products': products,
        'query': query,
        'min_price': min_price,
        'max_price': max_price,
        'sort': sort,
    })
    


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, available=True)
    
    # Other products in the same category
    related_products = Product.objects.filter(
        category=product.category,
        available=True
    ).exclude(id=product.id)[:4]   # maximum 4 products

    # Suggest unique random products
    from random import sample
    all_products = list(Product.objects.filter(available=True).exclude(id=product.id))

    suggested = sample(all_products, min(len(all_products), 4))

    return render(request, 'store/product_detail.html', {
        'product': product,
        'related_products': related_products,
        'suggested': suggested,
    })

def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id, available=True)

    if request.method == 'POST':
        try:
            quantity = int(request.POST.get('quantity', 1))
        except ValueError:
            quantity = 1
    else:
        quantity = 1

    if quantity < 1:
        quantity = 1

    cart.add(product=product, quantity=quantity)
    return redirect('cart_detail')


def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id, available=True)
    cart.remove(product)
    return redirect('cart_detail')

def cart_update(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id, available=True)

    if request.method == 'POST':
        try:
            quantity = int(request.POST.get('quantity', 1))
        except ValueError:
            quantity = 1

        cart.add(product=product, quantity=quantity, override_quantity=True)

    return redirect('cart_detail')

def cart_detail(request):
    cart = Cart(request)
    return render(request, 'store/cart_detail.html', {'cart': cart})


def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('product_list')
    else:
        form = UserCreationForm()
    return render(request, 'store/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('product_list')
    else:
        form = AuthenticationForm(request)
    return render(request, 'store/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('product_list')


@login_required
def checkout(request):
    cart = Cart(request)

    if len(cart) == 0:
        return redirect('product_list')

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.save()

            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    price=item['price'],
                    quantity=item['quantity']
                )

            cart.clear()
            return render(request, 'store/order_success.html', {'order': order})
    else:
        initial = {}
        if request.user.is_authenticated:
            initial = {
                'full_name': request.user.get_full_name() or request.user.username,
                'email': request.user.email,
            }
        form = CheckoutForm(initial=initial)

    return render(request, 'store/checkout.html', {
        'cart': cart,
        'form': form,
    })

