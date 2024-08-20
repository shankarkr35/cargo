from django.shortcuts import render,redirect
        
def auth_middleware(get_response):
    # one time integration
    def middleware(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_admin:
            response = get_response(request, *args, **kwargs)
            return response
        else:
            return redirect('/auth/admin-login')
        
    return middleware

 
def auth_courier_middleware(get_response):
    # one time integration
    def courier_middleware(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_courier:
            response = get_response(request, *args, **kwargs)
            return response
            
        else:
            return redirect('/courier-login/')
        
 
    return courier_middleware