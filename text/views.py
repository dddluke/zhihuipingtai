from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
# def edit_blog(request):
#     return None
from text.models import Blog


def edit_blog(request):
    return render(request, 'Rich.html')


def publish(request):
    if request.method == 'POST':

        s = request.POST.get('sBlog')
        # blog = Blog()
        # blog.sBlog = s
        # blog.save()
        post = Blog.objects.create(title='test4', sBlog=s)
        print(s)
        if post:
            return HttpResponse('ok')
    return render(request, 'post.html')


def show_post(request):
    post = Blog.objects.get(pk=8)
    return render(request, 'post.html', locals())