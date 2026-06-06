from django.contrib.auth.decorators import login_required

from notifications.models import Notification
from django.http import JsonResponse

@login_required
def mark_notifications_read(request):

    Notification.objects.filter(
        user=request.user,
        is_read=False
    ).update(is_read=True)

    return JsonResponse({'success': True})
