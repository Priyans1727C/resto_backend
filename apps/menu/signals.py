import os
from django.db.models.signals import pre_save, post_delete,post_save
from django.dispatch import receiver
from django.conf import settings
from .models import MenuItem
from django.core.cache import cache

@receiver(pre_save, sender=MenuItem)
def delete_old_image_on_update(sender,instance, **kwargs):
    if not instance.pk:
        return
    
    try:
        user = MenuItem.objects.get(pk =instance.pk)
    except MenuItem.DoesNotExist:
        return
    
    old_item_image = user.image
    new_item_image = instance.image
    
    if old_item_image and (not new_item_image or old_item_image!=new_item_image):
        if old_item_image.storage.exists(old_item_image.name):
            old_item_image.delete(old_item_image.name)
            
@receiver(post_delete, sender=MenuItem)
def delete_image_on_menu_delete(sender,instance,**kwargs):
    if instance.image:
        try:
            if instance.image.store.exist(instance.image.name):
                instance.image.store.delete(instance.image.name)
        except Exception:
            pass
        
@receiver([post_save,post_delete], sender = MenuItem)
def invalidate_caching(sender,instance,**kwargs):
    print("cleaing the menuitem cach")
    cache.delete_pattern("*menu_items*")
    cache.delete_pattern("*resto_details*")