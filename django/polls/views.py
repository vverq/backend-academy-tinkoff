from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.core.paginator import Paginator

from polls.models import Shop, Product, Post, Comment

def resume(request):
    return render(request, 'resume.html', {})

def index(request):
    posts = Post.objects.all()

    context = {
        "count_comments": {post: Comment.objects.filter(post_id=post.id).count() for post in posts}
    }
    return render(request, 'index.html', context)


def post(request, post_id):
    comments = Comment.objects.filter(post_id=post_id)
    paginator = Paginator(comments, 2)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        "comments": page_obj,
        "post": Post.objects.get(id=post_id)
    }

    return render(request, 'post.html', context)

def create_comment(request, post_id):
    if request.method == "POST":
        text = request.POST['text']
        comment = Comment.objects.create(text=text, post_id=post_id)
        comment.save()
        return redirect("post", post_id=post_id)

    return render(request, 'create_comment.html', {})


def create_post(request):
    if request.method == "POST":
        title = request.POST['title']
        text = request.POST['text']
        post = Post.objects.create(title=title, text=text)
        post.save()
        return redirect("index")

    return render(request, 'create_post.html', {})

def shop_list(request):
    products = Product.objects.all()

    context = {
        "shop_list": Shop.objects.all(),
        "product": {
            "title_x": [p.title for p in products],
            "price_y": [p.price for p in products]
        }
    }

    return render(request, 'shop/shops.html', context)
