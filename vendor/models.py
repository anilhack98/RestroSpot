from django.db import models
from django.utils.text import slugify  # To automatically generate URL-friendly slugs
from accounts.models import User, UserProfile  # Import custom User and UserProfile models
from datetime import time,date,datetime

# Vendor model: represents a vendor in the marketplace
class Vendor(models.Model):
    user = models.OneToOneField(User, related_name='user', on_delete=models.CASCADE)
    user_profile = models.OneToOneField(UserProfile, related_name='userprofile', on_delete=models.CASCADE)
    vendor_name = models.CharField(max_length=50)
    vendor_slug = models.SlugField(max_length=100, unique=True)
    vendor_license = models.ImageField(upload_to='vendor/license')
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    # Override save method to automatically create slug from vendor_name if not provided
    def save(self, *args, **kwargs):
        if not self.vendor_slug:
            self.vendor_slug = slugify(self.vendor_name)  # Converts name to URL-friendly slug
        super().save(*args, **kwargs)  # Call the original save method

    # String representation of the object
    def __str__(self):
        return self.vendor_name
    
    def is_open(self):
        # Check current day's opening Hour
        today_date = date.today()
        today = today_date.isoweekday()
        
        current_opening_hours = OpeningHour.objects.filter(vendor=self, day=today)
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")

        is_open = None
        for i in current_opening_hours:
            if not i.from_hour or not i.to_hour:
                continue

            try:
                start = str(datetime.strptime(i.from_hour, "%I:%M %p").time())
                end = str(datetime.strptime(i.to_hour, "%I:%M %p").time())
            except ValueError:
                continue
            
            if current_time > start and current_time < end:
                is_open = True
                break
            else:
                is_open = False
        return is_open
DAYS = [
    (1, ("Monday")),
    (2, ("Tuesday")),
    (3, ("Wednesday")),
    (4, ("Thursday")),
    (5, ("Friday")),
    (6, ("Saturday")),
    (7, ("Sunday")),
]

HOUR_OF_DAY_24 = [
    (time(h, m).strftime('%I:%M %p'), time(h, m).strftime('%I:%M %p'))
    for h in range(0, 24) for m in (0, 30)
]

class OpeningHour(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    day = models.IntegerField(choices=DAYS)
    from_hour = models.CharField(max_length=10, choices=HOUR_OF_DAY_24, blank=True)
    to_hour = models.CharField(max_length=10, choices=HOUR_OF_DAY_24, blank=True)
    is_closed = models.BooleanField(default=False)

    class Meta:
        ordering = ('day', '-from_hour')
        unique_together = ('vendor','day', 'from_hour', 'to_hour')

    def __str__(self):
        return self.get_day_display()