from django.utils.text import slugify

from random import choice
from string import ascii_lowercase, digits


def random_string_generator(size=10, chars=ascii_lowercase + digits):
    return ''.join(choice(chars) for _ in range(size))


# sluggified is the field to be turned into a slug
def unique_slugify(instance, new_slug, sluggified):
    if not new_slug:
        new_slug = slugify(sluggified)
        base_slug = new_slug
        while instance.objects.filter(slug=new_slug).exists():
            new_slug = base_slug + random_string_generator()

    return new_slug
