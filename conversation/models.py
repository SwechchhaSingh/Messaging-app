from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404


class MyUserManager(BaseUserManager):
    def create_user(self, email, password=None):
        """
        Creates and saves a User with the given email, and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        """
        Creates and saves a superuser with the given email, and password.
        """
        user = self.create_user(email,
            password=password,
        )

        user.is_superuser = True
        user.save(using=self._db)
        return user


class MyUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = MyUserManager()

    USERNAME_FIELD = 'email'

    def __unicode__(self):
        return self.email

    def get_full_name(self):
        # The user is identified by their email address
        return self.email

    def get_short_name(self):
        # The user is identified by their email address
        return self.email

    @property
    def is_staff(self):
        # "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_superuser


class MessageManager(models.Manager):

    def save(self, sender, content, receiver_list=None, thread_id=None):
        if thread_id:
            thread = Thread.objects.get(id=thread_id)  # Generate a new thread
        else:
            if receiver_list:
                thread = self.new_thread()
                for receiver in receiver_list:
                    user = get_user_model().objects.get(email=receiver)
                    thread.participants.add(user)  # Add each recipient user in thread participants
                thread.participants.add(sender)
            else:
                raise ValidationError([
                    ValidationError('Both thread_id and receivers_list cannot be None', code='CustomError'), ])
        message = self.model(sender=sender, content=content)  # Create a new message
        message.thread = thread  # Associate currently created message to currently generated thread
        message.save(using=self._db)
        return message

    def new_thread(self):
        thread = Thread()
        thread.save(using=self._db)  # New thread generation
        return thread


mgr = MessageManager()
mgr.use_for_related_fields = True


class Thread(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    participants = models.ManyToManyField(MyUser, related_name='threads')

    objects = MessageManager()

    def get_participants(self):
        return ",\n".join([s.email for s in self.participants.all()])

    # def __unicode__(self):
    #     return str(self.id)


class Message(models.Model):
    sender = models.ForeignKey(MyUser, related_name='sent_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    thread = models.ForeignKey(Thread, related_name='included_messages')

    objects = MessageManager()

    def __unicode__(self):
        return u'%s' % self.content