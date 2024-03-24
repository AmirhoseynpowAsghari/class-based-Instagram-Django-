from .models import Message  # Import your Message model here

def directs_context_processor(request):
    directs_count = 0
    if request.user.is_authenticated:
        directs_count = Message.objects.filter(user=request.user, is_read=False).count()
    return {'directs_count': directs_count}
