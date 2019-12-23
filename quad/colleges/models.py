from django.contrib.auth import get_user_model
from django.db import models
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from mptt.models import MPTTModel, TreeForeignKey


class College(models.Model):

    class CountryOfCollege(models.TextChoices):
        UNITED_STATES = 'USA', _('United States')
        UNITED_KINGDOM = 'GBR', _('United Kingdom')
        CANADA = 'CAN', _('Canada')
        AUSTRALIA = 'AUS', _('Australia')

    country = models.CharField(
        max_length=3,
        choices=CountryOfCollege.choices
    )
    state = models.CharField(max_length=20)

    full_name = models.CharField(max_length=70)
    short_name = models.CharField(max_length=20)
    parent_school = models.ForeignKey(
        'self',  # use 'self' instead of College
        blank=True,
        null=True,
        default=None,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.short_name


class Thread(models.Model):
    author = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        related_name='created_posts',
        null=True,
    )
    title = models.CharField(max_length=127)
    body = models.CharField(max_length=2047)
    slug = models.SlugField()
    timestamp = models.DateTimeField(default=now, editable=False)
    edited_timestamp = models.DateTimeField(null=True)
    score = models.IntegerField(default=0)

    college = models.ForeignKey(
        College,
        on_delete=models.CASCADE,
        related_name='threads',
        null=True,
    )


class Comment(MPTTModel):
    author = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        related_name='created_comments',
        null=True,
    )
    body = models.CharField(max_length=511)
    timestamp = models.DateTimeField(default=now, editable=False)
    edited_timestamp = models.DateTimeField(null=True)
    score = models.IntegerField(default=0)

    parent_thread = models.ForeignKey(
        Thread,
        on_delete=models.CASCADE,
        related_name='comments',
    )

    # mptt-django fields
    parent = TreeForeignKey(
        'self',
        on_delete=models.CASCADE,
        related_name='children',
    )

    class MPTTMeta:
        order_insertion_by = ['-score']
