from django.shortcuts import redirect

def mozo_required(view_func):
    def _wrapped_view_func(request, *args, **kwargs):
        if request.user.TipUsuCod.TipUsuDes != 'Mozo':
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return _wrapped_view_func

def administrador_required(view_func):
    def _wrapped_view_func(request, *args, **kwargs):
        if request.user.TipUsuCod.TipUsuDes != 'Administrador':
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return _wrapped_view_func

def cocinero_required(view_func):
    def _wrapped_view_func(request, *args, **kwargs):
        if request.user.TipUsuCod.TipUsuDes != 'Cocinero':
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return _wrapped_view_func

