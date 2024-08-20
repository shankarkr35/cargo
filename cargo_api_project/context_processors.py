from apps.support.models import Support
  
def user_support(request):
    try:
        support_data = Support.objects.get(id=1)
        
        my_cart_data = {
            'support_data': support_data,
        } 
        return my_cart_data
    except Support.DoesNotExist:
        return {'support_data': None}