#!/usr/bin/env python3
"""
SOP Library Generator — Module 10: SOP Library
Shop Command Center

Generate complete, print-ready Standard Operating Procedures for every major
auto repair shop process. Each SOP includes: Purpose, Scope, Responsibilities,
Materials/Tools, Step-by-Step Procedure (with Why notes), Quality Checks,
and Notes/Exceptions.

Usage:
  # Generate a specific SOP
  python tools/sop/generate_sop.py --procedure vehicle_intake

  # With shop-specific custom rules
  python tools/sop/generate_sop.py --procedure vehicle_intake \\
      --custom_rules "Always photograph all four corners at check-in."

  # Free-form custom SOP
  python tools/sop/generate_sop.py \\
      --custom "How to handle after-hours key drop-off for early morning pickups" \\
      --title "After-Hours Key Drop Procedure"

  # List all available procedures
  python tools/sop/generate_sop.py --list

  # Generate ALL SOPs at once
  python tools/sop/generate_sop.py --all
"""

import argparse
import json
import os
import sys

# Force UTF-8 output on Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
from datetime import datetime

PROFILE_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'shop_profile.json')
OUTPUT_DIR   = os.path.join(os.path.dirname(__file__), '..', '..', 'output', 'sop')


def load_profile():
    path = os.path.abspath(PROFILE_PATH)
    if not os.path.exists(path):
        return {}
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


# ─────────────────────────────────────────────────────────────────────────────
# SOP Definitions
# Each entry: title, purpose, scope, responsible, materials, steps, quality_checks, notes
# steps: list of (step_text, why_note) tuples
# ─────────────────────────────────────────────────────────────────────────────

PROCEDURES = {

    # ── VEHICLE OPERATIONS ────────────────────────────────────────────────────

    "vehicle_intake": {
        "title":       "Vehicle Intake & Check-In Procedure",
        "category":    "Vehicle Operations",
        "purpose":     "Ensure every vehicle entering the shop is properly documented, every customer concern is captured accurately, and expectations are set before work begins.",
        "scope":       "All service advisors and front desk staff. Applies to every vehicle check-in, including same-day walk-ins and scheduled appointments.",
        "responsible": "Service Advisor (primary). Shop Manager (oversight).",
        "materials":   ["Work order form or shop management software", "Camera or smartphone for photos", "Mileage log", "Pen or tablet for documentation"],
        "steps": [
            ("Greet the customer within 30 seconds of their arrival. Use their name if they're a returning customer.",
             "First impressions set the tone for the entire visit. A fast, personal greeting signals professionalism."),
            ("Ask for the keys and confirm the customer's contact information: name, phone number, and email.",
             "Accurate contact info is needed for status updates and follow-up. Outdated info causes missed calls and frustrated customers."),
            ("Walk around the vehicle WITH the customer before they leave. Note any pre-existing scratches, dents, or damage on the work order.",
             "This protects both the customer and the shop. Existing damage documented before work begins cannot be blamed on the shop."),
            ("Photograph all four sides of the vehicle and the odometer reading. Attach photos to the digital work order.",
             "[CUSTOMIZE] Some shops also photograph the interior. Photos are objective evidence — far more reliable than written notes alone."),
            ("Ask: 'What brings you in today?' — then listen completely before responding. Do not interrupt.",
             "Let the customer describe the problem in their own words. Their description often contains clues that a leading question would suppress."),
            ("Ask: 'Is there anything else you've noticed?' to probe for additional concerns.",
             "Customers often forget secondary issues. This single question frequently surfaces additional revenue-generating work."),
            ("Document all concerns on the work order using the customer's own words — not a paraphrase.",
             "Using their language prevents miscommunication. 'It makes a clunking noise on left turns' is more actionable than 'noise.'"),
            ("Record the mileage from the odometer. Confirm the VIN if not already in the system.",
             "Mileage is required for maintenance history accuracy and some warranty validations."),
            ("Provide an estimated completion time. If you cannot give an exact time, give a range and your best estimate.",
             "Customers plan their day around your estimate. Never promise a time you cannot deliver."),
            ("Explain the communication process: 'We'll text you when we've had a chance to look at it, and call before doing any work beyond what's approved.'",
             "Sets expectations for proactive communication. Surprises erode trust."),
            ("Ask: 'Would you like to wait, get a ride, or have us call when it's ready?'",
             "Giving options puts the customer in control. Know their preference before they walk out the door."),
            ("Enter all information into the shop management system immediately — never rely on memory.",
             "Delays between intake and data entry cause transcription errors. Log it now."),
        ],
        "quality_checks": [
            "All pre-existing damage is documented and photographed before customer leaves.",
            "Work order reflects customer's own words, not advisor's interpretation.",
            "Estimated completion time and update method have been communicated and confirmed.",
            "Contact information is current and verified.",
        ],
        "notes": "If the vehicle has a known recall open (see Module 8), note it on the work order at check-in. For vehicles with high mileage or obvious deferred maintenance, set the expectation early that the inspection may reveal additional items.",
    },

    "oil_change": {
        "title":       "Oil & Filter Change Procedure",
        "category":    "Vehicle Operations",
        "purpose":     "Perform a complete, safe, and consistent oil and filter service that meets the manufacturer's specifications for the vehicle.",
        "scope":       "All technicians performing oil changes. Applies to conventional, synthetic-blend, and full-synthetic oil services.",
        "responsible": "Assigned Technician. Service Advisor (customer communication and upsell).",
        "materials":   ["Correct oil type and viscosity (check OEM spec)", "New oil filter (OEM or quality aftermarket)", "Drain plug washer (if applicable)", "Oil drain pan", "Filter wrench", "Torque wrench", "Funnel", "Oil-absorbent pads or mats", "Multi-point inspection form"],
        "steps": [
            ("Pull the vehicle work order. Confirm the correct oil type, viscosity, and quantity. Look up the OEM specification — do not assume.",
             "Using the wrong viscosity or oil type can cause premature engine wear. Always verify for the specific year/make/model/engine."),
            ("Warm the engine for 2–3 minutes if the vehicle just arrived cold. Do NOT service a fully hot engine.",
             "Warm oil drains more completely. A hot engine risks burns. 2–3 minutes is the safe middle ground."),
            ("Position the vehicle on the lift or oil change pit. Raise to working height. Confirm vehicle is stable before going underneath.",
             "A vehicle falling off a lift is a life-safety incident. Stability check is non-negotiable."),
            ("Place drain pan under the drain plug. Remove the drain plug using the correct socket. Allow oil to drain fully — minimum 3 minutes.",
             "Rushing the drain leaves old, dirty oil behind. 3 minutes is the minimum; longer is better on high-mileage engines."),
            ("Remove the old oil filter. Position drain pan under the filter — filters hold oil and will spill.",
             "A filter emptied on the floor is wasted time, wasted oil, and a slip hazard."),
            ("Inspect the drain plug threads and the sealing surface for damage. Install a new crush washer if required by the vehicle.",
             "A stripped drain plug or damaged washer causes oil leaks. Catching it now costs nothing. A callback costs time and trust."),
            ("Hand-thread the drain plug in first, then torque to spec. Do not overtighten — that strips threads.",
             "Overtorquing is the #1 cause of stripped drain plug threads. Use a torque wrench. Know the spec."),
            ("Lightly lubricate the new filter gasket with fresh oil. Thread the filter on by hand until the gasket contacts the housing, then tighten 3/4 turn more.",
             "Dry gaskets can stick and tear, causing leaks. 3/4 turn past contact is the standard — avoid using a filter wrench to tighten."),
            ("Lower the vehicle. Add the correct amount and type of oil through the fill cap. Do not overfill.",
             "Overfilling causes oil foaming, pressure buildup, and seal damage. Fill to the middle of the dipstick range if uncertain."),
            ("Start the engine. Watch the oil pressure light — it should go off within 5 seconds. Check immediately for leaks at the drain plug and filter.",
             "Most post-oil-change leaks happen in the first minute of running. Check now, not when the customer calls."),
            ("Shut off the engine. Wait 2 minutes. Check oil level on the dipstick. Adjust if needed.",
             "Hot oil in the pan gives an inaccurate reading. Two minutes lets it settle for a true measurement."),
            ("Perform or record the multi-point inspection while the vehicle is accessible.",
             "The vehicle is already on the lift. A quick inspection takes 5 minutes and frequently surfaces additional services."),
            ("Reset the oil life monitor per the vehicle's procedure. Affix an oil change reminder sticker in the upper-left corner of the windshield.",
             "[CUSTOMIZE] sticker placement may vary. An unreset oil light is an easy customer complaint and easy to avoid."),
            ("Record oil type, viscosity, quantity used, filter part number, and mileage on the work order.",
             "Complete records protect the shop in warranty or complaint situations."),
        ],
        "quality_checks": [
            "Oil type and viscosity match OEM specification for this vehicle.",
            "Drain plug is torqued to spec with a fresh washer if required.",
            "No leaks present after engine run.",
            "Oil level on dipstick is in the correct range.",
            "Oil life monitor reset.",
            "Reminder sticker applied.",
            "Work order updated with oil specs, filter P/N, and mileage.",
        ],
        "notes": "If the drain plug shows significant thread damage, stop and inform the service advisor before proceeding. A HeliCoil or thread repair may be required. Never use thread-locking compound as a workaround on a drain plug.",
    },

    "tire_rotation": {
        "title":       "Tire Rotation Procedure",
        "category":    "Vehicle Operations",
        "purpose":     "Extend tire life by rotating tires in the correct pattern for the vehicle, document findings, and advise the customer of any tire-related concerns.",
        "scope":       "All technicians performing tire rotations.",
        "responsible": "Assigned Technician.",
        "materials":   ["Impact wrench or breaker bar", "Torque wrench", "Tire tread depth gauge", "Tire pressure gauge", "Air compressor and inflation chuck", "Work order / inspection form", "Jack stands (if applicable)"],
        "steps": [
            ("Pull the work order and confirm the vehicle year/make/model. Look up the correct rotation pattern for this vehicle.",
             "Rotation patterns differ: front-to-back, X-pattern, directional tires (front-to-back same side only), full-size spare inclusion. Using the wrong pattern defeats the purpose."),
            ("Before lifting the vehicle, loosen all lug nuts 1/4 turn while the tires are still on the ground.",
             "Loosening on the ground prevents the wheel from spinning and is faster and safer than fighting a spinning wheel on the lift."),
            ("Raise the vehicle on the lift. Confirm all four lift pads are on frame or pinch-weld locations per the vehicle spec.",
             "Incorrect lift placement can damage the vehicle structure and create a drop hazard."),
            ("Remove all four tires. Inspect each tire for: tread depth (measure with gauge in multiple grooves), sidewall cracks or bulges, embedded objects, and uneven wear patterns.",
             "Uneven wear is diagnostic — it tells you about alignment or inflation problems. Document what you see, not just the numbers."),
            ("Measure and record tread depth on all four tires (front-left, front-right, rear-left, rear-right). Use 32nds of an inch.",
             "Tread depth data gives the customer objective information and protects the shop if a tire fails after the service."),
            ("Move tires to their new positions per the correct rotation pattern for this vehicle.",
             "If unsure of the pattern, look it up. Wrong pattern = customer's tires wear unevenly, and they will know."),
            ("Inspect lug nut condition. Replace any that are rounded, cracked, or corroded.",
             "Damaged lug nuts are a safety hazard and can cause the customer to be unable to change a flat on the road."),
            ("Hand-thread all lug nuts first. Then use the impact wrench to snug — do not final-torque with the impact.",
             "Final torquing with an impact wrench overtorques and can crack rotors or strip studs."),
            ("Lower the vehicle with all four tires on the ground. Torque all lug nuts to the vehicle-specific spec using a torque wrench in a star pattern.",
             "Star pattern ensures the wheel seats evenly on the hub. Torque spec is on the work order or in AllData/Mitchell."),
            ("Check and adjust tire pressure on all four tires to the vehicle's door placard spec (not the max on the tire sidewall).",
             "The door placard is the manufacturer's spec. Sidewall numbers are the tire's maximum — not the correct inflation pressure."),
            ("Record tread depths, tire pressure (before and after), and any concerns on the work order.",
             "This data creates a service history and gives the service advisor material to discuss with the customer."),
            ("If any tire is at or below 4/32\", flag it as a customer advisory. Below 2/32\" is a safety replacement recommendation.",
             "4/32\" is the threshold where wet-weather performance degrades significantly. 2/32\" is the legal minimum in most states."),
        ],
        "quality_checks": [
            "Tires rotated in correct pattern for this vehicle.",
            "Lug nuts torqued to spec with torque wrench after lowering.",
            "Tire pressures set to door placard spec on all four tires.",
            "Tread depths measured and recorded.",
            "Any worn, damaged, or uneven-wear tires documented and communicated to service advisor.",
        ],
        "notes": "Staggered fitments (different front/rear widths) and directional tires cannot be crossed to the opposite side. Verify before rotating. If the vehicle has a full-size matching spare and the customer requests a 5-tire rotation, follow the manufacturer's recommended 5-tire pattern.",
    },

    "vehicle_inspection": {
        "title":       "Multi-Point Vehicle Inspection Procedure",
        "category":    "Vehicle Operations",
        "purpose":     "Perform a thorough, consistent inspection on every vehicle, document findings with objective measurements, and communicate results clearly to the service advisor.",
        "scope":       "All technicians performing inspections.",
        "responsible": "Assigned Technician. Service Advisor (customer communication).",
        "materials":   ["Multi-point inspection form (digital or paper)", "Flashlight", "Brake pad thickness gauge", "Tire tread depth gauge", "Battery tester", "Camera or smartphone", "Fluid test strips (coolant, brake fluid)", "Inspection mirror"],
        "steps": [
            ("Pull up the digital inspection form for the vehicle type. Confirm year/make/model is correct.",
             "Starting with the correct form prevents missing vehicle-specific items."),
            ("Begin with a visual exterior walk-around: tires, lights, glass, body, visible leaks underneath.",
             "Quick visual items first — some findings (flat tire, broken light) are noted before the vehicle goes on the lift."),
            ("Open the hood. Check all fluid levels: engine oil, coolant, brake fluid, power steering, transmission fluid, windshield washer fluid.",
             "Follow a consistent top-to-bottom, left-to-right pattern. Consistency prevents missing items on every vehicle."),
            ("Inspect belt condition: look for cracks, fraying, glazing. Inspect hose condition: look for swelling, cracks, soft spots.",
             "Belts and hoses that look 'okay' can fail without warning. Note age and mileage as context."),
            ("Test the battery: voltage and load test if the battery is more than 3 years old. Record voltage on the form.",
             "A battery that passes a voltage test can still fail a load test. Both tests together are meaningful."),
            ("Raise the vehicle on the lift. Visually inspect: brake pads and rotors, calipers, brake lines and hoses.",
             "Use a proper brake pad thickness gauge — do not estimate. 'Looks fine' is not a measurement."),
            ("Measure brake pad thickness in millimeters on all four corners. Record front and rear.",
             "Exact numbers, not ranges. Customers trust data. 'You have 4mm on your rear brakes' is more convincing than 'they're getting low.'"),
            ("Inspect front and rear suspension: control arms, ball joints, tie rod ends, sway bar links, struts/shocks for leaks.",
             "Grab each wheel at 3 and 9 o'clock and rock it to check for looseness. Then at 12 and 6 o'clock."),
            ("Inspect the exhaust system from catalytic converter to tailpipe: hangers, leaks, corrosion.",
             "An exhaust leak is a safety concern (CO exposure). It also fails emissions in states with testing."),
            ("Check for any fluid leaks: look for wet spots on the frame, engine block, transmission, differential, steering rack.",
             "Identify the fluid type: oil is brown/black, coolant is often orange or green, transmission fluid is red, brake fluid is clear/light yellow."),
            ("Rate each inspection item: Green (OK), Yellow (monitor / recommend at next service), Red (needs attention now / safety concern).",
             "Be honest. Do not rate items green just to avoid a conversation. Do not rate yellow items red to generate work."),
            ("Photograph any Red or Yellow items. Attach photos to the digital inspection form.",
             "Photos remove 'I don't believe you' objections. A photo of worn brake pads is more persuasive than any description."),
            ("Complete the form and submit to the service advisor with specific recommended actions for each flagged item.",
             "Technicians observe and recommend. Service advisors present to the customer. Keep these roles clear."),
        ],
        "quality_checks": [
            "All inspection items rated — no blanks left.",
            "Brake pad thickness recorded in mm on all four corners.",
            "Battery voltage documented.",
            "Red and Yellow items have photos attached.",
            "Form submitted to service advisor with recommended actions.",
        ],
        "notes": "Never present inspection results directly to the customer without the service advisor. A technician presenting findings without context can create confusion or mistrust. Communicate findings to the advisor, who translates them for the customer.",
    },

    "test_drive": {
        "title":       "Test Drive Procedure",
        "category":    "Vehicle Operations",
        "purpose":     "Verify repair quality and vehicle safety through a structured, consistent road test after applicable service.",
        "scope":       "Technicians performing post-repair test drives. Required after: brake work, suspension/steering work, drivability complaints, transmission service, alignment.",
        "responsible": "Assigned Technician or Shop Foreman.",
        "materials":   ["Valid driver's license (technician's)", "Work order", "Phone/voice recorder for notes during drive"],
        "steps": [
            ("Verify: your driver's license is current and you are authorized by the shop's insurance to drive customer vehicles.",
             "Liability requirement. An unlicensed or uninsured driver in a customer's vehicle is a significant legal exposure."),
            ("Review the work order before the drive. Know what was repaired and what complaint you're verifying.",
             "A test drive without a target is inefficient. Know what you're listening and feeling for."),
            ("Adjust mirrors and seat. Do not move personal items in the vehicle.",
             "Adjust for safety, but treat the customer's property with respect."),
            ("Use the shop's standard test drive route when possible — a mix of city and highway, including a stop-and-go segment.",
             "[CUSTOMIZE] Establish your standard route. Consistency means you know what 'normal' feels like on that route."),
            ("During the drive, test the specific systems that were serviced. For brakes: test stopping at various speeds. For steering: test at low speed and highway speed. For noise: drive the route that reproduces the complaint.",
             "Test what you fixed. A technician who doesn't verify their work is guessing, not confirming."),
            ("Drive with the radio off and window open in key moments. Listen for noises.",
             "You cannot hear a suspension clunk with the radio at volume 30. Window down amplifies road noise."),
            ("Verify all warning lights remain off during the drive.",
             "A warning light that appears during the test drive was caused by the service or existed before and was missed. Either way, address it now."),
            ("Return to the shop. Park in the designated ready area, not in a bay.",
             "A vehicle in a ready space signals it's complete. A vehicle in a bay signals it's in progress."),
            ("Record the test drive outcome on the work order: 'Test drive performed — no issues found' OR a description of any remaining concern.",
             "Documentation closes the loop. 'Test drive performed' on the work order is protection if a customer claims an issue was not addressed."),
        ],
        "quality_checks": [
            "All systems serviced were specifically tested during the drive.",
            "No warning lights present at the end of the drive.",
            "Outcome documented on the work order.",
            "Vehicle parked in designated ready area.",
        ],
        "notes": "If the original complaint is not resolved during the test drive, the vehicle is NOT ready. Return it to the technician — do not deliver an unresolved repair to the customer. Communicate the updated status to the service advisor immediately.",
    },

    "quality_control": {
        "title":       "Quality Control Pre-Delivery Procedure",
        "category":    "Vehicle Operations",
        "purpose":     "Verify all approved work is completed correctly and safely before the vehicle is returned to the customer.",
        "scope":       "Lead Technician or Shop Foreman. Every vehicle must pass QC before delivery.",
        "responsible": "Shop Foreman or Lead Technician.",
        "materials":   ["Work order (marked complete)", "Torque wrench", "Flashlight", "Fluid test strips"],
        "steps": [
            ("Review the completed work order. Confirm every approved line item is checked off as done.",
             "Nothing gets skipped. If a line item isn't checked, the work is not complete."),
            ("Physical check: verify torque specs on any fasteners that were disturbed during the repair.",
             "Safety-critical fasteners — wheels, brake caliper bolts, suspension bolts — must be verified, not assumed."),
            ("Check for fluid leaks: run the engine for 2 minutes, then inspect underneath for drips or wet spots.",
             "Most post-repair leaks appear in the first two minutes of operation. Catch them here, not in the customer's driveway."),
            ("Verify all fluids that were topped off or changed are at the correct level.",
             "A fluid level check takes 60 seconds. An underfilled brake master cylinder is a safety incident."),
            ("Reset any maintenance reminders or warning lights applicable to the service performed.",
             "A customer who sees a warning light for work that was just done will call immediately and lose confidence in the shop."),
            ("Perform a test drive if the service involved brakes, steering, drivability, suspension, or any noise complaint. Follow the Test Drive SOP.",
             "If it's safety-related, it gets a test drive. No exceptions."),
            ("Final visual: confirm there are no tools left in the engine bay, no grease on the steering wheel or seats, no floor mats out of place.",
             "Presentation is part of the product. A greasy steering wheel tells the customer their car was not cared for."),
            ("Sign off on the work order. QC technician initials = accountability.",
             "Sign-off means you personally verified this vehicle is safe and ready. Take it seriously."),
            ("Notify the service advisor the vehicle is ready for delivery.",
             "Trigger the customer notification through the shop's communication system."),
        ],
        "quality_checks": [
            "All work order items checked as complete.",
            "Safety-critical fasteners torque-verified.",
            "No fluid leaks after engine run.",
            "Vehicle interior clean — no grease, no tools, mats in place.",
            "Work order signed off by QC technician.",
        ],
        "notes": "QC is not just about the repair — it's about the customer's perception of the shop. A vehicle returned with a clean interior, all warning lights off, and a technician who stands behind their work is how you build a returning customer.",
    },

    "vehicle_delivery": {
        "title":       "Vehicle Delivery Procedure",
        "category":    "Vehicle Operations",
        "purpose":     "Ensure a professional, thorough handoff that reinforces trust, explains the work clearly, and sets up the customer's next visit.",
        "scope":       "Service Advisors. Applies to every vehicle returned to a customer.",
        "responsible": "Service Advisor.",
        "materials":   ["Completed work order", "Customer invoice", "Payment processing system", "Declined service follow-up notes"],
        "steps": [
            ("Review the completed work order before the customer arrives. Know what was done, what was declined, and what was recommended.",
             "You are the customer's advocate. If you don't know the details, you cannot answer questions confidently."),
            ("Contact the customer to let them know the vehicle is ready. Give them an estimated pickup time or confirm they are on their way.",
             "Never make the customer walk in wondering if their car is done. A heads-up phone call or text sets a positive final impression."),
            ("Walk the customer to their vehicle — do not hand keys across the counter.",
             "Walking to the vehicle creates a moment for conversation, shows respect, and gives you a natural opportunity to point out their car and any observations."),
            ("Explain the work completed in plain language — not technical jargon.",
             "Use the Estimate Narrator output if available. A customer who understands what was done trusts the bill."),
            ("If replaced parts were set aside at the customer's request, present them now.",
             "Some customers want to see old parts. If they asked, deliver. If they didn't ask, you don't need to offer, but don't dispose of parts until the customer has left."),
            ("Briefly mention any declined services — no pressure, no lecture. Just: 'We noted the [item] for next time. We'll remind you at your next visit.'",
             "This keeps future revenue opportunities visible without damaging the current relationship. Feed into the Declined Services module."),
            ("Provide the next recommended service and approximate timing: 'Your next oil change is around [date or mileage].'",
             "Setting the next appointment or expectation before they leave is the highest-leverage moment for retention."),
            ("Process payment. Thank the customer regardless of the total.",
             "A $50 oil change customer can become a $5,000 engine replacement customer in 18 months. Treat every ticket as a relationship investment."),
            ("Ask: 'Is there anything else I can help you with?'",
             "An open-ended closing question occasionally catches an issue or a question the customer had but didn't ask."),
            ("Mention the review link, once, naturally: 'If everything went well today, a Google review helps our small shop a lot — here's the link.'",
             "[CUSTOMIZE] Share your Google review link. Don't beg or script it as a demand. A genuine one-sentence ask works."),
            ("Trigger the post-visit thank-you message within 2 hours. Use the Appointment Reminders module.",
             "A same-day thank-you message is one of the highest-return customer experience actions the shop can take."),
        ],
        "quality_checks": [
            "Service advisor reviewed completed work order before customer arrival.",
            "All work explained in plain language.",
            "Declined services noted without pressure.",
            "Next service timing or date provided.",
            "Payment processed and receipt provided.",
            "Post-visit thank-you triggered.",
        ],
        "notes": "If the customer has a complaint or concern at delivery, do not become defensive. Acknowledge immediately and follow the Customer Complaint SOP. A delivery that turns into a smooth complaint resolution is often more loyalty-building than a perfect service.",
    },

    # ── CUSTOMER SERVICE ──────────────────────────────────────────────────────

    "phone_greeting": {
        "title":       "Phone Greeting & Call Handling Procedure",
        "category":    "Customer Service",
        "purpose":     "Answer every call professionally, route it correctly, and leave the caller with a positive impression of the shop — whether they book an appointment or not.",
        "scope":       "All staff who answer the shop phone.",
        "responsible": "Service Advisor (primary). Any available staff (if advisor is busy).",
        "materials":   ["Appointment scheduling system", "Pen and notepad (backup)"],
        "steps": [
            ("Answer the phone within 3 rings.",
             "After 4 rings, most callers assume no one is available. A missed call is often a missed customer."),
            ("Use the standard greeting: '[Shop Name], this is [Your Name], how can I help you today?'",
             "Your name creates a personal connection. 'How can I help you' is open-ended — it invites the caller to lead."),
            ("If you need to place the caller on hold, ask permission first: 'May I put you on a brief hold? I'll be right back with you.'",
             "Putting someone on hold without asking feels dismissive. Asking shows respect for their time."),
            ("Return to a hold caller within 90 seconds. If you need more time, check back: 'Thank you for holding. I need just one more moment — is that okay?'",
             "Callers left on hold longer than 90 seconds without an update will hang up."),
            ("Listen to the caller's concern fully before offering solutions or scheduling.",
             "Interrupting a caller to schedule before they've finished describing the issue often leads to booking the wrong service."),
            ("For appointment requests: confirm the service needed, ask for year/make/model, and offer two or three available time slots.",
             "Offering specific options — 'I have Tuesday at 10am or Thursday at 2pm' — is faster and more decisive than 'when works for you?'"),
            ("Collect and confirm: customer name, phone number, vehicle year/make/model, and service needed.",
             "Repeat it back to the customer to confirm: 'I have you down for [name], [vehicle], [service], [date/time]. Does that look right?'"),
            ("For callers asking about price only: give a range, explain that exact quotes require seeing the vehicle, and offer to schedule a free inspection.",
             "A quoted price over the phone without seeing the vehicle can undercut or overbid. A range is honest; a free inspection converts the caller."),
            ("For urgent calls (breakdown, safety concern): take the issue seriously, offer the earliest available appointment, and if needed, provide the nearest towing resource.",
             "A customer calling in distress needs to feel heard and helped immediately. This is one of the highest-opportunity calls the shop receives."),
            ("End every call: '[Customer name], thanks for calling [Shop Name]. We'll see you [date/time].' Or: 'We look forward to helping you.'",
             "A consistent warm close reinforces the shop's brand and leaves a positive final impression."),
        ],
        "quality_checks": [
            "Phone answered within 3 rings.",
            "Standard greeting used.",
            "Customer name, phone, vehicle, and service confirmed before ending the call.",
            "Appointment time read back to customer to confirm.",
            "No caller left on hold more than 90 seconds without a check-in.",
        ],
        "notes": "[CUSTOMIZE] If the shop uses a phone system with hold music or recorded greetings, this SOP governs the live-answer portion only. If the shop uses text-to-schedule, ensure the phone SOP directs callers to that option when appropriate.",
    },

    "customer_checkin": {
        "title":       "Customer Check-In Procedure",
        "category":    "Customer Service",
        "purpose":     "Ensure every customer is greeted professionally, their concerns are documented accurately, and expectations are set clearly from the first moment.",
        "scope":       "All service advisors and front desk staff.",
        "responsible": "Service Advisor.",
        "materials":   ["Shop management system / work order form", "Camera or smartphone"],
        "steps": [
            ("Greet the customer by name if returning; introduce yourself if new.",
             "First impressions set the tone for the entire visit."),
            ("Ask for keys and confirm contact information: phone and email.",
             "Accurate contact info is needed for status updates. Outdated info causes missed calls."),
            ("Walk around the vehicle WITH the customer. Note any existing damage on the work order.",
             "Protects the shop from damage claims. Document with photos whenever possible."),
            ("Ask: 'What brought you in today?' — listen fully before responding.",
             "Let the customer describe the problem in their own words."),
            ("Ask: 'Is there anything else you've noticed?' to uncover additional concerns.",
             "Customers often forget to mention secondary issues. This question frequently surfaces additional work."),
            ("Document all concerns on the work order in the customer's own words.",
             "Using their language prevents miscommunication."),
            ("Provide estimated completion time and cost range.",
             "Never promise exact times or prices at check-in unless you are certain."),
            ("Explain the update process: 'We'll text you with progress and call before doing any additional work.'",
             "Sets expectations for proactive communication. Surprises erode trust."),
            ("Confirm preferred contact method and authorization level: proceed on approved items, or call first on everything.",
             "Some customers want to approve every decision. Others trust you to proceed. Know which type before they leave."),
            ("Enter the work order into the system immediately.",
             "Delays between intake and data entry cause lost information."),
        ],
        "quality_checks": [
            "Pre-existing damage documented before customer leaves.",
            "Work order reflects customer's own words.",
            "Completion time and communication method confirmed.",
        ],
        "notes": "For returning customers, briefly review their service history before they arrive. Acknowledging their history ('I see you were in for brakes last spring') builds loyalty.",
    },

    "estimate_approval": {
        "title":       "Estimate Presentation & Approval Procedure",
        "category":    "Customer Service",
        "purpose":     "Present repair estimates clearly and transparently, obtain explicit approval on each item, and handle objections professionally — resulting in a signed work authorization the customer understands and trusts.",
        "scope":       "Service Advisors. Applies to all estimates presented to customers.",
        "responsible": "Service Advisor.",
        "materials":   ["Printed or digital estimate", "Inspection photos", "Estimate Narrator output (if available)", "Work authorization form"],
        "steps": [
            ("Review all technician findings and notes before calling the customer. Understand the work fully before presenting it.",
             "You cannot answer questions about work you haven't reviewed. Know the estimate before the customer does."),
            ("Lead with safety-critical items first. Then preventive maintenance. Then convenience items.",
             "Prioritizing by urgency helps the customer make informed decisions. If they can only do some of it, they'll do the most important items first."),
            ("Use plain language for every line item. Use the Estimate Narrator tool for complex repairs.",
             "A customer who understands the work trusts the price. 'Your control arm bushing is worn' means nothing. 'The rubber mount that cushions your suspension is cracked, causing the clunk' means something."),
            ("Present the estimate by phone or in person — never just email a number without explanation.",
             "An unexplained estimate invites the customer to shop around. A explained estimate builds trust and converts."),
            ("For each line item, say: 'This is what we found, here's why it matters, here's what we recommend.' Then pause. Let them respond.",
             "Don't steamroll. Silence after a recommendation gives the customer space to ask questions or say yes."),
            ("Share inspection photos for any flagged items. 'Here's a photo of the brake pad — you can see it's down to about 2mm of material left.'",
             "Photos are more persuasive than any description. Use them for every significant recommendation."),
            ("Ask for approval on each item individually: 'Do you want to go ahead with the brake pads?' — then move to the next.",
             "Never assume blanket approval. Explicit approval on each item protects the shop legally and the customer financially."),
            ("Document approved vs. declined on the work order. Get a signature or verbal confirmation (if phone, note 'verbal approval [date/time]').",
             "Approval documentation is the shop's protection against 'I didn't approve that' disputes."),
            ("For declined services, briefly note the risk without pressure: 'We'll keep it on your file for next time. It's something to watch.'",
             "A declined service is a future opportunity. Feed it into the Declined Services Follow-Up module."),
            ("Confirm the revised total and completion time with the customer before closing the call or conversation.",
             "No surprises at pickup. The total and time they confirm now is the total and time they expect at delivery."),
        ],
        "quality_checks": [
            "Every approved and declined item documented on the work order.",
            "Customer signature or verbal approval obtained and noted.",
            "Revised total and completion time confirmed before hanging up.",
            "Declined items logged for follow-up.",
        ],
        "notes": "If a customer asks you to 'just do what it needs,' document this as blanket approval with a stated maximum. 'Customer authorized all recommended work up to $[X]' is a reasonable approach with a defined limit.",
    },

    "customer_complaints": {
        "title":       "Customer Complaint Handling Procedure",
        "category":    "Customer Service",
        "purpose":     "Resolve customer complaints quickly, fairly, and in a way that retains the relationship and prevents repeat occurrences.",
        "scope":       "All staff, with escalation to Shop Manager.",
        "responsible": "Service Advisor (intake). Shop Manager (resolution authority).",
        "materials":   ["Complaint log form or shop management note", "Original work order"],
        "steps": [
            ("Listen fully without interrupting — let them finish speaking before you say anything.",
             "Interrupting escalates. Listening de-escalates. A customer who feels heard is easier to resolve than one who feels dismissed."),
            ("Acknowledge their frustration: 'I understand why that's frustrating. Thank you for letting us know.'",
             "Validation is not admission of fault. It's proof you're listening. Skip this step and the customer stays in escalation mode."),
            ("Ask clarifying questions to get specific: what happened, when, what did they expect, what did they experience?",
             "Vague complaints produce vague resolutions. Specific complaints can be solved. Get the details."),
            ("Pull the work order and review what was done before responding with a solution.",
             "Never offer a resolution before you know the facts. 'I'll take care of it' without knowing what 'it' is can cost more than necessary."),
            ("Document the complaint immediately: customer name, date, description, what they want.",
             "Written documentation protects the shop and creates data for identifying patterns."),
            ("Offer a resolution within your authority. If it's beyond your authority, say: 'Let me bring in [manager] to make sure we handle this correctly.'",
             "Don't offer what you can't deliver. Don't delay a decision you have the authority to make."),
            ("If re-work is needed, prioritize it — bring the vehicle in immediately, not at the next available appointment.",
             "Making a customer wait for a comeback sends the message that their problem is not your priority. It isn't true — demonstrate it."),
            ("Follow up within 24 hours to confirm the customer is satisfied.",
             "The follow-up is what turns a complaint into loyalty. Customers who have complaints resolved well are often more loyal than customers who never had a problem."),
            ("Log the complaint type and resolution in the shop management system.",
             "Repeated complaints about the same technician, part, or service are a systemic signal. Monthly review of complaint logs is a management practice."),
        ],
        "quality_checks": [
            "Complaint documented with date, customer name, and description.",
            "Resolution offered within 24 hours.",
            "Follow-up call made to confirm satisfaction.",
            "Complaint logged for pattern review.",
        ],
        "notes": "Never argue about who is right. Even if the shop is not at fault, the customer's experience is their reality. A gracious resolution to an incorrect complaint is almost always worth the cost. A customer who is proven wrong and treated well often becomes a loyal advocate.",
    },

    # ── OPERATIONS ────────────────────────────────────────────────────────────

    "parts_ordering": {
        "title":       "Parts Ordering Procedure",
        "category":    "Operations",
        "purpose":     "Ensure the correct parts are ordered, received, and matched to the right job efficiently and with full traceability.",
        "scope":       "Parts Manager, Service Advisors, Technicians who initiate part requests.",
        "responsible": "Parts Manager or designated Service Advisor.",
        "materials":   ["Shop management system (PO module)", "Vendor accounts and pricing catalogs", "Parts Inventory module (Module 11)"],
        "steps": [
            ("Verify the exact part needed: year, make, model, engine size, trim level, and any applicable sub-codes.",
             "Wrong part = wasted time, return freight, and a customer waiting longer than expected."),
            ("Check in-stock inventory first using the Parts Inventory module.",
             "Don't order what you already have. Unnecessary ordering ties up cash and creates overstock."),
            ("Check preferred vendor availability, pricing, and delivery time.",
             "[CUSTOMIZE] List your vendor priority order here. Example: Primary — local WD, Secondary — AutoZone Commercial, Tertiary — OEM dealer."),
            ("Place the order. Generate a PO number and link it to the customer's work order.",
             "Every order must be traceable from PO to work order. If a part is returned or disputed, this link is essential."),
            ("Confirm delivery ETA. If it will affect the customer's completion time, notify them immediately.",
             "Proactive communication about delays is far less damaging than an unexplained delay the customer discovers at pickup."),
            ("When the part arrives, verify: part number, quantity, and condition against the PO and work order.",
             "Receiving is not just signing the delivery slip. Verify before signing. Returns are harder after the driver leaves."),
            ("Stage the received part at the correct bay or technician's workbench before they begin the job.",
             "A technician searching for parts they're supposed to have is time the customer is paying for."),
            ("If the wrong part is received: document, initiate the return immediately, and reorder the correct part in the same call.",
             "Don't let a wrong part sit. A wrong part sitting in the bay is a car that doesn't get repaired today."),
            ("Update the work order with the actual parts cost. If it differs from the estimate, notify the service advisor before proceeding.",
             "Price changes require customer notification. The service advisor manages that conversation — give them the information before the work is done."),
        ],
        "quality_checks": [
            "Part number, quantity, and condition verified on receipt.",
            "PO number linked to work order.",
            "Customer notified if delivery affects their completion time.",
            "Wrong parts documented and returned same day.",
        ],
        "notes": "Core charge tracking: If a part requires a core return, set a reminder to return the core within the vendor's timeframe. Unclaimed core credits cost the shop money. [CUSTOMIZE] Add your core return process here.",
    },

    "end_of_day": {
        "title":       "End-of-Day Closing Procedure",
        "category":    "Operations",
        "purpose":     "Ensure the shop is securely closed, all vehicles and equipment are accounted for, the register is reconciled, and the facility is ready to open the next morning.",
        "scope":       "All closing staff. Applies every business day. Last person out is responsible for completing this checklist.",
        "responsible": "Shop Manager or designated Lead (closing).",
        "materials":   ["End-of-day checklist (this SOP)", "Key box", "Register/POS system", "Alarm system"],
        "steps": [
            ("Walk all service bays. Confirm every vehicle is accounted for: in the bay, in the lot, or picked up by customer. No vehicles left unaccounted.",
             "A vehicle left unlocked overnight is a liability. A vehicle unaccounted for is a much larger problem."),
            ("Secure all customer vehicles that will remain overnight: windows up, doors locked. Note keys in the key box.",
             "Every overnight vehicle must be locked and its keys must be in the secured key box — not on a workbench."),
            ("Lower all lift arms to the ground or resting position.",
             "Lifts left raised overnight are a safety hazard and a liability."),
            ("Clean all service bays: sweep floors, clear workbenches, dispose of waste oil in approved containers.",
             "A clean bay at closing is a safe and efficient bay at opening. Technicians lose time at the start of the day if they have to clean up someone else's close."),
            ("Verify all hazardous materials are stored correctly: used oil in sealed containers, chemicals secured, nothing left on the floor.",
             "Regulatory requirement and fire safety requirement. See the Hazmat Disposal SOP."),
            ("Shut off all air compressors. Bleed the pressure from the tank lines.",
             "[CUSTOMIZE] Some shops leave compressors pressurized. Confirm your compressor manufacturer's recommendation."),
            ("Check all shop equipment is off: lifts, tire machines, battery chargers, fluid equipment.",
             "A battery charger left connected overnight to a fully charged battery can cause a fire."),
            ("Turn off all lights except any security lighting that should remain on.",
             "[CUSTOMIZE] Note which lights stay on."),
            ("Reconcile the register: count cash, run the day's report, note any discrepancies. Follow the Cash Handling SOP.",
             "Discrepancies discovered the next morning are harder to trace than discrepancies discovered tonight."),
            ("Lock all external doors and gates. Confirm the overhead bay doors are fully closed and locked.",
             "Walk each door and physically pull on it. Don't assume it's locked because you pressed the button."),
            ("Activate the alarm system. Confirm arming status before leaving.",
             "If the alarm doesn't confirm, call the monitoring company before leaving the building."),
            ("Complete and sign the closing checklist. File it or enter the close time in the shop management system.",
             "A signed checklist creates accountability and is the record if anything is discovered wrong the next morning."),
        ],
        "quality_checks": [
            "All vehicles accounted for and locked. Keys in key box.",
            "All bays clean and lift arms lowered.",
            "Register reconciled and any discrepancies noted.",
            "All doors locked and alarm activated.",
            "Closing checklist signed.",
        ],
        "notes": "[CUSTOMIZE] If your shop has a night drop box, confirm the slot is accessible, the lockbox is locked, and there are envelopes stocked. Add instructions for handling overnight drop keys to this SOP.",
    },

    "warranty_claims": {
        "title":       "Warranty Claims Procedure",
        "category":    "Operations",
        "purpose":     "Identify, document, and efficiently recover warranty credits on failed parts to protect shop revenue.",
        "scope":       "Parts Manager, Service Advisors.",
        "responsible": "Parts Manager (primary). Service Advisor (customer communication).",
        "materials":   ["Original purchase receipt or PO", "Warranty claim form (vendor-specific)", "Warranty Tracker module (Module 12)", "Camera for failure photos"],
        "steps": [
            ("Identify warranty-eligible failure: check the purchase date and the vendor's warranty terms.",
             "Most quality parts carry 12–24 month warranties. Some offer lifetime. Know your vendors' terms."),
            ("Pull the original purchase receipt or PO. A claim without documentation is a claim that will be denied.",
             "No receipt = no claim. This is not negotiable with any vendor."),
            ("Document the failure: date, vehicle mileage, symptoms, photos of the failed part.",
             "Photos are required by most vendors. Detailed documentation speeds approval and reduces disputes."),
            ("Contact the vendor to initiate the claim. Log the claim in the Warranty Tracker (Module 12).",
             "Same-day initiation. Aged claims are harder to win and some vendors have time limits."),
            ("Ship or return the defective part per the vendor's specific instructions. Keep the tracking number.",
             "Some vendors want the part back. Some want only photos. Know the difference before you ship anything."),
            ("Follow up on the claim at 7 days, 14 days, and 30 days if not resolved.",
             "Vendors process hundreds of claims. Unchecked claims get pushed back. Your follow-up is what moves it forward."),
            ("When the credit is received, reconcile it against the original claim amount.",
             "Partial credits happen. If the credit doesn't match, call the vendor the same day."),
            ("Update the Warranty Tracker with the resolution: credit amount, date received, and any variance.",
             "Monthly warranty reports show the shop's recovery rate — a number worth tracking."),
        ],
        "quality_checks": [
            "Original receipt or PO found before initiating any claim.",
            "Failure documented with date, mileage, and photos.",
            "Claim logged in Warranty Tracker on day of initiation.",
            "Follow-up scheduled at 7/14/30 days.",
            "Resolution amount reconciled against claim.",
        ],
        "notes": "Never throw away a failed part until the warranty claim is resolved. Many vendors require the part for inspection. Disposing of the part before the claim is settled forfeits the credit.",
    },

    "cash_handling": {
        "title":       "Cash Handling Procedure",
        "category":    "Operations",
        "purpose":     "Maintain accurate cash management, prevent loss, and ensure full accountability for every cash transaction.",
        "scope":       "Front desk staff, Service Advisors, Shop Manager.",
        "responsible": "Service Advisor (transactions). Shop Manager (reconciliation and deposit).",
        "materials":   ["Cash register / POS system", "Deposit bag", "Deposit slip", "Two-person verification log"],
        "steps": [
            ("Opening: count starting cash. Two people count. Both sign the log.",
             "Two-person opening count creates a documented baseline. If there's a discrepancy at close, you know when it started."),
            ("Every cash transaction receives a receipt — no exceptions.",
             "A receipt is both a record and a customer's proof of payment."),
            ("For cash payments over $500: count the bills in front of the customer, state the amount aloud, then confirm: 'I'm counting $520. Does that match what you're handing me?'",
             "Prevents disputes about the amount tendered. Both parties confirm before money changes hands."),
            ("If the cash drawer exceeds $500 during the day: perform a mid-day drop into the safe. Log the drop amount.",
             "Reducing cash-in-drawer reduces theft exposure and simplifies end-of-day reconciliation."),
            ("Closing: count cash in the drawer. Compare against the POS daily report. Note any variance.",
             "A variance over $5 is reported to the manager immediately. Do not send any discrepancy home overnight without logging it."),
            ("Prepare the deposit: count with two people, prepare the deposit slip, seal the bag.",
             "Sealed, two-person-verified deposits are standard banking practice and internal fraud prevention."),
            ("Deposit within 24 hours. Do not leave cash in the drawer overnight beyond the starting amount.",
             "Overnight cash above the float is a loss exposure. It also makes the opening count inaccurate."),
            ("Any discrepancy over $5: report to the shop manager immediately, same day.",
             "Small discrepancies compound. A $5 daily loss is $1,800/year."),
        ],
        "quality_checks": [
            "Opening count signed by two people.",
            "Every cash transaction has a receipt.",
            "End-of-day count reconciled against POS report.",
            "Deposit sealed and two-person verified.",
            "Any discrepancy over $5 reported same day.",
        ],
        "notes": "[CUSTOMIZE] If the shop uses a cashless system, adapt this SOP to cover credit/debit reconciliation, chargebacks, and end-of-day POS report review.",
    },

    "hazmat_disposal": {
        "title":       "Hazardous Material Disposal Procedure",
        "category":    "Operations",
        "purpose":     "Ensure all hazardous waste generated by shop operations is handled, stored, and disposed of in compliance with local, state, and federal regulations.",
        "scope":       "All technicians. Shop Manager is responsible for compliance oversight.",
        "responsible": "Shop Manager (compliance). All Technicians (daily compliance).",
        "materials":   ["Approved waste containers (oil, coolant, etc.)", "Labels", "Hazmat disposal log", "Contact info for licensed waste hauler"],
        "steps": [
            ("Know what hazmat the shop generates: used motor oil, coolant, brake fluid, transmission fluid, batteries, tires, oil filters, AC refrigerant, solvents, parts cleaner.",
             "You cannot comply with what you haven't identified. This list should match your actual operations."),
            ("Store each waste type in labeled, approved containers in the designated hazmat area. Never mix waste types.",
             "Mixed waste is more expensive to dispose of and may violate regulations. Keep them separate."),
            ("Used oil: drain into the shop's used oil tank. Never dump used oil anywhere — into drains, onto the ground, into trash.",
             "Used oil contamination of groundwater is a federal violation with significant fines. Licensed recyclers will pick up used oil — often for free."),
            ("Oil filters: drain over the oil tank for a minimum of 12 hours before disposal. Crushed drained filters may go to recycling.",
             "A drained filter is significantly less hazardous than an undrained one. Many states require draining before disposal."),
            ("Batteries: store upright on an acid-resistant surface. Tape terminals. Return to vendor for core credit or take to a certified battery recycler.",
             "Lead-acid batteries are recyclable and have core return value. Never put them in regular trash."),
            ("Tires: store in the designated tire area (stacked upright if possible). Schedule pickup with a licensed tire recycler.",
             "[CUSTOMIZE] State tire disposal fees vary. Track tire disposal costs and ensure customer fees cover them."),
            ("Coolant: drain into a dedicated coolant container — never into the used oil tank. Coolant contains ethylene glycol, which is toxic.",
             "Coolant-contaminated oil cannot be recycled as oil. Separation is required for both regulatory and cost reasons."),
            ("AC refrigerant: recover using EPA-certified equipment only. Log recovery amounts. Never vent refrigerant to the atmosphere.",
             "Venting refrigerant is an EPA violation. Recovery equipment certification and logging are federal requirements."),
            ("Maintain the hazmat disposal log: waste type, quantity, date, hauler company, and manifest number.",
             "Minimum 3-year retention in most states. Inspectors can and do ask for these records."),
            ("Schedule regular pickups with your licensed waste hauler before containers reach capacity.",
             "[CUSTOMIZE] Frequency depends on your shop's volume. Establish a regular schedule — quarterly at minimum for most shops."),
            ("Annual review: verify compliance with current local and state regulations. Regulations change.",
             "Check with your waste hauler or state environmental agency annually. New requirements can appear without broad notice."),
        ],
        "quality_checks": [
            "All waste containers labeled with waste type.",
            "No mixed waste in any container.",
            "Disposal log current and up to date.",
            "All pickups documented with manifest numbers.",
            "Annual compliance review completed and dated.",
        ],
        "notes": "[CUSTOMIZE] Your state and municipality may have requirements beyond federal minimums. Contact your state environmental agency or waste management company for the current requirements in your area. Keep their contact information posted in the hazmat storage area.",
    },

}

# Map old --process names to new --procedure names for backward compatibility
PROCESS_ALIASES = {
    "customer_checkin":    "customer_checkin",
    "vehicle_inspection":  "vehicle_inspection",
    "estimate_creation":   "estimate_approval",
    "parts_ordering":      "parts_ordering",
    "quality_control":     "quality_control",
    "test_drive":          "test_drive",
    "vehicle_delivery":    "vehicle_delivery",
    "warranty_claims":     "warranty_claims",
    "customer_complaints": "customer_complaints",
    "cash_handling":       "cash_handling",
    "hazmat_disposal":     "hazmat_disposal",
}


# ─────────────────────────────────────────────────────────────────────────────
# SOP rendering
# ─────────────────────────────────────────────────────────────────────────────

def render_sop(key, proc, shop_name, custom_rules=''):
    today = datetime.now().strftime('%B %d, %Y')

    lines = []
    lines.append("=" * 72)
    lines.append(f"  STANDARD OPERATING PROCEDURE")
    lines.append(f"  {proc['title'].upper()}")
    lines.append(f"  {shop_name}")
    lines.append("=" * 72)
    lines.append(f"\n  Category    : {proc.get('category', 'General')}")
    lines.append(f"  Effective   : {today}")
    lines.append(f"  Revision    : 1.0")
    lines.append(f"  Approved by : {'_' * 28}  Date: {'_' * 10}")

    lines.append("\n" + "─" * 72)
    lines.append("  PURPOSE")
    lines.append("─" * 72)
    lines.append(f"  {proc['purpose']}")

    lines.append("\n" + "─" * 72)
    lines.append("  SCOPE")
    lines.append("─" * 72)
    lines.append(f"  {proc['scope']}")

    lines.append("\n" + "─" * 72)
    lines.append("  WHO IS RESPONSIBLE")
    lines.append("─" * 72)
    lines.append(f"  {proc['responsible']}")

    if proc.get('materials'):
        lines.append("\n" + "─" * 72)
        lines.append("  MATERIALS / TOOLS NEEDED")
        lines.append("─" * 72)
        for m in proc['materials']:
            lines.append(f"    • {m}")

    lines.append("\n" + "─" * 72)
    lines.append("  STEP-BY-STEP PROCEDURE")
    lines.append("─" * 72)

    for i, (step, why) in enumerate(proc['steps'], 1):
        lines.append(f"\n  Step {i:02d}. {step}")
        if why:
            lines.append(f"          ↳ WHY: {why}")

    if proc.get('quality_checks'):
        lines.append("\n" + "─" * 72)
        lines.append("  QUALITY CHECKS")
        lines.append("─" * 72)
        for qc in proc['quality_checks']:
            lines.append(f"    ☐ {qc}")

    if proc.get('notes'):
        lines.append("\n" + "─" * 72)
        lines.append("  NOTES / EXCEPTIONS")
        lines.append("─" * 72)
        lines.append(f"  {proc['notes']}")

    if custom_rules:
        lines.append("\n" + "─" * 72)
        lines.append(f"  SHOP-SPECIFIC RULES — {shop_name}")
        lines.append("─" * 72)
        for rule in custom_rules.split('. '):
            rule = rule.strip().rstrip('.')
            if rule:
                lines.append(f"    ★ {rule}.")

    lines.append("\n" + "─" * 72)
    lines.append("  DOCUMENTATION REQUIREMENTS")
    lines.append("─" * 72)
    lines.append("  All deviations from this procedure must be documented and reported")
    lines.append("  to the Shop Manager. Employee signature on this SOP indicates they")
    lines.append("  have read, understood, and agree to follow this procedure.")
    lines.append(f"\n  Employee: {'_' * 30}  Date: {'_' * 10}")
    lines.append(f"  Employee: {'_' * 30}  Date: {'_' * 10}")
    lines.append(f"  Employee: {'_' * 30}  Date: {'_' * 10}")

    lines.append("\n" + "=" * 72)
    lines.append(f"  {shop_name} | {proc['title']}")
    lines.append(f"  Generated: {today} | SOP ID: {key.upper()}-1.0")
    lines.append("=" * 72)

    return "\n".join(lines)


def render_custom_sop(description, title, shop_name, custom_rules=''):
    """Generate a structured SOP from a free-form description."""
    today = datetime.now().strftime('%B %d, %Y')
    safe_title = title or "Custom Procedure"

    lines = []
    lines.append("=" * 72)
    lines.append(f"  STANDARD OPERATING PROCEDURE")
    lines.append(f"  {safe_title.upper()}")
    lines.append(f"  {shop_name}")
    lines.append("=" * 72)
    lines.append(f"\n  Category    : Custom")
    lines.append(f"  Effective   : {today}")
    lines.append(f"  Revision    : 1.0")
    lines.append(f"  Approved by : {'_' * 28}  Date: {'_' * 10}")

    lines.append("\n" + "─" * 72)
    lines.append("  PURPOSE")
    lines.append("─" * 72)
    lines.append(f"  This SOP covers: {description}")

    lines.append("\n" + "─" * 72)
    lines.append("  SCOPE")
    lines.append("─" * 72)
    lines.append("  [CUSTOMIZE] Specify which staff roles this procedure applies to.")

    lines.append("\n" + "─" * 72)
    lines.append("  WHO IS RESPONSIBLE")
    lines.append("─" * 72)
    lines.append("  [CUSTOMIZE] Name the role responsible for executing and overseeing this procedure.")

    lines.append("\n" + "─" * 72)
    lines.append("  MATERIALS / TOOLS NEEDED")
    lines.append("─" * 72)
    lines.append("  [CUSTOMIZE] List all equipment, forms, software, or supplies required.")

    lines.append("\n" + "─" * 72)
    lines.append("  STEP-BY-STEP PROCEDURE")
    lines.append("─" * 72)
    lines.append(f"""
  This is a custom SOP template for: {description}

  Fill in each step below. For each step, include:
    - What to do (specific action)
    - Why it matters (the reason behind the step)

  Step 01. [First action]
           ↳ WHY: [Reason]

  Step 02. [Second action]
           ↳ WHY: [Reason]

  Step 03. [Third action]
           ↳ WHY: [Reason]

  [Continue adding steps as needed]
""")

    lines.append("─" * 72)
    lines.append("  QUALITY CHECKS")
    lines.append("─" * 72)
    lines.append("  ☐ [CUSTOMIZE] What should be verified before this procedure is considered complete?")
    lines.append("  ☐ [CUSTOMIZE] Add additional quality checkpoints.")

    lines.append("\n" + "─" * 72)
    lines.append("  NOTES / EXCEPTIONS")
    lines.append("─" * 72)
    lines.append("  [CUSTOMIZE] Note any exceptions, edge cases, or conditions where this procedure")
    lines.append("  does not apply or requires modification.")

    if custom_rules:
        lines.append("\n" + "─" * 72)
        lines.append(f"  SHOP-SPECIFIC RULES — {shop_name}")
        lines.append("─" * 72)
        for rule in custom_rules.split('. '):
            rule = rule.strip().rstrip('.')
            if rule:
                lines.append(f"    ★ {rule}.")

    lines.append("\n" + "─" * 72)
    lines.append("  DOCUMENTATION REQUIREMENTS")
    lines.append("─" * 72)
    lines.append("  All deviations from this procedure must be documented and reported")
    lines.append("  to the Shop Manager.")
    lines.append(f"\n  Employee: {'_' * 30}  Date: {'_' * 10}")
    lines.append(f"  Employee: {'_' * 30}  Date: {'_' * 10}")

    lines.append("\n" + "=" * 72)
    lines.append(f"  {shop_name} | {safe_title}")
    lines.append(f"  Generated: {today} | Custom SOP")
    lines.append("=" * 72)

    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="SOP Library Generator — Module 10"
    )
    parser.add_argument('--procedure', default='',
                        choices=list(PROCEDURES.keys()) + list(PROCESS_ALIASES.keys()) + [''],
                        help="Built-in procedure to generate")
    parser.add_argument('--process',   default='',
                        help="Alias for --procedure (backward compatibility)")
    parser.add_argument('--custom',    default='',
                        help="Free-form description for a custom SOP (bypasses built-in list)")
    parser.add_argument('--title',     default='',
                        help="Title for a custom SOP")
    parser.add_argument('--custom_rules', default='',
                        help="Shop-specific additions appended to any SOP")
    parser.add_argument('--list',      action='store_true',
                        help="List all available procedures and exit")
    parser.add_argument('--all',       action='store_true',
                        help="Generate all built-in SOPs at once")

    args = parser.parse_args()

    profile   = load_profile()
    shop_name = profile.get('shop_name', 'Your Shop') or 'Your Shop'

    os.makedirs(os.path.abspath(OUTPUT_DIR), exist_ok=True)

    # ── List mode ──
    if args.list:
        print("\nAvailable SOP procedures:")
        current_cat = None
        for key, proc in PROCEDURES.items():
            cat = proc.get('category', 'General')
            if cat != current_cat:
                print(f"\n  {cat.upper()}")
                current_cat = cat
            print(f"    {key:<25}  {proc['title']}")
        print("\nUsage: python tools/sop/generate_sop.py --procedure <name>")
        print("       python tools/sop/generate_sop.py --all")
        return

    # ── Generate all ──
    if args.all:
        saved = []
        for key, proc in PROCEDURES.items():
            content  = render_sop(key, proc, shop_name, args.custom_rules)
            filename = f"sop_{key}.txt"
            filepath = os.path.join(os.path.abspath(OUTPUT_DIR), filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            saved.append(filename)
            print(f"  Generated: {filename}")

        print(f"\n  {len(saved)} SOPs saved to output/sop/")
        return

    # ── Custom free-form SOP ──
    if args.custom:
        title    = args.title or "Custom Procedure"
        content  = render_custom_sop(args.custom, title, shop_name, args.custom_rules)
        safe_key = title.lower().replace(' ', '_').replace('/', '_')[:40]
        filename = f"sop_{safe_key}.txt"
        filepath = os.path.join(os.path.abspath(OUTPUT_DIR), filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(content)
        print(f"\n  Saved: output/sop/{filename}")
        return

    # ── Built-in procedure ──
    # Resolve --process alias (backward compat)
    proc_key = args.procedure or args.process
    if not proc_key:
        parser.print_help()
        print("\nERROR: Provide --procedure, --custom, --all, or --list", file=sys.stderr)
        sys.exit(1)

    # Handle aliases (old --process names)
    if proc_key in PROCESS_ALIASES:
        proc_key = PROCESS_ALIASES[proc_key]

    if proc_key not in PROCEDURES:
        print(f"ERROR: Unknown procedure '{proc_key}'. Run --list to see available options.", file=sys.stderr)
        sys.exit(1)

    proc     = PROCEDURES[proc_key]
    content  = render_sop(proc_key, proc, shop_name, args.custom_rules)
    filename = f"sop_{proc_key}.txt"
    filepath = os.path.join(os.path.abspath(OUTPUT_DIR), filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    print(content)
    print(f"\n  Saved: output/sop/{filename}")


if __name__ == '__main__':
    main()
