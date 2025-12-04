from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Category
from .cart import Cart

def product_list(request):
    products = Product.objects.filter(available=True)
    categories = Category.objects.all()
    return render(request, 'store/product_list.html', {
        'products': products,
        'categories': categories,
    })


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, available=True)
    return render(request, 'store/product_detail.html', {
        'product': product,
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


