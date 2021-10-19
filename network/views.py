from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
import json
from django.views.decorators.csrf import csrf_exempt
from .models import *
from datetime import datetime

import datetime

def index(request):
    posts = Post.objects.order_by('-timestamp').all()
    return render(request, "network/index.html", {'posts': posts})

def auctions(request):
    active_listings = Listing.objects.all().exclude(running=False)
    return render(request, "network/auctions.html",{
        "listings": active_listings
    })


def posts(request):
    posts = Post.objects.order_by('-timestamp').all()
    return JsonResponse([post.serialize() for post in posts], safe=False)


def likes(request):
    user = request.user
    liked = Like.objects.filter(user__exact = user)
    lst = []
    for pos in liked:
        lst.append(pos.post.id)    
    return JsonResponse([r for r in lst], status=201, safe=False)


@csrf_exempt
@login_required
def profile(request,name):
    user = User.objects.get(username=name)
    posts = Post.objects.order_by("-timestamp").filter(user=user)
    return render(request, "network/profile.html", {'posts': posts, 'person': user})


def JSONprofilePosts(request, name):
    user = User.objects.get(username=name)
    posts = Post.objects.order_by("-timestamp").filter(user=user)
    return JsonResponse([post.serialize() for post in posts], status=201, safe=False)


@csrf_exempt
@login_required
def follow(request, name, boo):
    user = request.user
    if boo==1:
        following = User.objects.get(username=name)
        foll = Follow(user=user, following=following)
        foll.save()
    elif boo==0:
        following = User.objects.get(username=name)
        foll = Follow.objects.get(user=user, following=following)
        foll.delete()
    return JsonResponse({'follow': boo}, status=201) 


@csrf_exempt
@login_required
def followed(request,name):
    user = request.user
    try:
        foll = User.objects.get(username=name)
        following = Follow.objects.get(user=user, following=foll)
        return JsonResponse({'followed': True}, status=201)
    except:
        return JsonResponse({'followed': False}, status=201)


def following(request):
    user = request.user
    followed = Follow.objects.all()
    posts = Post.objects.order_by("-timestamp").all()
    lst = []
    for post in posts:
        for foll in followed:
            if user == foll.user and post.user == foll.following:
                lst.append(post)

    
    return render(request, "network/following.html", {'posts': lst})
    
def JSONfollowPosts(request):
    user = request.user
    followed = Follow.objects.all()
    posts = Post.objects.order_by("-timestamp").all()
    lst = []
    for post in posts:
        for foll in followed:
            if user == foll.user and post.user == foll.following:
                lst.append(post)

    return JsonResponse([post.serialize() for post in lst], status=201, safe=False)

    


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")

@csrf_exempt
@login_required
def addpost(request):
    data = json.loads(request.body)
    post = data.get("post")
    user = request.user

    current_post = Post(user=user,post=post)
    current_post.save()

    return JsonResponse(current_post.serialize(), status=201)

@csrf_exempt
@login_required
def addlike(request,id):
    user = request.user
    data = json.loads(request.body)
    active = data.get("active")
    post = Post.objects.get(pk=id)
    if active:
        like = Like(user=user, post=post)
        like.save()
    else:
        like = Like.objects.get(user=user, post=post)
        like.delete()
    return JsonResponse({'active': active},status=201)


@csrf_exempt
@login_required
def getpost(request,ID):
    post = Post.objects.get(pk=ID)
    return JsonResponse(post.serialize(), safe=False)

@csrf_exempt
@login_required
def edit(request, ID):
    data = json.loads(request.body)
    post = data.get('post')
    post = Post.objects.filter(pk=ID).update(post=post)
    return JsonResponse({'post': post}, status=201)



@csrf_exempt
@login_required
def getfollow(request,name):
    user = User.objects.get(username=name)
    foll = Follow.objects.filter(user=user)
    fell = Follow.objects.filter(following=user)

    return JsonResponse({'following': len(foll), 'followers':len(fell)  })



#auctions

def createlisting(request):
    categories = Category.objects.all()
    return render(request, "network/createlisting.html", {
        'categories': categories
    })

@csrf_exempt
def create(request):
    current_user = request.user
    user = User.objects.get(username=current_user)

    try:
        now = datetime.datetime.now()
        time = "Created " + str(now.strftime('%B')) + "." + str(now.day) + ". " + str(now.year) + " " + str(now.strftime('%I:%M:%p'))
        if request.method=="POST":
            data = json.loads(request.body)
            title=data.get('title')
            bid=data.get('bid')
            category=data.get('category')
            category = Category.objects.get(name = category)
            description=data.get('description')
            if data.get('image'): image=data.get('image')
            else: image=None
            listing = Listing(title=title, price=bid, category=category, description=description, image=image, user=user)
            listing.save()
            return HttpResponseRedirect(reverse("auctions"))
    except ValueError:
        return render(request, "network/createlisting.html", {
            'error': True
        })


    
def count_bids(listing):
    bids = Bid.objects.filter(listing__exact = listing)
    if bids: return bids.count()
    else: return 0

def item(request,name):
    if request.user.is_active:
        current_user = request.user
        user = User.objects.get(username=current_user)
        listing = Listing.objects.get(pk=name)
        highest, person = max_biduser(listing)
        ended = not listing.running
        listing.user = listing.user
        if listing.user==user: owner=True
        else: owner=False
        watchList = Watchlist.objects.filter(user=user, listing=listing)
        count = watchList.count()

        if count==0: already=False
        else: already=True

        all_comments = Comment.objects.filter(listing__exact=listing)
        return render(request, "network/item.html",{
            'listing':listing,
            'count': count_bids(listing),
            'comments': all_comments,
            'owner': owner,
            'ended': ended,
            'highest': highest,
            'person': person,
            'already': int(already)
        })
    else:
        return HttpResponseRedirect(reverse("login"))


def max_bid(listing):
    all_bids = []
    bids = Bid.objects.filter(listing__exact = listing)
    for any_bid in bids:
        all_bids.append(any_bid.bid)  
    if all_bids: return max(all_bids)
    else: return listing.price

def max_biduser(listing):
    all_bids = []
    bids = Bid.objects.filter(listing__exact = listing)
    for any_bid in bids:
        all_bids.append(any_bid.bid)  
    if all_bids:
        highest = max(all_bids)
        person = Bid.objects.get(bid=highest, listing=listing)
        return highest, person
    else: return listing.price, listing.user


@csrf_exempt
def bid(request,name):
    listing = Listing.objects.get(pk=name)
    highest_bid = max_bid(listing)

    try:
        data = json.loads(request.body)
        bid = int(data.get("bid"))
        current_user = request.user
        user = User.objects.get(username=current_user)

        if bid <= highest_bid:
            return JsonResponse( {
                    'invalid': False,
                    'less_bid': True,
                    'highest': highest_bid,
                    'count': count_bids(listing)
                })
                
        current_bid = Bid(user=user, bid=bid, listing=listing)
        current_bid.save()

        return JsonResponse({
                        'invalid': False,
                        'less_bid': False,
                        'highest': highest_bid,
                        'count': count_bids(listing),
                        'added': True
                    })
    except:
        return JsonResponse( {
                'invalid': True,
                'highest': highest_bid,
                'count': count_bids(listing),
            })



@csrf_exempt
def listwatch(request,name):
    current_user = request.user
    user = User.objects.get(username=current_user)
    listing = Listing.objects.get(pk=name)
 
    watchlist = Watchlist(user=user, listing=listing)
    watchlist.save()
            
    return HttpResponse(status=201) 



@csrf_exempt
def removewatch(request,name):
    current_user = request.user
    user = User.objects.get(username=current_user)
    listing = Listing.objects.get(pk=name)    
    watchlist = Watchlist.objects.filter(listing__exact=listing, user__exact = user)
    watchlist.delete()
    
    return HttpResponse(status=201)
    

def watch(request):
    try:
        current_user = request.user
        user = User.objects.get(username=current_user)
        watching = Watchlist.objects.filter(user = user).exclude(listing=None)
        if watching:
            return render(request, "network/watchlist.html", {
                'watchlist': watching
            } )
        else:
            return render(request, "network/watchlist.html", {
                'error': True
            })
    except:
        return HttpResponseRedirect(reverse("login"))

@csrf_exempt
def comment(request,name):
    listing = Listing.objects.get(pk=name)
    current_user = request.user
    user = User.objects.get(username=current_user)

    all_comments = Comment.objects.filter(listing__exact=listing)

    data = json.loads(request.body)
    commentTxt = data.get("comment")
    if commentTxt:
        current_comment = Comment(user=user, comment=commentTxt, listing=listing)
        current_comment.save()

    return JsonResponse( [comment.serialize() for comment in all_comments] , safe=False)


def categories(request):
    cats = Category.objects.all()
    return render(request, "network/categories.html", {
        'categories': cats
    })


def viewbycategory(request, name):
    category = Category.objects.get(name = name)
    listings = Listing.objects.filter(category = category)
    return render(request, "network/viewbycategory.html", {
    'listings': listings,
    'category': name
})


def endauction(request, name):
    listing = Listing.objects.get(pk=name)
    listing.running = False
    # highest, person = max_biduser(listing)
    listing.save(update_fields=['running'])
    return HttpResponse(status=201)


def closed(request):
    closed_listings = Listing.objects.all().exclude(running=True)
    return render(request, "network/closed.html",{
        "listings": closed_listings
    })



#mail


def mail(request):

    # Authenticated users view their inbox
    if request.user.is_authenticated:
        return render(request, "network/inbox.html")

    # Everyone else is prompted to sign in
    else:
        return HttpResponseRedirect(reverse("login"))


@csrf_exempt
@login_required
def compose(request):

    # Composing a new email must be via POST
    if request.method != "POST":
        return JsonResponse({"error": "POST request required.", "status":400}, status=400)

    # Check recipient emails
    data = json.loads(request.body)
    emails = [email.strip() for email in data.get("recipients").split(",")]
    if emails == [""]:
        return JsonResponse({
            "error": "At least one recipient required."
        }, status=400)

    # Convert email addresses to users
    recipients = []
    for email in emails:
        try:
            user = User.objects.get(email=email)
            recipients.append(user)
        except User.DoesNotExist:
            return JsonResponse({
                "error": f"User with email {email} does not exist.", "status": 400
            }, status=400)

    # Get contents of email
    subject = data.get("subject", "")
    body = data.get("body", "")

    # Create one email for each recipient, plus sender
    users = set()
    users.add(request.user)
    users.update(recipients)
    for user in users:
        email = Email(
            user=user,
            sender=request.user,
            subject=subject,
            body=body,
            read=user == request.user
        )
        email.save()
        for recipient in recipients:
            email.recipients.add(recipient)
        email.save()

    return JsonResponse({"message": "Email sent successfully.", "status":201 }, status=201)


@login_required
def mailbox(request, mailbox):

    # Filter emails returned based on mailbox
    if mailbox == "inbox":
        emails = Email.objects.filter(
            user=request.user, recipients=request.user, archived=False
        )
    elif mailbox == "sent":
        emails = Email.objects.filter(
            user=request.user, sender=request.user
        )
    elif mailbox == "archive":
        emails = Email.objects.filter(
            user=request.user, recipients=request.user, archived=True
        )
    else:
        return JsonResponse({"error": "Invalid mailbox."}, status=400)

    # Return emails in reverse chronologial order
    emails = emails.order_by("-timestamp").all()
    return JsonResponse([email.serialize() for email in emails], safe=False)


@csrf_exempt
@login_required
def email(request, email_id):

    # Query for requested email
    try:
        email = Email.objects.get(user=request.user, pk=email_id)
    except Email.DoesNotExist:
        return JsonResponse({"error": "Email not found."}, status=404)

    # Return email contents
    if request.method == "GET":
        return JsonResponse(email.serialize())

    # Update whether email is read or should be archived
    elif request.method == "PUT":
        data = json.loads(request.body)
        if data.get("read") is not None:
            email.read = data["read"]
        if data.get("archived") is not None:
            email.archived = data["archived"]
        email.save()
        return HttpResponse(status=204)

    # Email must be via GET or PUT
    else:
        return JsonResponse({
            "error": "GET or PUT request required."
        }, status=400)