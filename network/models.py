from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    pass

class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.CharField(max_length=999)
    timestamp = models.DateTimeField(auto_now_add=True)

    def likes(self):
        return Like.objects.filter(post=self.id).count()

    def serialize(self):
        ap = ""
        T = self.timestamp.strftime("%p")
        if T=="AM": ap = 'a.m.'
        else: ap = 'p.m.' 
        likes = Like.objects.filter(post=self.id).count()
        return {'user':self.user.username,'id': self.id, 'post': self.post, 'timestamp': self.timestamp.strftime("%B %d, %Y, %I:%M ") + ap, 'likes': likes}


class Like(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    post = models.ForeignKey(Post,on_delete=models.CASCADE)


class Follow(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE, related_name='user')
    following = models.ForeignKey(User, on_delete=models.CASCADE)

class Category(models.Model):
    name = models.CharField(max_length=64)

class Listing(models.Model):
    title = models.CharField(max_length=64)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    description = models.CharField(max_length=164)
    image = models.CharField(max_length=900)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    price = models.FloatField()
    running = models.BooleanField(default=True)
    
class Bid(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    bid = models.FloatField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.CharField(max_length=164)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, default="")

    def serialize(self):
        return {'user':self.user.username,'id': self.id, 'comment': self.comment, 'listing': self.listing.id}


class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, null=True)


class Email(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="emails")
    sender = models.ForeignKey(User, on_delete=models.PROTECT, related_name="emails_sent")
    recipients = models.ManyToManyField(User, related_name="emails_received")
    subject = models.CharField(max_length=255)
    body = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
    archived = models.BooleanField(default=False)

    def serialize(self):
        return {
            "id": self.id,
            "sender": self.sender.email,
            "recipients": [user.email for user in self.recipients.all()],
            "subject": self.subject,
            "body": self.body,
            "timestamp": self.timestamp.strftime("%b %d %Y, %I:%M %p"),
            "read": self.read,
            "archived": self.archived
        }
