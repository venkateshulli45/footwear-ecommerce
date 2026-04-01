from django.db.models import Sum

from .models import BagItem


def bag_summary(request):
    count = 0
    if request.user.is_authenticated:
        agg = BagItem.objects.filter(user=request.user).aggregate(s=Sum('quantity'))
        count = agg['s'] or 0
    return {'bag_item_count': count}
