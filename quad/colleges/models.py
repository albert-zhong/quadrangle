from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from mptt.models import MPTTModel, TreeForeignKey

from .utils import unique_slugify


class College(models.Model):
    full_name = models.CharField(max_length=70, unique=True)
    short_name = models.CharField(max_length=20, unique=True)
    logo = models.ImageField(null=True, blank=True)
    banner = models.ImageField(null=True, blank=True)
    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.short_name)
        super(College, self).save(*args, **kwargs)

    def __str__(self):
        return self.short_name

    def get_absolute_url(self):
        return reverse('forum', kwargs={'college_slug': self.slug})


class CollegeEmail(models.Model):
    domain = models.URLField(max_length=31)
    college = models.ForeignKey(
        College,
        on_delete=models.CASCADE,
        related_name='emails'
    )


class Thread(models.Model):
    author = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        related_name='created_threads',
        null=True,
    )
    college = models.ForeignKey(
        College,
        on_delete=models.CASCADE,
        related_name='threads',
    )

    title = models.CharField(max_length=127)
    body = models.CharField(max_length=2047)
    score = models.IntegerField(default=0)
    timestamp = models.DateTimeField(default=now, editable=False)
    edited_timestamp = models.DateTimeField(null=True)
    is_anonymous = models.BooleanField(default=False)

    hits = models.IntegerField(default=0)
    comments_count = models.IntegerField(default=0)
    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        self.slug = unique_slugify(Thread, self.slug, self.title)
        super(Thread, self).save(*args, **kwargs)

    def __str__(self):
        return self.slug

    def get_absolute_url(self):
        return reverse('thread', kwargs={'thread_slug': self.slug})


class Comment(MPTTModel):
    author = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        related_name='created_comments',
        null=True,
    )
    thread = models.ForeignKey(
        Thread,
        on_delete=models.CASCADE,
        related_name='comments',
        null=True, # eventually make this false
    )

    body = models.CharField(max_length=511)
    score = models.IntegerField(default=0)
    timestamp = models.DateTimeField(default=now, editable=False)
    edited_timestamp = models.DateTimeField(null=True)
    is_anonymous = models.BooleanField(default=False)

    # mptt-django fields
    parent = TreeForeignKey(
        'self',
        on_delete=models.CASCADE,
        related_name='children',
        null=True,
        db_index=True,
    )

    class MPTTMeta:
        order_insertion_by = ['-score']


class Vote(models.Model):
    voter = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='%(class)s_votes',
    )
    is_like = models.BooleanField()

    class Meta:
        abstract = True


class ThreadVote(Vote):
    thread = models.ForeignKey(
        Thread,
        on_delete=models.CASCADE,
        related_name='thread_votes'
    )


class CommentVote(Vote):
    comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        related_name='comment_votes'
    )
