from django.contrib.auth.decorators import login_required
from django.shortcuts import render

def test(request):

    return render(request, 'chart/test.html', locals())