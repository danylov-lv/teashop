from django.shortcuts import render, get_object_or_404
from cart.forms import CartAddProductForm
from .models import Category, Product


def product_list(request, category_slug=None):
    template_name = 'shop/product/list.html'

    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)

    context = {
        'category': category,
        'categories': categories,
        'products': products
    }

    return render(request=request, template_name=template_name, context=context)


def product_detail(request, id, slug):
    template_name = 'shop/product/detail.html'

    product = get_object_or_404(Product, id=id, slug=slug, available=True)

    cart_product_form = CartAddProductForm()

    context = {
        'product': product,
        'cart_product_form': cart_product_form
    }

    return render(request=request, template_name=template_name, context=context)
