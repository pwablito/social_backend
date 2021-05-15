from django.db import models
from django.utils import timezone


class User(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    username = models.CharField(max_length=30)
    password_hash = models.CharField(max_length=30)
    password_salt = models.CharField(max_length=30)
    email = models.EmailField(null=True)
    date_created = models.DateTimeField(default=timezone.now)
    profile_photo = models.ImageField(upload_to='images/profile/', null=True)


class AuthToken(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=20)
    date_issued = models.DateTimeField(default=timezone.now)


class Post(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    caption = models.CharField(max_length=200)
    date_created = models.DateTimeField(default=timezone.now)
    image = models.ImageField(upload_to='images/posts/', null=True)


class Like(models.Model):
    post_id = models.ForeignKey(Post, on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)


class Comment(models.Model):
    post_id = models.ForeignKey(Post, on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.CharField(max_length=200)
    date_created = models.DateTimeField(default=timezone.now)


class Friendship(models.Model):
    first_user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='first_user_id')
    second_user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='second_user_id')
    date_started = models.DateTimeField(default=timezone.now)


class FriendRequest(models.Model):
    initiator_user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='initiator_user_id')
    target_user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='target_user_id')
    date_requested = models.DateTimeField(default=timezone.now)
