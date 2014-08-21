from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.contrib.auth import get_user_model


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
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_superuser


class MessageManager(models.Manager):

    def save(self, sender, content, receiver_list):
        message = self.model(sender=sender, content=content)
        # message.receiver = receiver
        message.save(using = self._db)
        model=get_user_model()
        for receiver in receiver_list:
            user=model.objects.get(email=receiver)
            message.receiver.add(user)
        return message


mgr=MessageManager()
mgr.use_for_related_fields = True


class Message(models.Model):
    sender = models.ForeignKey(MyUser, related_name='sent_messages')
    content = models.TextField()
    receiver = models.ManyToManyField(MyUser, related_name='received_messages')
    timestamp = models.DateTimeField(auto_now_add=True)

    objects = MessageManager()

    def __unicode__(self):
        return u'%s' % self.content

