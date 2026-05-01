#!/usr/bin/env python3
"""
Generate high-converting, expert-level appointment reminder templates.
"""

import argparse
import os
import sys

# Force UTF-8 output on Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# ---------------------------------------------------------------------------
# Profile helpers
# ---------------------------------------------------------------------------
def pval(profile, key, default='[Not Set]'):
    return profile.get(key) or default

# ---------------------------------------------------------------------------
# Elite Templates
# ---------------------------------------------------------------------------

TEMPLATES = {
    "booking_confirmation": {
        "sms": (
            "Hi {{customer_name}}, you're all set! Your {{service_type}} at {shop_name} "
            "is confirmed for {{date}} at {{time}}. Need to adjust? Call {phone}. See you then!"
        ),
        "email": (
            "Subject: Your Appointment is Confirmed! We'll see you on {{date}}.\n\n"
            "Hi {{customer_name}},\n\n"
            "Thank you for choosing {shop_name}. You're officially on the schedule for your upcoming {{service_type}}, and we're looking forward to taking great care of your vehicle.\n\n"
            "Here are the details for your visit:\n"
            "• Service: {{service_type}}\n"
            "• Date: {{date}}\n"
            "• Time: {{time}}\n"
            "• Location: {address}\n\n"
            "To help us get you back on the road faster, please plan to arrive about 5 minutes early. If you've noticed any other issues lately—strange noises, new smells, or a warning light—just let our service advisor know when you drop off the keys. We'll be happy to take a look.\n\n"
            "If you need to reschedule, no problem at all. Just give us a call at {phone}.\n\n"
            "See you soon,\n\n"
            "{owner_name}\n"
            "{shop_name}\n"
            "{phone} | {website}"
        ),
        "phone_script": (
            "[GREET] Hi, may I speak with {{customer_name}}? ... Hi {{customer_name}}, this is {{agent_name}} calling from {shop_name}.\n\n"
            "[PURPOSE] I'm calling to quickly confirm your appointment for a {{service_type}} on {{date}} at {{time}}.\n\n"
            "[PAUSE] Does that time still work perfectly for you?\n\n"
            "[IF YES] Fantastic. We're at {address}. Please try to arrive just a few minutes early so we can get your paperwork started right away. If you think of anything else you'd like us to check while we have it in the bay, just let us know when you drop off the keys.\n\n"
            "[IF NO] Not a problem at all. Let me pull up the schedule... I have an opening on [Alternative Date/Time] or [Alternative Date/Time]. Do either of those work better for your schedule?\n\n"
            "[CLOSE] Great, we have you locked in. If anything comes up before then, feel free to call us directly at {phone}. Thanks, {{customer_name}}, we'll see you soon!"
        ),
    },

    "day_before_reminder": {
        "sms": (
            "Reminder: Your {{service_type}} at {shop_name} is TOMORROW at {{time}}. "
            "Questions? Reply or call {phone}. We look forward to seeing you!"
        ),
        "email": (
            "Subject: Reminder: We'll see you tomorrow at {{time}}!\n\n"
            "Hi {{customer_name}},\n\n"
            "Just a quick reminder that you are on our schedule tomorrow for your {{service_type}}. Our technicians are ready for you!\n\n"
            "Appointment Details:\n"
            "• Date: {{date}} (Tomorrow)\n"
            "• Time: {{time}}\n"
            "• Location: {address}\n\n"
            "When you arrive, just pull into the service drive and head to the front desk. If you need a ride home or to work while we service your vehicle, please let us know so we can accommodate you.\n\n"
            "Need to make a last-minute change? Give us a call directly at {phone}.\n\n"
            "Drive safely, and we'll see you tomorrow!\n\n"
            "The Team at {shop_name}\n"
            "{phone}"
        ),
        "phone_script": (
            "[GREET] Hi {{customer_name}}, this is {{agent_name}} from {shop_name}.\n\n"
            "[PURPOSE] I'm just calling with a quick, friendly reminder that your {{service_type}} is on our schedule for tomorrow at {{time}}.\n\n"
            "[PAUSE] Are we still good to go for tomorrow?\n\n"
            "[IF YES] Wonderful. Our address is {address}. Just a reminder to bring any spare keys if you have them, and let us know if there's absolutely anything else you'd like our techs to look at while we have the vehicle on the lift.\n\n"
            "[IF NO] No worries, life happens! Let's get you rescheduled right now so we don't lose your spot in line. How does next week look for you?\n\n"
            "[CLOSE] Perfect. We're looking forward to seeing you tomorrow at {{time}}. Have a great rest of your day, {{customer_name}}!"
        ),
    },

    "day_of_notification": {
        "sms": (
            "Good morning {{customer_name}}! Today's the day for your {{service_type}} at {shop_name}. "
            "See you at {{time}}! {address}"
        ),
        "email": (
            "Subject: See you today, {{customer_name}}!\n\n"
            "Good morning {{customer_name}},\n\n"
            "Today is the day! We are fully prepared and expecting you at {{time}} for your {{service_type}}.\n\n"
            "Location: {address}\n"
            "Questions? Call us at: {phone}\n\n"
            "A quick tip: Write down any dashboard warning lights, weird sounds, or performance issues you've noticed recently. The more details you give us, the faster and more accurately our technicians can diagnose and service your vehicle.\n\n"
            "We'll see you shortly!\n\n"
            "{shop_name}"
        ),
        "phone_script": (
            "[GREET] Good morning {{customer_name}}, this is {{agent_name}} calling from {shop_name}.\n\n"
            "[PURPOSE] I'm just giving you a quick call to let you know our service bay is ready and we're expecting you today at {{time}} for your {{service_type}}.\n\n"
            "[PAUSE] Did you have any last-minute questions before you head over?\n\n"
            "[IF NO] Excellent. We'll be ready for you at the front desk when you arrive. Drive safe!\n\n"
            "[IF YES] [Answer questions thoroughly and reassure the customer].\n\n"
            "[CLOSE] We'll see you at {{time}}, {{customer_name}}. Thanks for choosing {shop_name}!"
        ),
    },

    "post_service_thankyou": {
        "sms": (
            "Hi {{customer_name}}, thanks for trusting {shop_name} with your {{service_type}} today! "
            "If you loved our service, a quick review means the world: {review_link}"
        ),
        "email": (
            "Subject: Thank you for choosing {shop_name}, {{customer_name}}!\n\n"
            "Hi {{customer_name}},\n\n"
            "I want to personally thank you for bringing your vehicle to {shop_name} today for your {{service_type}}. We know you have choices when it comes to auto repair, and we are grateful you chose us.\n\n"
            "Our goal is always to provide transparent, high-quality service that keeps your vehicle safe and reliable. \n\n"
            "Two quick things:\n"
            "1. If you notice anything unusual over the next few days—don't hesitate to call us immediately at {phone}. We stand completely behind our work and want to make sure you are 100% satisfied.\n"
            "2. As a local business, we rely heavily on word-of-mouth. If you had a 5-star experience with our team today, it would mean the world to us if you took 30 seconds to leave a quick Google review:\n"
            "{review_link}\n\n"
            "Thank you again for your trust. Drive safely, and we'll see you next time!\n\n"
            "Best regards,\n\n"
            "{owner_name}\n"
            "{shop_name}\n"
            "{website}"
        ),
        "phone_script": (
            "[GREET] Hi {{customer_name}}, this is {{agent_name}} following up from {shop_name}.\n\n"
            "[PURPOSE] I'm just calling to make sure everything went perfectly with your {{service_type}} today and to thank you for your business.\n\n"
            "[PAUSE] How is the vehicle driving for you?\n\n"
            "[IF GOOD] That is exactly what we love to hear! We really appreciate you giving us the opportunity to earn your trust. By the way, if you have a spare minute, I'd love to text you a link to leave us a quick Google review. It helps our small business tremendously. Would that be okay?\n\n"
            "[IF ISSUE] I'm so sorry to hear you're experiencing that. That's not the standard we strive for. Can you describe exactly what it's doing? [Listen carefully, log notes]. I want to make this right immediately. Can you bring it back by tomorrow morning so our lead tech can inspect it at no charge?\n\n"
            "[CLOSE] Thank you again, {{customer_name}}. Don't hesitate to call us at {phone} if you ever need anything else. Have a wonderful day!"
        ),
    },

    "thirty_day_followup": {
        "sms": (
            "Hi {{customer_name}}, it's been a month since your {{service_type}} at {shop_name}. "
            "Is the vehicle driving perfectly? Need anything else? Just text or call {phone}."
        ),
        "email": (
            "Subject: Checking in: How is your vehicle running? | {shop_name}\n\n"
            "Hi {{customer_name}},\n\n"
            "It's been about 30 days since your last visit to {shop_name} for your {{service_type}}, and we just wanted to do a quick check-in.\n\n"
            "How is your vehicle performing? We strongly believe that preventative care is the secret to avoiding massive repair bills. If you've felt any new vibrations, heard any new squeaks, or noticed a drop in fuel economy, those are early warning signs. \n\n"
            "It's always cheaper to fix a small problem now than a major failure on the side of the highway later.\n\n"
            "If everything is running beautifully—great! If you have even the slightest concern, give us a call at {phone}. We're always happy to offer advice over the phone or schedule a quick diagnostic look.\n\n"
            "Stay safe out there,\n\n"
            "The Team at {shop_name}\n"
            "{phone}"
        ),
        "phone_script": (
            "[GREET] Hi {{customer_name}}, this is {{agent_name}} calling from {shop_name}.\n\n"
            "[PURPOSE] I'm just doing a quick courtesy follow-up. It's been about a month since we saw you for your {{service_type}}.\n\n"
            "[PAUSE] I wanted to make sure everything is still running smoothly. Any weird noises or concerns we should know about?\n\n"
            "[IF GOOD] That is great news. A well-maintained vehicle is a safe vehicle! Just a heads-up, we are currently running a special on [Insert Special/Seasonal Service]. Should I go ahead and pencil you in for a quick checkup while I have you on the phone?\n\n"
            "[IF ISSUE] I'm glad I called. That sounds like something we should definitely take a look at before it turns into a bigger headache for you. I have an opening tomorrow afternoon—want me to put you down so we can get it diagnosed?\n\n"
            "[CLOSE] Excellent. Thanks for your time, {{customer_name}}. Keep us in mind if you need anything at all. Our number is {phone}. Take care!"
        ),
    },

    "six_month_maintenance": {
        "sms": (
            "Hi {{customer_name}}, it's been 6 months since your {{service_type}} at {shop_name}. "
            "Stay ahead of costly repairs—call {phone} to book your routine check-up today."
        ),
        "email": (
            "Subject: It's time for your 6-month vehicle check-up! | {shop_name}\n\n"
            "Hi {{customer_name}},\n\n"
            "Can you believe it's been six months since your last visit to {shop_name} for your {{service_type}}?\n\n"
            "Based on your vehicle's factory maintenance schedule, you are likely due for a routine service. Staying strictly on top of routine maintenance (like oil changes, fluid flushes, and brake inspections) is the single most effective way to drastically extend the life of your vehicle and prevent multi-thousand-dollar emergency repairs.\n\n"
            "When you bring your vehicle in, we don't just do the bare minimum. We perform a comprehensive multi-point digital inspection to catch early signs of wear and tear before they become dangerous or expensive.\n\n"
            "Don't wait for a breakdown. Call us today at {phone} or reply to this email to get on the schedule at a time that is convenient for you.\n\n"
            "We look forward to seeing you!\n\n"
            "{shop_name}\n"
            "{phone} | {website}"
        ),
        "phone_script": (
            "[GREET] Hi {{customer_name}}, this is {{agent_name}} from {shop_name}.\n\n"
            "[PURPOSE] I'm calling because our records show it's been about six months since your {{service_type}}. Based on typical driving habits, you're right in the window where routine maintenance is due to keep your warranty valid and your engine healthy.\n\n"
            "[PAUSE] Have you had a chance to get your oil changed or your fluids checked recently?\n\n"
            "[IF NO] No problem, that's exactly why we reach out! Getting it done now prevents major engine wear later. I actually have an opening this Thursday or Friday. Which of those days works better for you to drop it off?\n\n"
            "[IF YES] Oh, excellent! We love to hear that you're staying on top of it. Did they happen to check your brake pads and alignment while it was in the shop?\n\n"
            "[CLOSE] Great, I'll update our records. Let us know when you're ready for your next service, {{customer_name}}. Call us anytime at {phone}. Have a great day!"
        ),
    },
}

TOUCHPOINT_ORDER = [
    "booking_confirmation",
    "day_before_reminder",
    "day_of_notification",
    "post_service_thankyou",
    "thirty_day_followup",
    "six_month_maintenance",
]

# ---------------------------------------------------------------------------
# Core generation
# ---------------------------------------------------------------------------

def apply_profile(content, profile, customer_name, service_type):
    """Replace {profile_var} tokens with real values from the shop profile."""
    shop_name   = pval(profile, 'shop_name',  'Your Auto Shop')
    phone       = pval(profile, 'phone',       '(555) 555-5555')
    address     = pval(profile, 'address') or pval(profile, 'location', '123 Main St')
    owner_name  = pval(profile, 'owner_name', 'The Owner')
    website     = pval(profile, 'website',    'yourshop.com')
    review_link = profile.get('review_links', {}).get('google', '') or 'https://g.page/r/[add-your-google-review-link]'
    
    c_name = customer_name.strip() if customer_name else "[Customer Name]"

    replacements = {
        '{shop_name}':   shop_name,
        '{phone}':       phone,
        '{address}':     address,
        '{owner_name}':  owner_name,
        '{website}':     website,
        '{review_link}': review_link,
        '{{customer_name}}': c_name,
        '{{service_type}}': service_type,
        '{{date}}': '[Date]',
        '{{time}}': '[Time]',
        '{{agent_name}}': '[Your Name]'
    }
    for token, value in replacements.items():
        content = content.replace(token, value)
    return content

def generate_touchpoint(touchpoint, customer_name, service_type, channels, profile, output_dir):
    """Generate all requested channels for one touchpoint into ONE combined file."""
    templates = TEMPLATES.get(touchpoint)
    if not templates:
        print(f"ERROR: Unknown touchpoint '{touchpoint}'", file=sys.stderr)
        return []

    combined_content = []

    if "sms" in channels or "all" in channels:
        if "sms" in templates:
            txt = apply_profile(templates["sms"], profile, customer_name, service_type)
            combined_content.append("--- SMS ---\n" + txt + "\n")

    if "email" in channels or "all" in channels:
        if "email" in templates:
            txt = apply_profile(templates["email"], profile, customer_name, service_type)
            combined_content.append("--- EMAIL ---\n" + txt + "\n")

    if "phone_script" in channels or "all" in channels:
        if "phone_script" in templates:
            txt = apply_profile(templates["phone_script"], profile, customer_name, service_type)
            combined_content.append("--- PHONE SCRIPT ---\n" + txt + "\n")

    if not combined_content:
        return []

    filename = f"{touchpoint}.txt"
    filepath = os.path.join(output_dir, filename)
    with open(filepath, 'w', encoding='utf-8') as fh:
        fh.write("\n".join(combined_content))

    print(f"  ✅ output/appointments/{filename}")
    return [filename]

# ---------------------------------------------------------------------------
# CLI (kept for compatibility, though mostly called via router)
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--touchpoint', required=True)
    parser.add_argument('--customer_name', default='')
    parser.add_argument('--service_type', required=True)
    parser.add_argument('--channels', default='sms,email,phone_script')
    args = parser.parse_args()
    
    print("CLI execution is deprecated. Please use the FastAPI router.")

if __name__ == '__main__':
    main()
 len(channels)} total templates")


if __name__ == '__main__':
    main()
