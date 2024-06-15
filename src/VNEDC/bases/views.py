from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render


@login_required
def index(request):
    return render(request, 'bases/index.html', locals())
    #return redirect(reverse('assets_main'))


