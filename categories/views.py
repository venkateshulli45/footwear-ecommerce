from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods, require_POST

from .models import (
    BagItem,
    KFM,
    MFM,
    Order,
    OrderLine,
    WFM,
    KFMSizeAvailability,
    MFMSizeAvailability,
    WFMSizeAvailability,
)

CATEGORY_SIZES = {
    'MFM': ['6', '7', '8', '9', '10'],
    'WFM': ['4', '5', '6', '7', '8'],
    'KFM': ['1', '2', '3', '4', '5'],
}

CATALOG_META = {
    'WFM': {
        'slug': 'women',
        'title': "Women's footwear",
        'subtitle': 'Heels, flats, sandals, and everyday pairs curated for comfort.',
    },
    'MFM': {
        'slug': 'men',
        'title': "Men's footwear",
        'subtitle': 'Sneakers, formal shoes, and rugged casuals.',
    },
    'KFM': {
        'slug': 'kids',
        'title': "Kids' footwear",
        'subtitle': 'Durable sizes for growing feet — playground to classroom.',
    },
}

FREE_SHIPPING_AT = Decimal('1999.00')
STANDARD_SHIPPING = Decimal('99.00')


def get_product_and_sizes(category, product_id):
    model_map = {
        'WFM': (WFM, WFMSizeAvailability),
        'MFM': (MFM, MFMSizeAvailability),
        'KFM': (KFM, KFMSizeAvailability),
    }
    if category not in model_map:
        return None, []
    ProductModel, _ = model_map[category]
    try:
        product = ProductModel.objects.prefetch_related('sizes').get(id=product_id)
        available_sizes = list(
            product.sizes.filter(quantity__gt=0).values_list('size', flat=True)
        )
        try:
            available_sizes.sort(key=float)
        except ValueError:
            available_sizes.sort()
        return product, available_sizes
    except ProductModel.DoesNotExist:
        return None, []


def _annotate_products(products, category_code):
    for product in products:
        available_sizes = [s.size for s in product.sizes.all() if s.quantity > 0]
        try:
            available_sizes.sort(key=float)
        except ValueError:
            available_sizes.sort()
        product.set_available_sizes(available_sizes)

        # Pricing + merch annotations for templates (avoid template math).
        try:
            mrp = int(product.mrp) if product.mrp else None
        except (TypeError, ValueError):
            mrp = None
        price = int(product.price) if product.price is not None else 0

        if mrp and mrp > price and price > 0:
            product.has_discount = True
            product.discount_amount = mrp - price
            product.discount_percent = int(round((product.discount_amount / mrp) * 100))
            product.display_mrp = mrp
        else:
            product.has_discount = False
            product.discount_amount = 0
            product.discount_percent = 0
            product.display_mrp = None

        if product.rating is not None:
            product.display_rating = float(product.rating)
        else:
            product.display_rating = None
    return products


def wft(request):
    products = _annotate_products(
        list(WFM.objects.prefetch_related('sizes').all()), 'WFM'
    )
    meta = CATALOG_META['WFM']
    return render(
        request,
        'catalog_list.html',
        {
            'products': products,
            'category_code': 'WFM',
            'page_title': meta['title'],
            'page_subtitle': meta['subtitle'],
        },
    )


def mft(request):
    products = _annotate_products(
        list(MFM.objects.prefetch_related('sizes').all()), 'MFM'
    )
    meta = CATALOG_META['MFM']
    return render(
        request,
        'catalog_list.html',
        {
            'products': products,
            'category_code': 'MFM',
            'page_title': meta['title'],
            'page_subtitle': meta['subtitle'],
        },
    )


def kft(request):
    products = _annotate_products(
        list(KFM.objects.prefetch_related('sizes').all()), 'KFM'
    )
    meta = CATALOG_META['KFM']
    return render(
        request,
        'catalog_list.html',
        {
            'products': products,
            'category_code': 'KFM',
            'page_title': meta['title'],
            'page_subtitle': meta['subtitle'],
        },
    )


def product_detail(request, category, product_id):
    if category not in ('WFM', 'MFM', 'KFM'):
        return HttpResponse('Not found.', status=404)
    product, available_sizes = get_product_and_sizes(category, product_id)
    if not product:
        return HttpResponse('Product not found.', status=404)
    # Ensure the same derived fields as listing pages.
    _annotate_products([product], category)
    meta = CATALOG_META.get(category, {})
    return render(
        request,
        'product_detail.html',
        {
            'product': product,
            'category': category,
            'available_sizes': available_sizes,
            'all_sizes': CATEGORY_SIZES.get(category, []),
            'catalog_title': meta.get('title', 'Catalog'),
        },
    )


@require_POST
def add_to_bag(request):
    if not request.user.is_authenticated:
        return JsonResponse(
            {
                'status': 'error',
                'message': 'Sign in to add items to your bag.',
                'login_url': reverse('login'),
            },
            status=401,
        )
    product_id = request.POST.get('product_id')
    category = request.POST.get('category')
    size = request.POST.get('size')
    if not size:
        return JsonResponse(
            {'status': 'error', 'message': 'Choose a size first.'}, status=400
        )
    try:
        pid = int(product_id)
    except (TypeError, ValueError):
        return JsonResponse({'status': 'error', 'message': 'Invalid product.'}, status=400)
    if category not in ('WFM', 'MFM', 'KFM'):
        return JsonResponse({'status': 'error', 'message': 'Invalid category.'}, status=400)
    product, available_sizes = get_product_and_sizes(category, pid)
    if not product or size not in available_sizes:
        return JsonResponse(
            {'status': 'error', 'message': 'That size is not available.'}, status=400
        )
    bag_item, created = BagItem.objects.get_or_create(
        user=request.user,
        product_id=pid,
        category=category,
        size=size,
        defaults={'quantity': 1},
    )
    if not created:
        bag_item.quantity += 1
        bag_item.save(update_fields=['quantity'])
    return JsonResponse({'status': 'success', 'message': 'Added to bag'})


@login_required
def view_bag(request):
    bag_items = BagItem.objects.filter(user=request.user)
    lines = []
    subtotal = Decimal('0.00')
    for item in bag_items:
        product, _ = get_product_and_sizes(item.category, item.product_id)
        if not product:
            continue
        line_total = Decimal(product.price) * item.quantity
        subtotal += line_total
        lines.append(
            {
                'product': product,
                'quantity': item.quantity,
                'category': item.category,
                'size': item.size,
                'item_id': item.id,
                'line_total': line_total,
            }
        )
    shipping = (
        Decimal('0.00') if subtotal >= FREE_SHIPPING_AT or subtotal == 0 else STANDARD_SHIPPING
    )
    return render(
        request,
        'cart.html',
        {
            'lines': lines,
            'subtotal': subtotal,
            'shipping': shipping,
            'total': subtotal + shipping,
            'free_shipping_at': FREE_SHIPPING_AT,
            'qty_choices': range(1, 11),
        },
    )


@login_required
@require_POST
def remove_from_bag(request, item_id):
    BagItem.objects.filter(id=item_id, user=request.user).delete()
    messages.success(request, 'Removed from bag.')
    return redirect('view_bag')


@login_required
@require_POST
def update_bag_quantity(request, item_id):
    bag_item = get_object_or_404(BagItem, id=item_id, user=request.user)
    try:
        qty = max(1, min(10, int(request.POST.get('quantity', 1))))
    except (TypeError, ValueError):
        qty = 1
    product, _ = get_product_and_sizes(bag_item.category, bag_item.product_id)
    if product:
        stock = (
            product.sizes.filter(size=bag_item.size).values_list('quantity', flat=True).first()
            or 0
        )
        qty = min(qty, max(1, stock))
    bag_item.quantity = qty
    bag_item.save(update_fields=['quantity'])
    messages.success(request, 'Quantity updated.')
    return redirect('view_bag')


@login_required
@require_http_methods(['GET', 'POST'])
def checkout(request):
    bag_items = list(BagItem.objects.filter(user=request.user))
    resolved = []
    subtotal = Decimal('0.00')
    for item in bag_items:
        product, avail = get_product_and_sizes(item.category, item.product_id)
        if not product:
            item.delete()
            continue
        stock = (
            product.sizes.filter(size=item.size).values_list('quantity', flat=True).first() or 0
        )
        if stock < item.quantity:
            item.quantity = stock
            if stock <= 0:
                item.delete()
                messages.warning(
                    request,
                    f'"{product.company}" size {item.size} sold out — removed from bag.',
                )
                continue
            item.save(update_fields=['quantity'])
            messages.warning(request, 'Some quantities were reduced to match stock.')
        line_total = Decimal(product.price) * item.quantity
        subtotal += line_total
        resolved.append(
            {
                'bag_item': item,
                'product': product,
                'line_total': line_total,
            }
        )

    shipping = (
        Decimal('0.00') if subtotal >= FREE_SHIPPING_AT or subtotal == 0 else STANDARD_SHIPPING
    )
    total = subtotal + shipping

    if request.method == 'POST':
        if not resolved:
            messages.error(request, 'Your bag is empty.')
            return redirect('view_bag')
        required = ['fullname', 'phone', 'address', 'pincode']
        if not all(request.POST.get(f) for f in required):
            messages.error(request, 'Fill in all required shipping fields.')
            return redirect('checkout')
        try:
            with transaction.atomic():
                order = Order(
                    user=request.user,
                    fullname=request.POST.get('fullname', '').strip(),
                    phone=request.POST.get('phone', '').strip(),
                    address=request.POST.get('address', '').strip(),
                    landmark=request.POST.get('landmark', '').strip(),
                    pincode=request.POST.get('pincode', '').strip(),
                    subtotal=subtotal,
                    shipping_fee=shipping,
                    total=total,
                    status=Order.Status.CONFIRMED,
                    payment_status=Order.PaymentStatus.PENDING,
                )
                order.save()

                for row in resolved:
                    item = row['bag_item']
                    product = row['product']
                    size_rec = product.sizes.select_for_update().get(size=item.size)
                    if size_rec.quantity < item.quantity:
                        raise ValueError('stock')
                    size_rec.quantity -= item.quantity
                    size_rec.save(update_fields=['quantity'])
                    unit = Decimal(product.price)
                    line_total = unit * item.quantity
                    OrderLine.objects.create(
                        order=order,
                        category=item.category,
                        product_id=item.product_id,
                        product_label=f'{product.company} — {product.model}',
                        size=item.size,
                        quantity=item.quantity,
                        unit_price=unit,
                        line_total=line_total,
                    )
                    item.delete()

                request.session['last_order_id'] = order.id
            return redirect('order_confirmation')
        except Exception:
            messages.error(
                request,
                'Could not place the order — stock may have changed. Refresh your bag and try again.',
            )
            return redirect('view_bag')

    if not resolved and request.method == 'GET':
        messages.info(request, 'Your bag is empty.')
        return redirect('view_bag')

    return render(
        request,
        'checkout.html',
        {
            'lines': resolved,
            'subtotal': subtotal,
            'shipping': shipping,
            'total': total,
            'free_shipping_at': FREE_SHIPPING_AT,
        },
    )


@login_required
@require_http_methods(['GET'])
def order_confirmation(request):
    order_id = request.session.pop('last_order_id', None)
    if not order_id:
        messages.error(request, 'No recent order found.')
        return redirect('index')
    order = get_object_or_404(
        Order.objects.prefetch_related('lines'),
        id=order_id,
        user=request.user,
    )
    return render(request, 'confirmation.html', {'order': order})


@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).prefetch_related('lines')
    return render(request, 'orderhistory.html', {'orders': orders})


@login_required
@require_POST
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    if order.status == Order.Status.CANCELLED:
        messages.info(request, 'This order was already cancelled.')
        return redirect('order_history')
    if order.status not in (Order.Status.CONFIRMED, Order.Status.PENDING_PAYMENT):
        messages.error(request, 'This order can no longer be cancelled online.')
        return redirect('order_history')
    try:
        with transaction.atomic():
            for line in order.lines.all():
                product, _ = get_product_and_sizes(line.category, line.product_id)
                if product:
                    size_rec = product.sizes.select_for_update().get(size=line.size)
                    size_rec.quantity += line.quantity
                    size_rec.save(update_fields=['quantity'])
            order.status = Order.Status.CANCELLED
            order.save(update_fields=['status', 'updated_at'])
        messages.success(request, 'Order cancelled. Items returned to inventory.')
    except Exception:
        messages.error(request, 'Could not cancel this order. Contact support.')
    return redirect('order_history')
