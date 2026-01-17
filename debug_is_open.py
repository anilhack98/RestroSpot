# Import required Python modules
import os
import sys
import django
from datetime import datetime, date

# ---------------------------------------------------
# STEP 1: Setup Django Environment
# ---------------------------------------------------

# Add your Django project path so Python can find it
sys.path.append('d:\\PROJ\\RestroSpot_check')

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'khanaspot.settings')

# Initialize Django
django.setup()

# ---------------------------------------------------
# STEP 2: Import Django Models
# ---------------------------------------------------

from vendor.models import Vendor, OpeningHour

# ---------------------------------------------------
# STEP 3: Debug Function to Check Vendor Open Hours
# ---------------------------------------------------

def debug_vendor_hours():

    # Open a text file to store debug output
    with open('debug_output.txt', 'w') as f:

        # Get today's date
        today_date = date.today()

        # Get ISO weekday number (Monday=1, Sunday=7)
        today = today_date.isoweekday()

        # Get current date and time
        now = datetime.now()

        # Convert current time to string format (HH:MM:SS)
        current_time = now.strftime("%H:%M:%S")

        # Write basic system information
        f.write(f"DEBUG: Current Date: {today_date}\n")
        f.write(f"DEBUG: Current Day (Weekday): {today}\n")
        f.write(f"DEBUG: Current Time: {current_time}\n")

        # Fetch all vendors from database
        vendors = Vendor.objects.all()

        # Loop through each vendor
        for vendor in vendors:
            f.write(f"\nChecking Vendor: {vendor.vendor_name}\n")

            # Get today's opening hours for this vendor
            opening_hours = OpeningHour.objects.filter(
                vendor=vendor,
                day=today
            )

            # Write number of time slots found
            f.write(f"Found {opening_hours.count()} opening hours for today.\n")

            # Variable to track open/close status
            is_open = None

            # Loop through each opening hour slot
            for i in opening_hours:
                f.write(
                    f"  - Slot: {i.from_hour} to {i.to_hour} "
                    f"(Closed: {i.is_closed})\n"
                )

                # Skip if start or end time is missing
                if not i.from_hour or not i.to_hour:
                    f.write("    -> Skipping empty hours\n")
                    continue

                try:
                    # Convert 12-hour time (e.g. 10:00 AM) to 24-hour time
                    start = str(datetime.strptime(i.from_hour, "%I:%M %p").time())
                    end = str(datetime.strptime(i.to_hour, "%I:%M %p").time())

                    f.write(
                        f"    -> Parsed Start: {start}, "
                        f"End: {end}\n"
                    )

                # Handle invalid time format errors
                except ValueError as e:
                    f.write(f"    -> ValueError parsing time: {e}\n")
                    continue

                # Check if current time falls within opening time range
                if current_time > start and current_time < end:
                    f.write("    -> MATCH! Vendor is OPEN.\n")
                    is_open = True
                    break
                else:
                    f.write("    -> No match for this slot.\n")
                    is_open = False

            # Final open/close status for vendor
            f.write(f"Final is_open Status: {is_open}\n")

# ---------------------------------------------------
# STEP 4: Run Function Directly
# ---------------------------------------------------

if __name__ == '__main__':
    debug_vendor_hours()
