from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, UserProfile

@receiver(post_save, sender=User)
def create_profile_receiver(sender, instance, created, **kwargs):
    print(created)
    if created:
        # New user → create profile
        UserProfile.objects.create(user=instance)
    else:
        # For existing users → ensure profile exists
        profile, created_profile = UserProfile.objects.get_or_create(user=instance)
        if created_profile:
            print("Profile did not exist, created now")
        else:
            profile.save()
            print("User updated and profile saved")
