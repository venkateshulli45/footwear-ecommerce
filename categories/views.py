from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from django.db import transaction
from .models import WFM, MFM, KFM, WFMSizeAvailability, MFMSizeAvailability, KFMSizeAvailability, Purchase,BagItem
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.urls import reverse


CATEGORY_SIZES = {
    'MFM': ['6', '7', '8', '9', '10'],
    'WFM': ['4', '5', '6', '7', '8'],
    'KFM': ['1', '2', '3', '4', '5'],
}


def get_product_and_sizes(category, product_id):
    model_map = {
        'WFM': (WFM, WFMSizeAvailability),
        'MFM': (MFM, MFMSizeAvailability),
        'KFM': (KFM, KFMSizeAvailability),
    }
    
    if category in model_map:
        ProductModel, SizeModel = model_map[category]
        try:
            product = ProductModel.objects.get(id=product_id)
            available_sizes = product.sizes.filter(quantity__gt=0).values_list('size', flat=True)
            return product, list(available_sizes)
        except ProductModel.DoesNotExist:
            return None, []
    return None, []

@require_http_methods(["GET", "POST"])
def confirm_purchase(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        category = request.POST.get('category')
        selected_size = request.POST.get('size')
        
        if product_id and 'fullname' not in request.POST:
            product, available_sizes = get_product_and_sizes(category, product_id)
            
            if product:
                context = {
                    'product': product,
                    'category': category,
                    'available_sizes': available_sizes,
                    'all_sizes': CATEGORY_SIZES.get(category, []),
                    'selected_size': selected_size
                }
                return render(request, 'buypage.html', context)
            return HttpResponse("Product not found.", status=404)
        
     
        elif all(field in request.POST for field in ['fullname', 'phone', 'address', 'pincode']):
            product, available_sizes = get_product_and_sizes(category, product_id)
            
            if not product:
                return HttpResponse("Product not found.", status=404)
            
            if str(selected_size) not in available_sizes:
                return HttpResponse("Selected size is not available.", status=400)
            
            try:
                with transaction.atomic():
                    size_record = product.sizes.get(size=selected_size)
                    if size_record.quantity < 1:
                        return HttpResponse("This size is out of stock.", status=400)
                    
                    size_record.quantity -= 1
                    size_record.save()
                    
                    purchase = Purchase.objects.create(
                        user=request.user,
                        fullname=request.POST.get('fullname'),
                        size=selected_size,
                        phone=request.POST.get('phone'),
                        address=request.POST.get('address'),
                        landmark=request.POST.get('landmark', ''),
                        pincode=request.POST.get('pincode'),
                        product=f"{product.company} - {product.articleno} (Size {selected_size})"
                    )
                    
                    
                    request.session['purchase_id'] = purchase.id
                    return redirect('purchase_confirmation')
            except Exception as e:
                return HttpResponse(f"An error occurred while processing your purchase: {str(e)}", status=500)
    
    return HttpResponse("Invalid request method.", status=405)

@require_http_methods(["GET"])
def purchase_confirmation(request):
    purchase_id = request.session.pop('purchase_id', None)
    if purchase_id:
        try:
            purchase = Purchase.objects.get(id=purchase_id)
            product_info = purchase.product.split(' - ')
            company = product_info[0]
            articleno = product_info[1].split(' (Size')[0]
            
            context = {
                'purchase': purchase,
                'product': {'company': company, 'articleno': articleno}
            }
            return render(request, 'confirmation.html', context)
        except Purchase.DoesNotExist:
            messages.error(request, "Purchase information not found.")
    else:
        messages.error(request, "No recent purchase found.")
    
    return redirect('index')

@login_required
def order_history(request):
 
    orders = Purchase.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orderhistory.html', {'orders': orders})



@login_required
def add_to_bag(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        category = request.POST.get('category')
        size = request.POST.get('size')
        
        if not size:
            return JsonResponse({'status': 'error', 'message': 'Size is required'}, status=400)
        
        bag_item, created = BagItem.objects.get_or_create(
            user=request.user,
            product_id=product_id,
            category=category,
            size=size
        )
        
        if not created:
            bag_item.quantity += 1
            bag_item.save()
        
        return JsonResponse({'status': 'success', 'message': 'Item added to bag'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

@login_required
def view_bag(request):
    bag_items = BagItem.objects.filter(user=request.user)
    products = []
    
    for item in bag_items:
        product, _ = get_product_and_sizes(item.category, item.product_id)
        if product:
            products.append({
                'product': product,
                'quantity': item.quantity,
                'category': item.category,
                'size': item.size,
                'item_id': item.id
            })
    
    return render(request, 'addtobag.html', {'products': products})

@login_required
def remove_from_bag(request, item_id):
    try:
        bag_item = BagItem.objects.get(id=item_id, user=request.user)
        bag_item.delete()
        messages.success(request, 'Item removed from bag successfully.')
    except BagItem.DoesNotExist:
        messages.error(request, 'Item not found in your bag.')
    
    return redirect('view_bag')



def wft(request):
    products = WFM.objects.prefetch_related('sizes').all()
    for product in products:
        available_sizes = [
            size.size for size in product.sizes.filter(quantity__gt=0)
        ]
        product.set_available_sizes(available_sizes)
    return render(request, 'womenchappals.html', {'wm': products})

def mft(request):
    products = MFM.objects.prefetch_related('sizes').all()
    for product in products:
        available_sizes = [
            size.size for size in product.sizes.filter(quantity__gt=0)
        ]
        product.set_available_sizes(available_sizes)
    return render(request, 'mencollection.html', {'mm': products})

def kft(request):
    products = KFM.objects.prefetch_related('sizes').all()
    for product in products:
        available_sizes = [
            size.size for size in product.sizes.filter(quantity__gt=0)
        ]
        product.set_available_sizes(available_sizes)
    return render(request, 'kidschappals.html', {'km': products})
