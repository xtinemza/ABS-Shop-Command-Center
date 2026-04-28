"""
Shop Command Center — Marketing Templates Knowledge Base
Pre-written social media posts, CTAs, and promos for common auto services.
Endpoints check here first; only fall back to AI for unknown service types.

Placeholders: {shop_name} {phone} {promo_line} {hashtag} {service} {offer} {expiry}
"""

# ── Social Media Templates ────────────────────────────────────────────────────

SOCIAL = {
    "oil_change": {
        "keywords": ["oil change", "oil service", "oil & filter", "oil and filter",
                     "synthetic oil", "conventional oil", "lube", "oil change special"],
        "instagram": (
            "🔧 Don't ignore your oil change!\n\n"
            "Fresh oil = a happy engine. We make it quick, easy, and affordable.\n\n"
            "✅ Full synthetic available\n"
            "✅ In and out in under an hour\n"
            "✅ Multi-point visual check included\n\n"
            "📞 Book now: {phone}\n"
            "🏪 {shop_name}\n\n"
            "{promo_line}"
            "#OilChange #AutoCare #CarMaintenance #LocalShop #EngineHealth #{hashtag}"
        ),
        "facebook": (
            "⚠️ When was your last oil change?\n\n"
            "Most vehicles need fresh oil every 5,000–10,000 miles — and skipping it "
            "is one of the fastest ways to wear out your engine.\n\n"
            "At {shop_name}, we make it painless:\n"
            "• Conventional and full synthetic options\n"
            "• Quick turnaround — most done in under an hour\n"
            "• Multi-point visual inspection included\n"
            "• Friendly, honest service every time\n\n"
            "{promo_line}"
            "📞 Call or text: {phone} — Walk-ins welcome!"
        ),
        "google": (
            "Time for an oil change? {shop_name} offers fast, affordable oil changes "
            "with full synthetic options. Walk-ins welcome — call {phone}."
        ),
    },

    "brakes": {
        "keywords": ["brake", "brakes", "brake pad", "brake pads", "brake service",
                     "rotor", "rotors", "stopping", "brake repair", "brake inspection"],
        "instagram": (
            "🛑 Squeaking or grinding when you stop?\n\n"
            "Don't wait on brakes — your safety depends on them.\n\n"
            "🔍 Free brake inspection with any service\n"
            "🔧 OEM and quality aftermarket options\n"
            "⚡ Same-day service available\n\n"
            "📞 {phone} | {shop_name}\n\n"
            "{promo_line}"
            "#BrakeService #CarSafety #AutoRepair #BrakePads #StaySafe #{hashtag}"
        ),
        "facebook": (
            "🚨 Your brakes are your most important safety system — "
            "don't ignore the warning signs.\n\n"
            "Squeaking, grinding, pulling to one side, or a soft pedal are all signs "
            "it's time for a brake inspection.\n\n"
            "At {shop_name}, we:\n"
            "✅ Inspect brakes FREE with any service\n"
            "✅ Give you an honest assessment — no pressure\n"
            "✅ Offer OEM and quality aftermarket parts\n"
            "✅ Complete most brake jobs same day\n\n"
            "{promo_line}"
            "Your safety is worth it. Call us at {phone}."
        ),
        "google": (
            "Brake problems? {shop_name} offers free brake inspections and same-day "
            "service. Honest estimates, quality parts. Call {phone}."
        ),
    },

    "tires": {
        "keywords": ["tire", "tires", "tire rotation", "new tires", "flat tire",
                     "tire repair", "tpms", "wheel rotation", "tire change", "tread"],
        "instagram": (
            "🔄 Tires are your only contact with the road — keep them in top shape!\n\n"
            "✅ Tire rotations extend tire life up to 20%\n"
            "✅ New tires in all major brands\n"
            "✅ Free tire pressure check anytime\n\n"
            "📞 {phone} | {shop_name}\n\n"
            "{promo_line}"
            "#TireRotation #NewTires #TireSafety #AutoService #{hashtag}"
        ),
        "facebook": (
            "🚗 How are your tires holding up?\n\n"
            "Worn or uneven tires affect your fuel economy, handling, and safety — "
            "especially in wet conditions.\n\n"
            "{shop_name} offers:\n"
            "• Tire rotations to maximize tread life\n"
            "• New tire installation in major brands\n"
            "• Flat repairs and TPMS service\n"
            "• Free tire pressure checks — always\n\n"
            "{promo_line}"
            "📞 {phone} — come in today!"
        ),
        "google": (
            "New tires or a rotation? {shop_name} carries major brands and offers "
            "fast installation. Free tire pressure checks. Call {phone}."
        ),
    },

    "alignment": {
        "keywords": ["alignment", "wheel alignment", "align", "four wheel alignment",
                     "4 wheel alignment", "pulling", "steering wheel off"],
        "instagram": (
            "↔️ Is your car pulling to one side?\n\n"
            "Misalignment wears your tires fast and makes your car harder to control.\n\n"
            "🎯 Precision alignment service\n"
            "🔧 Improves fuel economy too\n"
            "✅ Most vehicles done in under an hour\n\n"
            "📞 {phone} | {shop_name}\n\n"
            "{promo_line}"
            "#WheelAlignment #AutoRepair #TireCare #CarMaintenance #{hashtag}"
        ),
        "facebook": (
            "Is your steering wheel off-center? Tires wearing unevenly? "
            "That's a classic alignment issue.\n\n"
            "Proper wheel alignment:\n"
            "✅ Extends tire life significantly\n"
            "✅ Improves fuel efficiency\n"
            "✅ Makes your car safer and easier to handle\n\n"
            "{shop_name} uses precision equipment to get your alignment spot-on.\n\n"
            "{promo_line}"
            "📞 Book today: {phone}"
        ),
        "google": (
            "Wheel alignment at {shop_name} — precision equipment, quick turnaround. "
            "Fixes pulling, uneven wear, and improves fuel economy. Call {phone}."
        ),
    },

    "battery": {
        "keywords": ["battery", "batteries", "dead battery", "car battery",
                     "won't start", "slow start", "jump start", "battery replacement"],
        "instagram": (
            "🔋 Don't get stranded with a dead battery!\n\n"
            "Most batteries last 3–5 years. If yours is getting close, it's time.\n\n"
            "⚡ Free battery test while you wait\n"
            "🔧 Quality replacements installed fast\n"
            "🛡️ Charging system check included\n\n"
            "📞 {phone} | {shop_name}\n\n"
            "{promo_line}"
            "#CarBattery #AutoRepair #DontGetStranded #{hashtag}"
        ),
        "facebook": (
            "⚠️ Slow to start in the morning? Dashboard lights flickering? "
            "Your battery might be on its way out.\n\n"
            "Stop by {shop_name} for a FREE battery test — takes about 5 minutes "
            "and could save you from getting stranded.\n\n"
            "If you need a replacement, we carry quality batteries for all makes "
            "and models and install them on the spot.\n\n"
            "{promo_line}"
            "📞 {phone} — walk-ins always welcome."
        ),
        "google": (
            "Free battery testing at {shop_name}. We carry quality replacements for "
            "all vehicles and install on the spot. Walk-ins welcome — call {phone}."
        ),
    },

    "ac": {
        "keywords": ["ac", "a/c", "air conditioning", "air conditioner",
                     "ac recharge", "ac service", "ac repair", "cooling", "hvac",
                     "heat not working", "ac not working", "air not cold"],
        "instagram": (
            "🌡️ AC not keeping up with the heat?\n\n"
            "Don't sweat it — we'll get your cool air back fast.\n\n"
            "❄️ AC recharge & leak check\n"
            "🔧 Compressor & component service\n"
            "✅ Most AC repairs same day\n\n"
            "📞 {phone} | {shop_name}\n\n"
            "{promo_line}"
            "#ACRepair #CarAC #StayCool #AutoRepair #{hashtag}"
        ),
        "facebook": (
            "☀️ Is your AC ready for the heat?\n\n"
            "There's nothing worse than a hot car in the middle of summer. "
            "If your AC is blowing warm air, running weak, or making noise, "
            "bring it to {shop_name}.\n\n"
            "We offer:\n"
            "• AC recharge (refrigerant check & refill)\n"
            "• Leak detection and repair\n"
            "• Compressor and component service\n"
            "• Cabin air filter replacement\n\n"
            "{promo_line}"
            "📞 Call {phone} to get your cool air back today."
        ),
        "google": (
            "AC not working? {shop_name} does AC recharges, leak checks, and full "
            "HVAC repairs. Most jobs completed same day. Call {phone}."
        ),
    },

    "seasonal": {
        "keywords": ["seasonal", "winter prep", "summer prep", "spring check",
                     "fall check", "winter ready", "summer ready", "seasonal special",
                     "seasonal service", "season change"],
        "instagram": (
            "🍂 Season change = car checkup time!\n\n"
            "Don't let the weather catch you off guard. A seasonal inspection "
            "keeps you safe and saves money later.\n\n"
            "✅ Tires, brakes, fluids & battery\n"
            "✅ Wiper blades & lights\n"
            "✅ Full multi-point check\n\n"
            "📞 {phone} | {shop_name}\n\n"
            "{promo_line}"
            "#SeasonalService #CarCare #AutoMaintenance #WinterReady #{hashtag}"
        ),
        "facebook": (
            "The seasons are changing — is your car ready?\n\n"
            "At {shop_name}, our seasonal inspection covers everything that matters:\n\n"
            "🔍 Tire tread and pressure\n"
            "🔋 Battery load test\n"
            "🛑 Brake inspection\n"
            "💧 All fluid levels\n"
            "🌧️ Wiper blades and washer fluid\n"
            "💡 Lights and visibility check\n\n"
            "Catch small problems before they become expensive ones.\n\n"
            "{promo_line}"
            "📞 Book your seasonal check: {phone}"
        ),
        "google": (
            "Seasonal vehicle inspection at {shop_name} — tires, battery, brakes, "
            "fluids, wipers, and more. Get ready before the weather changes. "
            "Call {phone}."
        ),
    },

    "inspection": {
        "keywords": ["inspection", "multi-point", "mpi", "vehicle inspection",
                     "car inspection", "check engine", "diagnostic", "vehicle check",
                     "pre-purchase", "pre purchase"],
        "instagram": (
            "🔍 Know exactly what's going on with your car.\n\n"
            "Our multi-point inspection gives you the full picture — "
            "no surprises, no pressure.\n\n"
            "✅ 30+ point visual inspection\n"
            "📋 Written report you keep\n"
            "🔧 Honest recommendations only\n\n"
            "📞 {phone} | {shop_name}\n\n"
            "{promo_line}"
            "#CarInspection #HonestMechanic #AutoRepair #MultiPoint #{hashtag}"
        ),
        "facebook": (
            "💡 Not sure what's going on with your vehicle? Let us take a look.\n\n"
            "{shop_name}'s multi-point inspection covers:\n"
            "• Engine and fluid levels\n"
            "• Brakes and tire condition\n"
            "• Lights and electrical\n"
            "• Belts, hoses, and filters\n"
            "• Suspension and steering\n\n"
            "You get a written report of everything we find — and we never "
            "recommend work you don't need.\n\n"
            "{promo_line}"
            "📞 Schedule today: {phone}"
        ),
        "google": (
            "Multi-point vehicle inspection at {shop_name}. Full written report, "
            "honest recommendations. {promo_line}Call {phone}."
        ),
    },

    "transmission": {
        "keywords": ["transmission", "trans service", "transmission fluid",
                     "trans fluid", "transmission flush", "shifting", "gear"],
        "instagram": (
            "⚙️ When did you last service your transmission?\n\n"
            "Most manufacturers recommend a fluid change every 30,000–60,000 miles. "
            "Skipping it is expensive.\n\n"
            "✅ Drain & fill or full flush\n"
            "✅ Filter replacement where applicable\n"
            "✅ All makes and models\n\n"
            "📞 {phone} | {shop_name}\n\n"
            "{promo_line}"
            "#TransmissionService #AutoMaintenance #CarCare #{hashtag}"
        ),
        "facebook": (
            "Your transmission is one of the most expensive components to replace — "
            "and regular fluid changes are the best way to protect it.\n\n"
            "{shop_name} offers transmission fluid services for all makes and models. "
            "We'll check your service history and recommend exactly what your "
            "vehicle needs.\n\n"
            "{promo_line}"
            "📞 Call {phone} to schedule."
        ),
        "google": (
            "Transmission service at {shop_name} — fluid changes and flushes for "
            "all makes and models. Protect your drivetrain. Call {phone}."
        ),
    },

    "coolant": {
        "keywords": ["coolant", "radiator", "cooling system", "antifreeze",
                     "coolant flush", "overheating", "radiator flush"],
        "instagram": (
            "🌡️ Coolant flush time?\n\n"
            "Old coolant loses its protective properties and can cause overheating "
            "or internal corrosion. Don't wait.\n\n"
            "✅ Full cooling system flush\n"
            "✅ New coolant to OEM spec\n"
            "✅ Hose and cap inspection included\n\n"
            "📞 {phone} | {shop_name}\n\n"
            "{promo_line}"
            "#CoolantFlush #RadiatorService #CarMaintenance #{hashtag}"
        ),
        "facebook": (
            "Is your coolant still doing its job?\n\n"
            "Over time, coolant breaks down and stops protecting your engine from "
            "overheating and corrosion. Most vehicles need a flush every 2–5 years.\n\n"
            "{shop_name} does a complete cooling system flush with fresh coolant "
            "matched to your vehicle's specs — and we inspect hoses and the radiator cap too.\n\n"
            "{promo_line}"
            "📞 {phone} to schedule."
        ),
        "google": (
            "Coolant flush and radiator service at {shop_name}. Prevents overheating "
            "and engine corrosion. All makes and models. Call {phone}."
        ),
    },

    "referral": {
        "keywords": ["referral", "refer a friend", "word of mouth", "review",
                     "google review", "recommend", "tell a friend"],
        "instagram": (
            "❤️ Love your experience at {shop_name}?\n\n"
            "Tell a friend! We built this shop on referrals and we never take "
            "that trust for granted.\n\n"
            "📲 Tag someone who needs a great mechanic\n"
            "⭐ Leave us a Google review\n"
            "🎁 Ask us about our referral rewards\n\n"
            "📞 {phone}\n\n"
            "#Referral #LocalShop #HonestMechanic #CarCare #{hashtag}"
        ),
        "facebook": (
            "The greatest compliment we can receive is a referral. 🙏\n\n"
            "If {shop_name} has taken good care of your vehicle, please consider "
            "sharing our name with a friend or family member who needs a shop "
            "they can trust.\n\n"
            "We treat every customer like a neighbor — because most of you are.\n\n"
            "📞 {phone} | Tag someone below who could use a great mechanic!"
        ),
        "google": (
            "Love {shop_name}? Share the word! We appreciate every referral and "
            "strive to earn your trust with every visit. Call {phone}."
        ),
    },

    "general": {
        "keywords": [],   # catch-all fallback
        "instagram": (
            "🔧 Your car works hard for you — return the favor.\n\n"
            "At {shop_name}, we keep your vehicle running its best with honest "
            "service and quality parts.\n\n"
            "✅ All makes and models\n"
            "✅ Experienced technicians\n"
            "✅ Fair, upfront pricing\n\n"
            "📞 {phone}\n\n"
            "{promo_line}"
            "#AutoRepair #CarCare #LocalShop #HonestMechanic #{hashtag}"
        ),
        "facebook": (
            "Looking for an auto repair shop you can actually trust?\n\n"
            "{shop_name} serves our community with honest, quality car care. "
            "No upselling, no surprises — just the work your vehicle actually "
            "needs at a fair price.\n\n"
            "{promo_line}"
            "Give us a call at {phone} or stop by. We'd love to earn your trust."
        ),
        "google": (
            "{shop_name} — honest auto repair and maintenance for all makes and "
            "models. Fair prices, experienced technicians. Call {phone}."
        ),
    },
}


# ── CTA Templates ─────────────────────────────────────────────────────────────

CTA = {
    "book": {
        "keywords": ["book", "appointment", "schedule", "reserve", "booking"],
        "button":   "Book Your Appointment",
        "headline": "Schedule Service at {shop_name} — Quick & Easy",
        "email":    "Ready to get it on the calendar? Click below to book your appointment at {shop_name}. Takes 60 seconds.",
        "sms":      "Book @ {shop_name}: {phone}",
    },
    "call": {
        "keywords": ["call", "phone", "contact", "reach", "speak"],
        "button":   "Call {shop_name} Now",
        "headline": "Questions? We're One Call Away — {phone}",
        "email":    "Have questions about your vehicle? Our team at {shop_name} is ready to help. Call {phone} today.",
        "sms":      "Call {shop_name}: {phone}",
    },
    "estimate": {
        "keywords": ["estimate", "quote", "price", "cost", "how much", "pricing"],
        "button":   "Get a Free Estimate",
        "headline": "Free, No-Obligation Estimates at {shop_name}",
        "email":    "Wondering what a repair will cost? Get a free, honest estimate from {shop_name}. No pressure, no surprises. Call {phone}.",
        "sms":      "Free estimate @ {shop_name}: {phone}",
    },
    "promo": {
        "keywords": ["deal", "offer", "discount", "special", "save", "coupon", "promotion"],
        "button":   "Claim Your Discount",
        "headline": "Limited-Time Offer at {shop_name} — Don't Miss Out",
        "email":    "This offer won't last long. Bring this email to {shop_name} to redeem your discount. Call {phone} to schedule.",
        "sms":      "Save @ {shop_name}: {phone}",
    },
    "review": {
        "keywords": ["review", "feedback", "google", "rating", "testimonial", "yelp"],
        "button":   "Leave Us a Review",
        "headline": "Love Your Experience at {shop_name}? Tell Others!",
        "email":    "Thank you for choosing {shop_name}! A quick Google review means the world to us and helps your neighbors find honest auto care.",
        "sms":      "Review {shop_name} — thank you!",
    },
    "general": {
        "keywords": [],
        "button":   "Visit {shop_name} Today",
        "headline": "Trusted Auto Repair at {shop_name}",
        "email":    "Your vehicle deserves the best care. {shop_name} is here for all your auto repair and maintenance needs. Call {phone} to schedule.",
        "sms":      "{shop_name}: {phone}",
    },
}


# ── Promo Templates ───────────────────────────────────────────────────────────

PROMO = {
    "oil_change": {
        "keywords": ["oil change", "oil & filter", "oil service", "synthetic", "conventional oil"],
        "sms":          "🔧 {offer} at {shop_name}! Expires {expiry}. Call/text {phone}. Limited spots.",
        "email_subject": "{offer} at {shop_name} — Expires {expiry}",
        "email_body":   (
            "Hi there,\n\n"
            "Don't miss out — {shop_name} is offering {offer} through {expiry}.\n\n"
            "This is a great time to get your oil changed before it's overdue.\n\n"
            "👉 Call or text {phone} to schedule\n"
            "👉 Walk-ins welcome while spots last\n\n"
            "We look forward to seeing you!\n"
            "— The Team at {shop_name}"
        ),
        "social":       "🔧 {offer} at {shop_name}!\n\nFresh oil, happy engine. Expires {expiry}.\n\n📞 {phone}",
    },

    "brakes": {
        "keywords": ["brake", "brakes", "brake pad", "rotor", "brake service"],
        "sms":          "🛑 {offer} at {shop_name}. Safety first! Expires {expiry}. Call {phone}.",
        "email_subject": "Brake Special at {shop_name} — Offer Ends {expiry}",
        "email_body":   (
            "Hi there,\n\n"
            "Your safety matters. That's why {shop_name} is offering {offer} — "
            "valid through {expiry}.\n\n"
            "If you've been hearing squeaking or grinding, now's the time.\n\n"
            "📞 Call {phone} to schedule\n"
            "✅ Free inspection with every brake service\n\n"
            "— The Team at {shop_name}"
        ),
        "social":       "🛑 {offer} at {shop_name}!\n\nSafety first — don't put this off. Expires {expiry}.\n\n📞 {phone}",
    },

    "tires": {
        "keywords": ["tire", "tires", "tire rotation", "new tires", "wheel"],
        "sms":          "🔄 {offer} at {shop_name}! Expires {expiry}. Call {phone} to book.",
        "email_subject": "Tire Special at {shop_name} — Valid Through {expiry}",
        "email_body":   (
            "Hi there,\n\n"
            "{shop_name} is offering {offer} through {expiry}.\n\n"
            "Regular tire service extends tread life and keeps you safer on the road.\n\n"
            "📞 Call {phone} to schedule — walk-ins welcome.\n\n"
            "— The Team at {shop_name}"
        ),
        "social":       "🔄 {offer} at {shop_name}!\n\nKeep those tires in shape. Expires {expiry}.\n\n📞 {phone}",
    },

    "seasonal": {
        "keywords": ["seasonal", "winter", "summer", "spring", "fall", "season"],
        "sms":          "⚠️ {offer} — be ready for the season! Expires {expiry}. Book at {shop_name}: {phone}",
        "email_subject": "Seasonal Special at {shop_name} — Limited Time, Expires {expiry}",
        "email_body":   (
            "Hi there,\n\n"
            "Season change is here and {shop_name} wants to make sure "
            "your vehicle is ready.\n\n"
            "{offer} — valid through {expiry}.\n\n"
            "Our seasonal check covers tires, battery, brakes, fluids, and more.\n\n"
            "📞 Call {phone} to schedule.\n\n"
            "— The Team at {shop_name}"
        ),
        "social":       "🍂 {offer} at {shop_name}!\n\nDon't let the season catch you off guard. Expires {expiry}.\n\n📞 {phone}",
    },

    "inspection": {
        "keywords": ["inspection", "diagnostic", "multi-point", "check engine"],
        "sms":          "🔍 {offer} at {shop_name}! Know your car's health. Expires {expiry}. Call {phone}.",
        "email_subject": "Free/Discounted Inspection at {shop_name} — Expires {expiry}",
        "email_body":   (
            "Hi there,\n\n"
            "{shop_name} is offering {offer} through {expiry}.\n\n"
            "Our multi-point inspection covers 30+ items with a written report — "
            "no surprises, no pressure.\n\n"
            "📞 Call {phone} to schedule.\n\n"
            "— The Team at {shop_name}"
        ),
        "social":       "🔍 {offer} at {shop_name}!\n\nKnow what's going on with your car. Expires {expiry}.\n\n📞 {phone}",
    },

    "general": {
        "keywords": [],
        "sms":          "🚗 {offer} at {shop_name}! Expires {expiry}. Call {phone} to book your spot.",
        "email_subject": "Special Offer from {shop_name} — Expires {expiry}",
        "email_body":   (
            "Hi there,\n\n"
            "{shop_name} is offering {offer} — valid through {expiry}.\n\n"
            "We appreciate your business and want to make car care as easy "
            "and affordable as possible.\n\n"
            "📞 Call or text {phone} to schedule\n"
            "👉 Walk-ins welcome\n\n"
            "Thank you,\n"
            "— The Team at {shop_name}"
        ),
        "social":       "🎉 {offer} at {shop_name}!\n\nDon't miss this — expires {expiry}.\n\n📞 {phone}",
    },
}


# ── Helpers ───────────────────────────────────────────────────────────────────

def _fill(template: str, **kw) -> str:
    for k, v in kw.items():
        template = template.replace("{" + k + "}", v or "")
    return template.strip()


def _hashtag(shop_name: str) -> str:
    return "".join(c for c in shop_name if c.isalnum())[:18] or "AutoRepair"


def _match(lookup: dict, text: str) -> dict | None:
    """Return first template whose keywords appear in text, else None."""
    t = text.lower()
    for key, tmpl in lookup.items():
        if key == "general":
            continue
        if any(k in t for k in tmpl.get("keywords", [])):
            return tmpl
    return None


def find_social(service_type: str) -> dict | None:
    return _match(SOCIAL, service_type)

def find_cta(goal: str) -> dict | None:
    return _match(CTA, goal)

def find_promo(service_type: str, offer: str = "") -> dict | None:
    return _match(PROMO, f"{service_type} {offer}")


# Expose template names for the frontend KB panel
SOCIAL_SERVICES  = [k for k in SOCIAL if k != "general"]   # 11 services
CTA_GOALS        = [k for k in CTA   if k != "general"]     # 5 goals
PROMO_SERVICES   = [k for k in PROMO  if k != "general"]    # 5 services
