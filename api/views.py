from rest_framework.decorators import api_view
from .models import User, AuthToken, Post, Like, Comment, Friendship, FriendRequest
from .utils import generate_unique_string, hash_password, check_friends
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Q
from django.core.files.storage import default_storage
from django.http import JsonResponse
import os
from django.conf import settings


@api_view(['POST'])
def register(request):
    missing_fields = []
    if 'first_name' not in request.data:
        missing_fields.append('first_name')
    if 'last_name' not in request.data:
        missing_fields.append('last_name')
    if 'username' not in request.data:
        missing_fields.append('username')
    if 'password' not in request.data:
        missing_fields.append('password')
    if 'email' not in request.data:
        missing_fields.append('email')
    if len(missing_fields):
        return JsonResponse({
            'success': False,
            'message': 'Some required fields were missing.',
            'missing_fields': missing_fields
        })
    if len(request.data['username']) < 2:
        return JsonResponse({'success': False, 'message': 'Username too short.'})
    if len(request.data['password']) < 5:
        return JsonResponse({'success': False, 'message': 'Password too short.'})
    if len(request.data['first_name']) == 0:
        return JsonResponse({'success': False, 'message': 'First name can not be empty.'})
    if User.objects.all().filter(email=request.data['email']).count() != 0:
        return JsonResponse({'success': False, 'message': 'Email already in use.'})
    if User.objects.all().filter(username=request.data['username']).count() != 0:
        return JsonResponse({'success': False, 'message': 'Username already taken.'})
    salt = generate_unique_string(8)
    hashed_password = hash_password(request.data['password'], salt)
    user = User(
        first_name=request.data['first_name'],
        last_name=request.data['last_name'],
        username=request.data['username'],
        email=request.data['email'],
        password_salt=salt,
        password_hash=hashed_password,
        date_created=datetime.now(tz=timezone.get_current_timezone())
    )
    user.save()
    token = AuthToken(
        user_id=user,
        token=generate_unique_string(20),
        date_issued=datetime.now(tz=timezone.get_current_timezone())
    )
    token.save()
    return JsonResponse({'success': True, 'token': token.token})


@api_view(['POST'])
def login(request):
    missing_fields = []
    if 'username' not in request.data:
        missing_fields.append('username')
    if 'password' not in request.data:
        missing_fields.append('password')
    if len(missing_fields):
        return JsonResponse({
            'success': False,
            'message': 'Some required fields were missing.',
            'missing_fields': missing_fields
        })
    if User.objects.all().filter(username=request.data['username']).count() == 0:
        return JsonResponse({'success': False, 'message': 'Invalid username.'})
    user = User.objects.get(username=request.data['username'])
    salt = user.password_salt
    if hash_password(request.data['password'], salt) != user.password_hash:
        return JsonResponse({'success': False, 'message': 'Incorrect password.'})
    token = AuthToken.objects.get(user_id=user)
    return JsonResponse({'success': True, 'token': token.token})


@api_view(['POST'])
def deleteaccount(request):
    missing_fields = []
    if 'username' not in request.data:
        missing_fields.append('username')
    if 'password' not in request.data:
        missing_fields.append('password')
    if len(missing_fields):
        return JsonResponse({
            'success': False,
            'message': 'Some required fields were missing.',
            'missing_fields': missing_fields
        })
    if User.objects.all().filter(username=request.data['username']).count() == 0:
        return JsonResponse({'success': False, 'message': 'Invalid username.'})
    user = User.objects.get(username=request.data['username'])
    salt = user.password_salt
    if hash_password(request.data['password'], salt) != user.password_hash:
        return JsonResponse({'success': False, 'message': 'Incorrect password.'})
    user.delete()
    return JsonResponse({'success': True})


@api_view(['POST'])
def newpost(request):
    missing_fields = []
    if 'Authorization' not in request.headers:
        return JsonResponse({'success': False, 'message': 'Missing authorization token'})
    if 'caption' not in request.data:
        missing_fields.append('caption')
    if len(missing_fields):
        return JsonResponse({
            'success': False,
            'message': 'Some required fields were missing.',
            'missing_fields': missing_fields
        })
    if AuthToken.objects.all().filter(token=request.headers['Authorization']).count() == 0:
        return JsonResponse({'success': False, 'message': 'Invalid authorization token.'})
    token = AuthToken.objects.get(token=request.headers['Authorization'])
    if Post.objects.all().filter(
            user_id=token.user_id
        ).count() != 0 and datetime.now(tz=timezone.get_current_timezone()) < Post.objects.all().filter(
            user_id=token.user_id
            ).order_by("-date_created")[0].date_created + timedelta(days=1):
        return JsonResponse({'success': False, 'message': 'Must wait 1 day between posts'})
    post = Post(
        user_id=token.user_id,
        caption=request.data['caption'],
        date_created=datetime.now(tz=timezone.get_current_timezone())
    )
    if 'photo' in request.FILES:
        filename = 'images/posts/' + request.FILES['photo'].name + "_" + generate_unique_string(12)
        file_obj = request.FILES['photo']
        with default_storage.open(filename, 'wb+') as destination:
            for chunk in file_obj.chunks():
                destination.write(chunk)
        post.image = filename
    post.save()
    return JsonResponse({'success': True})


@api_view(['POST'])
def deletepost(request):
    if 'Authorization' not in request.headers:
        return JsonResponse({'success': False, 'message': 'Missing authorization token'})
    if 'post_id' not in request.data:
        return JsonResponse({'success': False, 'message': 'Missing post_id.'})
    if AuthToken.objects.all().filter(token=request.headers['Authorization']).count() == 0:
        return JsonResponse({'success': False, 'message': 'Invalid authorization token.'})
    token = AuthToken.objects.get(token=request.headers['Authorization'])
    post = Post.objects.get(id=request.data['post_id'])
    if token.user_id != post.user_id:
        return JsonResponse({'success': False, 'message': 'Post does not belong to this user.'})
    post.delete()
    return JsonResponse({'success': True})


@api_view(['GET'])
def getposts(request):
    if 'Authorization' not in request.headers:
        return JsonResponse({'success': False, 'message': 'Missing authorization token'})
    if AuthToken.objects.all().filter(token=request.headers['Authorization']).count() == 0:
        return JsonResponse({'success': False, 'message': 'Invalid authorization token.'})
    token = AuthToken.objects.get(token=request.headers['Authorization'])
    friendships = Friendship.objects.all().filter(
        Q(first_user_id=token.user_id) | Q(second_user_id=token.user_id)
    )
    raw_posts = Post.objects.all().filter(
        Q(
            user_id=token.user_id
        ) | Q(
            user_id__in=friendships.values_list('first_user_id')
        ) | Q(
            user_id__in=friendships.values_list('second_user_id')
        )
    ).order_by("-date_created")
    posts = []
    for post in raw_posts:
        like_count = Like.objects.all().filter(post_id=post).count()
        self_liked = False
        if Like.objects.all().filter(user_id=token.user_id, post_id=post).count() > 0:
            self_liked = True
        image_url = None
        if post.image:
            image_url = str(post.image)
        posts.append({
            'id': post.id,
            'image_url': image_url,
            'caption': post.caption,
            'posted_by': post.user_id.username,
            'posted_by_id': post.user_id.id,
            'likes': like_count,
            'date': post.date_created,
            'liked': self_liked
        })
    return JsonResponse({'success': True, 'posts': posts})


@api_view(['POST'])
def likepost(request):
    if 'Authorization' not in request.headers:
        return JsonResponse({'success': False, 'message': 'Missing authorization token'})
    if AuthToken.objects.all().filter(token=request.headers['Authorization']).count() == 0:
        return JsonResponse({'success': False, 'message': 'Invalid authorization token.'})
    if 'post_id' not in request.data:
        return JsonResponse({'success': False, 'message': 'Missing post_id.'})
    if Post.objects.all().filter(id=request.data['post_id']).count() == 0:
        return JsonResponse({'success': False, 'message': 'Invalid post_id.'})
    post = Post.objects.get(id=request.data['post_id'])
    token = AuthToken.objects.get(token=request.headers['Authorization'])
    if not check_friends(token.user_id, post.user_id):
        return JsonResponse({'success': False, 'message': 'Must be friends.'})
    if Like.objects.all().filter(user_id=token.user_id, post_id=post).count() != 0:
        return JsonResponse({'success': False, 'message': 'Already liked.'})
    like = Like(user_id=token.user_id, post_id=post)
    like.save()
    return JsonResponse({'success': True})


@api_view(['POST'])
def unlikepost(request):
    if 'Authorization' not in request.headers:
        return JsonResponse({'success': False, 'message': 'Missing authorization token'})
    if AuthToken.objects.all().filter(token=request.headers['Authorization']).count() == 0:
        return JsonResponse({'success': False, 'message': 'Invalid authorization token.'})
    if 'post_id' not in request.data:
        return JsonResponse({'success': False, 'message': 'Missing post_id.'})
    if Post.objects.all().filter(id=request.data['post_id']).count() == 0:
        return JsonResponse({'success': False, 'message': 'Invalid post_id.'})
    post = Post.objects.get(id=request.data['post_id'])
    token = AuthToken.objects.get(token=request.headers['Authorization'])
    if Like.objects.all().filter(user_id=token.user_id, post_id=post).count() == 0:
        return JsonResponse({'success': False, 'message': 'Already not liked.'})
    Like.objects.all().filter(user_id=token.user_id, post_id=post).delete()
    return JsonResponse({'success': True})


@api_view(['POST'])
def newcomment(request):
    if 'Authorization' not in request.headers:
        return JsonResponse({'success': False, 'message': 'Missing authorization token'})
    if AuthToken.objects.all().filter(token=request.headers['Authorization']).count() == 0:
        return JsonResponse({'success': False, 'message': 'Invalid authorization token.'})
    if 'post_id' not in request.data:
        return JsonResponse({'success': False, 'message': 'Missing post_id.'})
    if 'content' not in request.data:
        return JsonResponse({'success': False, 'message': 'Missing content.'})
    if Post.objects.all().filter(id=request.data['post_id']).count() == 0:
        return JsonResponse({'success': False, 'message': 'Invalid post_id.'})
    post = Post.objects.get(id=request.data['post_id'])
    token = AuthToken.objects.get(token=request.headers['Authorization'])
    if not check_friends(token.user_id, post.user_id):
        return JsonResponse({'success': False, 'message': 'Must be friends.'})
    comment = Comment(
        user_id=token.user_id,
        post_id=post,
        content=request.data['content'],
        date_created=datetime.now(tz=timezone.get_current_timezone()),
    )
    comment.save()
    return JsonResponse({'success': True})


@api_view(['POST'])
def deletecomment(request):
    if 'Authorization' not in request.headers:
        return JsonResponse({'success': False, 'message': 'Missing authorization token'})
    if AuthToken.objects.all().filter(token=request.headers['Authorization']).count() == 0:
        return JsonResponse({'success': False, 'message': 'Invalid authorization token.'})
    if 'comment_id' not in request.data:
        return JsonResponse({'success': False, 'message': 'Missing post_id.'})
    if Comment.objects.all().filter(id=request.data['comment_id']).count() == 0:
        return JsonResponse({'success': False, 'message': 'Invalid comment_id.'})
    comment = Comment.objects.get(id=request.data['comment_id'])
    token = AuthToken.objects.get(token=request.headers['Authorization'])
    if comment.user_id != token.user_id and comment.user_id:
        return JsonResponse({
            'success': False,
            'message': 'Comment does not belong to this user or the owner of this post.'
        })
    comment.delete()
    return JsonResponse({'success': True})


@api_view(['POST'])
def getcomments(request):
    if 'Authorization' not in request.headers:
        return JsonResponse({'success': False, 'message': 'Missing authorization token'})
    if AuthToken.objects.all().filter(token=request.headers['Authorization']).count() == 0:
        return JsonResponse({'success': False, 'message': 'Invalid authorization token.'})
    if 'post_id' not in request.data:
        return JsonResponse({'success': False, 'message': 'Missing post_id'})
    if Post.objects.all().filter(id=request.data['post_id']).count() == 0:
        return JsonResponse({'success': False, 'message': 'Post does not exist'})
    post = Post.objects.get(id=request.data['post_id'])
    token = AuthToken.objects.get(token=request.headers['Authorization'])
    comments = []
    if check_friends(token.user_id, post.user_id):
        for comment in Comment.objects.all().filter(post_id=post).order_by("date_created"):
            comments.append({
                'id': comment.id,
                'user_id': comment.user_id.id,
                'username': User.objects.get(id=comment.user_id.id).username,
                'content': comment.content,
            })
    return JsonResponse({'success': True, 'comments': comments})


@api_view(['POST'])
def requestfriend(request):
    if 'Authorization' not in request.headers:
        return JsonResponse({'success': False, 'message': 'Missing authorization token'})
    if AuthToken.objects.all().filter(token=request.headers['Authorization']).count() == 0:
        return JsonResponse({'success': False, 'message': 'Invalid authorization token.'})
    if 'friend_user_id' not in request.data:
        return JsonResponse({'success': False, 'message': 'Missing friend_user_id.'})
    if User.objects.all().filter(id=request.data['friend_user_id']).count() == 0:
        return JsonResponse({'success': False, 'message': 'Invalid friend_user_id.'})
    token = AuthToken.objects.get(token=request.headers['Authorization'])
    friend = User.objects.get(id=request.data['friend_user_id'])
    if check_friends(friend.id, token.user_id):
        return JsonResponse({'success': False, 'message': 'Already friends'})
    if FriendRequest.objects.all().filter(initiator_user_id=token.user_id, target_user_id=friend.id).count() != 0:
        return JsonResponse({'success': False, 'message': 'Already requested.'})
    if FriendRequest.objects.all().filter(initiator_user_id=friend.id, target_user_id=token.user_id).count() != 0:
        return JsonResponse({'success': False, 'message': 'This user already requested to be your friend.'})
    friend_request = FriendRequest(
        initiator_user_id=token.user_id,
        target_user_id=friend,
        date_requested=datetime.now(tz=timezone.get_current_timezone()),
    )
    friend_request.save()
    return JsonResponse({'success': True})


@api_view(['POST'])
def acceptfriendrequest(request):
    if 'Authorization' not in request.headers:
        return JsonResponse({'success': False, 'message': 'Missing authorization token'})
    if AuthToken.objects.all().filter(token=request.headers['Authorization']).count() == 0:
        return JsonResponse({'success': False, 'message': 'Invalid authorization token.'})
    if 'friend_request_id' not in request.data:
        return JsonResponse({'success': False, 'message': 'Missing friend_request_id.'})
    if FriendRequest.objects.all().filter(id=request.data['friend_request_id']).count() == 0:
        return JsonResponse({'success': False, 'message': 'Invalid friend_request_id.'})
    token = AuthToken.objects.get(token=request.headers['Authorization'])
    friend_request = FriendRequest.objects.get(id=request.data['friend_request_id'])
    if token.user_id != friend_request.target_user_id:
        return JsonResponse({'success': False, 'message': 'User does not match requested friend.'})
    friendship = Friendship(
        first_user_id=friend_request.initiator_user_id,
        second_user_id=friend_request.target_user_id,
        date_started=datetime.now(tz=timezone.get_current_timezone()),
    )
    friendship.save()
    friend_request.delete()
    return JsonResponse({'success': True})


@api_view(['POST'])
def deletefriendrequest(request):
    if 'Authorization' not in request.headers:
        return JsonResponse({'success': False, 'message': 'Missing authorization token'})
    if AuthToken.objects.all().filter(token=request.headers['Authorization']).count() == 0:
        return JsonResponse({'success': False, 'message': 'Invalid authorization token.'})
    if 'friend_request_id' not in request.data:
        return JsonResponse({'success': False, 'message': 'Missing friend_request_id.'})
    if FriendRequest.objects.all().filter(id=request.data['friend_request_id']).count() == 0:
        return JsonResponse({'success': False, 'message': 'Invalid friend_request_id.'})
    token = AuthToken.objects.get(token=request.headers['Authorization'])
    friend_request = FriendRequest.objects.get(id=request.data['friend_request_id'])
    if token.user_id != friend_request.target_user_id and token.user_id != friend_request.initiator_user_id:
        return JsonResponse({'success': False, 'message': 'This user is not allowed to delete this request'})
    friend_request.delete()
    return JsonResponse({'success': True})


@api_view(['GET'])
def getfriendrequestsincoming(request):
    if 'Authorization' not in request.headers:
        return JsonResponse({'success': False, 'message': 'Missing authorization token'})
    if AuthToken.objects.all().filter(token=request.headers['Authorization']).count() == 0:
        return JsonResponse({'success': False, 'message': 'Invalid authorization token.'})
    token = AuthToken.objects.get(token=request.headers['Authorization'])
    raw_friend_requests = FriendRequest.objects.all().filter(target_user_id=token.user_id)
    friend_requests = []
    for friend_request in raw_friend_requests:
        friend_requests.append({
            'id': friend_request.id,
            'from_username': friend_request.initiator_user_id.username,
            'from_id': friend_request.initiator_user_id.id
        })
    return JsonResponse({'success': True, 'friend_requests': friend_requests})


@api_view(['GET'])
def getfriendrequestsoutgoing(request):
    if 'Authorization' not in request.headers:
        return JsonResponse({'success': False, 'message': 'Missing authorization token'})
    if AuthToken.objects.all().filter(token=request.headers['Authorization']).count() == 0:
        return JsonResponse({'success': False, 'message': 'Invalid authorization token.'})
    token = AuthToken.objects.get(token=request.headers['Authorization'])
    raw_friend_requests = FriendRequest.objects.all().filter(initiator_user_id=token.user_id)
    friend_requests = []
    for friend_request in raw_friend_requests:
        friend_requests.append({
            'id': friend_request.id,
            'to_username': friend_request.target_user_id.username,
            'to_id': friend_request.target_user_id.id
        })
    return JsonResponse({'success': True, 'friend_requests': friend_requests})


@api_view(['POST'])
def deletefriendship(request):
    if 'Authorization' not in request.headers:
        return JsonResponse({'success': False, 'message': 'Missing authorization token'})
    if AuthToken.objects.all().filter(token=request.headers['Authorization']).count() == 0:
        return JsonResponse({'success': False, 'message': 'Invalid authorization token.'})
    if 'friend_user_id' not in request.data:
        return JsonResponse({'success': False, 'message': 'Missing friend_user_id.'})
    if User.objects.all().filter(id=request.data['friend_user_id']).count() == 0:
        return JsonResponse({'success': False, 'message': 'Invalid friend_user_id.'})
    token = AuthToken.objects.get(token=request.headers['Authorization'])
    friend = User.objects.get(id=request.data['friend_user_id'])
    if Friendship.objects.all().filter(
        Q(
            first_user_id=friend.id,
            second_user_id=token.user_id
        ) | Q(
            first_user_id=token.user_id,
            second_user_id=friend.id
        )
    ).count() == 0:
        return JsonResponse({'success': False, 'message': 'Already not friends.'})
    Friendship.objects.all().filter(Q(first_user_id=friend.id) | Q(second_user_id=friend.id)).delete()
    return JsonResponse({'success': True})


@api_view(['POST'])
def getprofile(request):
    if 'Authorization' not in request.headers:
        return JsonResponse({'success': False, 'message': 'Missing authorization token'})
    if AuthToken.objects.all().filter(token=request.headers['Authorization']).count() == 0:
        return JsonResponse({'success': False, 'message': 'Invalid authorization token.'})
    token = AuthToken.objects.get(token=request.headers['Authorization'])
    user_id = token.user_id
    if 'user_id' in request.data:
        if User.objects.all().filter(id=request.data['user_id']).count() == 0:
            return JsonResponse({'success': False, 'message': 'Invalid user_id.'})
        user_id = User.objects.get(id=request.data['user_id'])
    user = User.objects.get(id=user_id.id)
    friend_count = Friendship.objects.all().filter(
        Q(first_user_id=user_id.id) | Q(second_user_id=user_id.id)
    ).count()
    response = {
        'username': user.username,
        'id': user.id,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'friend_count': friend_count,
        'friends': check_friends(token.user_id.id, user.id),
    }
    if user.profile_photo:
        response['profile_photo'] = user.profile_photo
    if response['friends']:
        response['posts'] = []
        for post in Post.objects.all().filter(user_id=user_id.id).order_by("-date_created"):
            like_count = Like.objects.all().filter(post_id=post).count()
            self_liked = False if Like.objects.all().filter(post_id=post, user_id=token.user_id).count() == 0 else True
            image_url = None
            if post.image:
                image_url = str(post.image)
            response['posts'].append({
                'id': post.id,
                'caption': post.caption,
                'posted_by': post.user_id.username,
                'posted_by_id': post.user_id.id,
                'likes': like_count,
                'date': post.date_created,
                'liked': self_liked,
                'image_url': image_url,
            })
    return JsonResponse(response)


@api_view(['POST'])
def searchpeople(request):
    if 'Authorization' not in request.headers:
        return JsonResponse({'success': False, 'message': 'Missing authorization token'})
    if AuthToken.objects.all().filter(token=request.headers['Authorization']).count() == 0:
        return JsonResponse({'success': False, 'message': 'Invalid authorization token.'})
    # token = AuthToken.objects.get(token=request.headers['Authorization'])
    if 'search_value' not in request.data:
        return JsonResponse({'success': False, 'message': 'Missing search_value'})
    if request.data['search_value'] == '':
        return JsonResponse({'success': True, 'users': []})
    users = User.objects.all().filter(username__contains=request.data['search_value'])
    return_users = []
    for user in users:
        return_users.append({
            'username': user.username,
            'id': user.id,
            'first_name': user.first_name,
            'last_name': user.last_name,
        })
    return JsonResponse({'success': True, 'users': return_users})


@api_view(['POST'])
def updateprofilephoto(request):
    if 'Authorization' not in request.headers:
        return JsonResponse({'success': False, 'message': 'Missing authorization token'})
    if AuthToken.objects.all().filter(token=request.headers['Authorization']).count() == 0:
        return JsonResponse({'success': False, 'message': 'Invalid authorization token.'})
    token = AuthToken.objects.get(token=request.headers['Authorization'])
    user = token.user_id
    filename = os.path.join(settings.MEDIA_ROOT, 'images/profile/', user.username)
    if 'photo' in request.FILES:
        file_obj = request.FILES['photo']
        with default_storage.open(filename, 'wb+') as destination:
            for chunk in file_obj.chunks():
                destination.write(chunk)
        user.profile_photo = filename
    else:
        os.remove(filename)
        user.profile_photo = None
    user.save()
    return JsonResponse({'success': True})
