from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q


class ThreadManager(models.Manager):
    def by_user(self, user):
        qlookup = Q(first=user) | Q(second=user)
        qlookup2 = Q(first=user) & Q(second=user)
        qs = self.get_queryset().filter(qlookup).exclude(qlookup2).distinct()
        return qs

    def get_or_new(self, user, other_username): # get_or_create
        username = user.username
        if username == other_username:
            return None
        qlookup1 = Q(first__username=username) & Q(second__username=other_username)
        qlookup2 = Q(first__username=other_username) & Q(second__username=username)
        qs = self.get_queryset().filter(qlookup1 | qlookup2).distinct()
        if qs.count() == 1:
            return qs.first(), False
        elif qs.count() > 1:
            return qs.order_by('timestamp').first(), False
        else:
            Klass = user.__class__
            user2 = Klass.objects.get(username=other_username)
            if user != user2:
                obj = self.model(
                        first=user, 
                        second=user2
                    )
                obj.save()
                return obj, True
            return None, False


# Create your models here.
class Thread(models.Model):
    first = models.ForeignKey(User, related_name='thread_first_users', on_delete=models.PROTECT, null=True,blank=True)
    second = models.ForeignKey(User, related_name='thread_second_users', on_delete=models.PROTECT, null=True,blank=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    objects      = ThreadManager()
    @property
    def room_group_name(self):
        return f'chat_{self.id}'

    # def broadcast(self, msg=None):
    #     if msg not None:
    #
    def __str__(self):
        return f'Thread - {self.id}'


class ChatMessage(models.Model):
    thread = models.ForeignKey(Thread, on_delete=models.PROTECT, related_name='thread_chat_messages')
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='user_chat_messages')
    message = models.TextField()
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.id} - {self.user}'
