from django.db import models


class Shop(models.Model):
    title = models.CharField(max_length=200)
    email = models.EmailField()
    created_date = models.DateTimeField('created_at')

    def __str__(self):
        return self.title


class Product(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=200, null=True, blank=True)
    price = models.PositiveIntegerField()
    rating = models.IntegerField(default=0)

    def __str__(self):
        return self.title


class Post(models.Model):
    title = models.CharField(max_length=100)
    text = models.CharField(max_length=1000)

    def __str__(self):
        return self.title


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, default=0)
    text = models.CharField(max_length=200)

    def __str__(self):
        return self.text
