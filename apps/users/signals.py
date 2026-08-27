from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import F
from apps.posts.models import Post

@receiver(post_save, sender=Post)
def increment_post_count(sender, instance, created, **kwargs):
    if created:
        instance.user.__class__.objects.filter(pk=instance.user.pk).update(post_count=F('post_count') + 1)

@receiver(post_delete, sender=Post)
def decrement_post_count(sender, instance, **kwargs):
    instance.user.__class__.objects.filter(pk=instance.user.pk).update(post_count=F('post_count') - 1)
