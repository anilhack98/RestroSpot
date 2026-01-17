
import os
import sys
import django
from datetime import datetime, date

# Setup Django environment
sys.path.append('d:\\PROJ\\RestroSpot_check')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'khanaspot.settings')
django.setup()

from vendor.models import Vendor, OpeningHour

def debug_vendor_hours():
    with open('debug_output.txt', 'w') as f:
        today_date = date.today()
        today = today_date.isoweekday()
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")

        f.write(f"DEBUG: Current Date: {today_date}\n")
        f.write(f"DEBUG: Current Day (Weekday): {today}\n")
        f.write(f"DEBUG: Current Time: {current_time}\n")

        vendors = Vendor.objects.all()
        for vendor in vendors:
            f.write(f"\nChecking Vendor: {vendor.vendor_name}\n")
            opening_hours = OpeningHour.objects.filter(vendor=vendor, day=today)
            f.write(f"Found {opening_hours.count()} opening hours for today.\n")
            
            is_open = None
            for i in opening_hours:
                f.write(f"  - Slot: {i.from_hour} to {i.to_hour} (Closed: {i.is_closed})\n")
                
                if not i.from_hour or not i.to_hour:
                    f.write("    -> Skipping empty hours\n")
                    continue

                try:
                    start = str(datetime.strptime(i.from_hour, "%I:%M %p").time())
                    end = str(datetime.strptime(i.to_hour, "%I:%M %p").time())
                    f.write(f"    -> Parsed Start: {start}, End: {end}\n")
                except ValueError as e:
                    f.write(f"    -> ValueError parsing time: {e}\n")
                    continue
                
                if current_time > start and current_time < end:
                    f.write("    -> MATCH! Vendor is OPEN.\n")
                    is_open = True
                    break
                else:
                    f.write("    -> No match for this slot.\n")
                    is_open = False
            
            f.write(f"Final is_open Status: {is_open}\n")

if __name__ == '__main__':
    debug_vendor_hours()
