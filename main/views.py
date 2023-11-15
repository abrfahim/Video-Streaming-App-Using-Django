from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.models import User
from .models import VideoPost, Comment, UserData
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist


# Create your views here.
def home(request):
    if not request.user.is_authenticated:
        demo_videos = VideoPost.objects.all().order_by('-id')[:5]
        params = {'videos': demo_videos}
        return render(request, 'welcome.html', params)
    else:
        all_videos = VideoPost.objects.all().order_by('-id')
        params = {'all_videos': all_videos}
        return render(request, 'home.html', params)


def search(request):
    query = request.GET['search_query']
    try:
        user_obj = User.objects.filter(username__icontains=query)
    except:
        user_obj = User.objects.none()
    params = {'user_obj': user_obj}

    return render(request, 'search_page.html', params)


def upload_video(request):
    if request.method == 'POST':
        title = request.POST['title']
        desc = request.POST['desc']
        video_file = request.FILES['fileName']
        thumb_nail = request.FILES['thumbnail_img']
        cate = request.POST['category']
        user_obj = User.objects.get(username=request.user)
        upload_video = VideoPost(user=user_obj, title=title, desc=desc, video_file=video_file, thumbnail=thumb_nail,
                                 category=cate)
        upload_video.save()
        messages.success(request, 'Video has been uploaded.')

    return render(request, 'upload_video.html')


def watch_video(request, video_id):
    try:
        video_obj = VideoPost.objects.get(id=video_id)
    except ObjectDoesNotExist:
        return render(request, '404.html')
    try:
        session_obj = User.objects.get(username=request.user.username)
    except:
        messages.warning(request, 'Login to watch this video.')
        return redirect('home')

    video_comments = Comment.objects.filter(post=video_obj).order_by('-id')

    # Increase Views of Video if User visit this page

    if request.user not in video_obj.video_views.all():
        video_obj.video_views.add(request.user)

    # Increase Likes of Video if User like this video

    is_liked = False
    if session_obj in video_obj.likes.all():
        is_liked = True
    else:
        is_liked = False
    params = {'video': video_obj, 'comments': video_comments, 'is_liked': is_liked}
    return render(request, 'watch_video.html', params)


def add_comment(request):
    if request.method == 'GET':
        video_id = request.GET['video_id']
        comment = request.GET['comment_text']
        video_obj = VideoPost.objects.get(id=video_id)
        session_obj = User.objects.get(username=request.user.username)
        video_comments = Comment.objects.filter(post=video_obj).order_by('-id')
        create_comment = Comment.objects.create(post=video_obj, user=session_obj, comment=comment)
        create_comment.save()

    return JsonResponse({'comment': create_comment.comment, 'count_comments': video_comments.count()})


def add_like(request, video_id):
    user_obj = User.objects.get(username=request.user.username)
    video_obj = VideoPost.objects.get(id=video_id)
    is_liked = False
    if user_obj in video_obj.likes.all():
        video_obj.likes.remove(user_obj)
        is_liked = True
    else:
        video_obj.likes.add(user_obj)
        is_liked = False
    return JsonResponse({'is_liked': is_liked, 'likes_count': video_obj.likes.all().count()})


def profile(request, session_username):
    try:
        session_obj = User.objects.get(username=session_username)
    except:
        return render(request, '404.html')
    profile_data = UserData.objects.get_or_create(user=session_obj)[0]
    user_posts = VideoPost.objects.filter(user=session_obj).order_by('-id')

    # Category wise Posts

    video_cat_science = VideoPost.objects.filter(user=session_obj, category='Science & Technology').order_by('-id')
    video_cat_blogs = VideoPost.objects.filter(user=session_obj, category='Blogs').order_by('-id')
    video_cat_fashion = VideoPost.objects.filter(user=session_obj, category='Fashion').order_by('-id')
    video_cat_education = VideoPost.objects.filter(user=session_obj, category='Education').order_by('-id')
    video_cat_food = VideoPost.objects.filter(user=session_obj, category='Food').order_by('-id')

    subscribed = False
    if request.user in profile_data.subscribers.all():
        subscribed = True
    else:
        subscribed = False
    params = {'subscribed': subscribed, 'session_obj': session_obj, 'user_data': profile_data, 'videos': user_posts,
              'sci': video_cat_science, 'blogs': video_cat_blogs, 'fashion': video_cat_fashion,
              'edu': video_cat_education, 'food': video_cat_food}
    return render(request, 'profile.html', params)


def dashboard(request, session_username):
    user_videos = VideoPost.objects.filter(user__username=request.user.username).order_by('-id')
    user_data = UserData.objects.get_or_create(user=User.objects.get(username=request.user.username))[0]
    user_video_likes = 0
    user_videos_views = 0

    for video in user_videos:
        user_video_likes += video.likes.count()
        user_videos_views += video.video_views.count()

    params = {'videos': user_videos, 'user_data': user_data, 'total_likes': user_video_likes,
              'total_views': user_videos_views}
    return render(request, 'dashboard.html', params)


def add_sub(request, viewer):
    viewer_obj = UserData.objects.get_or_create(user=User.objects.get(username=viewer))[0]
    subscriber_obj = User.objects.get(username=request.user.username)

    subscribed = False
    if subscriber_obj in viewer_obj.subscribers.all():
        viewer_obj.subscribers.remove(subscriber_obj)
        subscribed = True
    else:
        viewer_obj.subscribers.add(subscriber_obj)
        subscribed = False

    return JsonResponse({'is_subscribed': subscribed, 'viewer_obj': viewer_obj.subscribers.all().count()})


def edit_video(request, video_id):
    if request.method == 'POST':
        new_title = request.POST['new_title']
        new_desc = request.POST['new_desc']
        new_cate = request.POST['new_cate']

        video_obj = VideoPost.objects.get(id=video_id)
        video_obj.title = new_title
        video_obj.desc = new_desc
        video_obj.category = new_cate
        video_obj.save()

        return HttpResponseRedirect(reverse('dashboard', args=[str(request.user.username)]))
    else:
        return HttpResponse('get')


def update_details(request):
    if request.method == 'POST':
        user_data = UserData.objects.get(user=request.user)

        aboutText = request.POST['about_text']
        try:
            imgFile = request.FILES['img_field']
            if imgFile:
                user_data.profile_pic = imgFile

        except:
            print('some error occurred')

        user_data.about = aboutText
        user_data.save()

        return HttpResponseRedirect(reverse('dashboard', args=[str(request.user.username)]))
    return redirect('dashboard')


def delete_video(request):
    if request.method == 'GET':
        vid = request.GET['videoId']
        video_obj = VideoPost.objects.get(id=vid)
        video_obj.delete()

        user_videos = VideoPost.objects.filter(user__username=request.user.username)
        user_video_likes = 0
        for video in user_videos:
            user_video_likes += video.likes.count()
        return JsonResponse({'video_id': vid, 'videosCount': user_videos.count(), 'videosLikes': user_video_likes})
    else:
        return JsonResponse({'status': 'not ok'})

def signup(request):
    if request.method == 'POST':
        first_name = request.POST['fname']
        last_name = request.POST['lname']
        username = request.POST['username']
        mail = request.POST['mail']
        pwd = request.POST['pwd']

        try:
            new_user = User.objects.create_user(f'{username.lower()}', mail, pwd)
            new_user.first_name = first_name
            new_user.last_name = last_name
            new_user.save()
            messages.warning(request, 'Account has been created successfully.')
        except:
            messages.warning(request, 'Username is already exist.')

    return redirect('home')


def user_login(request):
    if not request.user.is_authenticated:

        if request.method == 'POST':
            uname = request.POST['uname'].lower()
            pwd = request.POST['pwd']

            check_user = authenticate(username=uname, password=pwd)
            if check_user is not None:
                login(request, check_user)
                return redirect('home')
            else:
                messages.warning(request, 'Invalid Username or Password.')
                return redirect('home')
        return redirect('home')

    else:
        return redirect('home')


def user_logout(request):
    logout(request)
    return redirect('home')

