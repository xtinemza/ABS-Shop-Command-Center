import AppointmentsForm from '../components/forms/AppointmentsForm'
import WelcomeKitForm from '../components/forms/WelcomeKitForm'
import WaitTimeForm from '../components/forms/WaitTimeForm'
import DeclinedForm from '../components/forms/DeclinedForm'
import ServiceHistoryForm from '../components/forms/ServiceHistoryForm'
import EstimatesForm from '../components/forms/EstimatesForm'
import InspectionForm from '../components/forms/InspectionForm'
import RecallForm from '../components/forms/RecallForm'
import EquipmentForm from '../components/forms/EquipmentForm'
import SopForm from '../components/forms/SopForm'
import PartsForm from '../components/forms/PartsForm'
import WarrantyForm from '../components/forms/WarrantyForm'
import ExpensesForm from '../components/forms/ExpensesForm'
import SeasonalForm from '../components/forms/SeasonalForm'
import ReferralsForm from '../components/forms/ReferralsForm'
import TechForm from '../components/forms/TechForm'
import MilestonesForm from '../components/forms/MilestonesForm'
import VehicleLookupForm from '../components/forms/VehicleLookupForm'
import RepairAssistantForm from '../components/forms/RepairAssistantForm'

export const modules = [
  // ── Front Office ─────────────────────────────────────────────────────────
  { id: "appointments", title: "Appointment Reminders", subtitle: "& Follow-Up Sequences", icon: "📅", category: "front-office", status: "core", desc: "Confirmations, day-before reminders, post-service thank-yous, 30-day check-ins, 6-month maintenance nudges. SMS, email & phone scripts.", impact: "Reduces no-shows up to 30%", tag: "HIGH IMPACT", formComponent: AppointmentsForm, apiCall: "appointments" },
  { id: "welcome-kit", title: "New Customer Welcome Kit", subtitle: "Generator", icon: "🎁", category: "front-office", status: "core", desc: "Thank-you letter, shop overview, vehicle-specific maintenance schedule, discount coupons, referral cards, and digital email version.", impact: "Boosts 2nd visit rate", tag: "RETENTION", formComponent: WelcomeKitForm, apiCall: "welcome-kit" },
  { id: "wait-time", title: "Wait Time Comms", subtitle: "Template Library", icon: "⏱", category: "front-office", status: "core", desc: "Check-in confirmations, tech-assigned alerts, mid-service updates, parts delay notices, completion alerts, pickup-ready messages.", impact: "#1 satisfaction driver", tag: "EXPERIENCE", formComponent: WaitTimeForm, apiCall: "wait-time" },
  { id: "declined", title: "Declined Services", subtitle: "Follow-Up Campaigns", icon: "🔄", category: "front-office", status: "core", desc: "Multi-touch sequences for unapproved work. Educational content, seasonal urgency triggers, re-engagement offers by service type.", impact: "Recovers 40-60% lost revenue", tag: "REVENUE", formComponent: DeclinedForm, apiCall: "declined" },
  { id: "seasonal", title: "Seasonal Campaign", subtitle: "Builder", icon: "🗓", category: "front-office", status: "core", desc: "Calendar-driven marketing — winterization, AC checks, tire rotation reminders. AI-generated SMS, email & social content.", impact: "Low-effort recurring revenue", tag: "MARKETING", formComponent: SeasonalForm, apiCall: "seasonal" },
  { id: "referrals", title: "Referral Tracking", subtitle: "& Reward System", icon: "🤝", category: "front-office", status: "core", desc: "Tracks referrer-to-referee chains, automated thank-yous, reward notifications, referral analytics, custom reward tiers.", impact: "Highest-trust lead channel", tag: "GROWTH", formComponent: ReferralsForm, apiCall: "referrals" },
  { id: "anniversaries", title: "Customer Milestone", subtitle: "Outreach", icon: "🎉", category: "front-office", status: "suggested", desc: "Auto-generated messages for 1-year anniversary, 5th visit, milestones. Simple touchpoints, strong retention signal.", impact: "Retention on autopilot", tag: "RETENTION", formComponent: MilestonesForm, apiCall: "milestones" },

  // ── Mechanics ────────────────────────────────────────────────────────────
  { id: "repair-assistant", title: "Repair Assistant", subtitle: "AI-Powered Diagnostics", icon: "🔬", category: "mechanics", status: "core", desc: "Enter symptoms + OBD codes → get ranked causes, tests to run, parts needed, labor estimate, and a plain-language script for the service advisor.", impact: "Faster, more accurate diagnoses", tag: "AI POWERED", formComponent: RepairAssistantForm, apiCall: "repair-assistant" },
  { id: "inspection-forms", title: "Vehicle Intake &", subtitle: "Inspection Forms", icon: "🔍", category: "mechanics", status: "core", desc: "Digital multi-point inspections — checkboxes, condition ratings, photo placeholders, notes. Customer-facing urgency reports.", impact: "Foundation of trust selling", tag: "OPERATIONS", formComponent: InspectionForm, apiCall: "inspection-forms" },
  { id: "estimate-narrator", title: "Repair Estimate", subtitle: "Narrator", icon: "💬", category: "mechanics", status: "core", desc: "Translates technical repair descriptions into plain language. Explains the why, deferral risk, and pricing context for transparency.", impact: "Increases approval rates", tag: "TRUST", formComponent: EstimatesForm, apiCall: "estimate-narrator" },
  { id: "service-history", title: "Vehicle Service History", subtitle: "Report Generator", icon: "📊", category: "mechanics", status: "core", desc: "Branded PDF: complete maintenance history, upcoming recommendations, vehicle health summary, visual timelines, color-coded status.", impact: "Builds lifetime loyalty", tag: "TRUST", formComponent: ServiceHistoryForm, apiCall: "service-history" },
  { id: "recall", title: "Vehicle Recall", subtitle: "Notification Service", icon: "🚨", category: "mechanics", status: "core", desc: "Cross-references VINs against recall databases. Personalized safety notifications explaining implications, offering to perform recall work.", impact: "Positions shop as safety advocate", tag: "SAFETY", formComponent: RecallForm, apiCall: "recall" },
  { id: "vehicle-lookup", title: "Vehicle DB", subtitle: "Direct Lookup", icon: "⚡", category: "mechanics", status: "core", desc: "Instant database query for vehicle specs, torque settings, intervals, and recalls. Uses 0 AI tokens.", impact: "Instant lookup speed", tag: "SPEED", formComponent: VehicleLookupForm, apiCall: "vehicle-lookup" },

  // ── Inventory ────────────────────────────────────────────────────────────
  { id: "parts-inventory", title: "Parts Inventory", subtitle: "& Reorder Alerts", icon: "📦", category: "inventory", status: "core", desc: "Stock levels, minimum thresholds, preferred vendors, cost data. Auto-generated POs and reorder alerts when stock drops.", impact: "Eliminates stockouts", tag: "OPERATIONS", formComponent: PartsForm, apiCall: "parts-inventory" },
  { id: "warranty", title: "Warranty Claims", subtitle: "Tracker & Docs", icon: "🛡", category: "inventory", status: "core", desc: "Claim forms, documentation checklists, vendor contacts, status tracking, reimbursement reconciliation, monthly recovery reports.", impact: "Recovers thousands annually", tag: "REVENUE", formComponent: WarrantyForm, apiCall: "warranty" },
  { id: "equipment", title: "Equipment Maintenance", subtitle: "& Calibration Logger", icon: "🔧", category: "inventory", status: "core", desc: "Tracks lifts, alignment machines, scanners, tire machines. Maintenance schedules, calibration dates, service history, warranties.", impact: "Prevents costly downtime", tag: "COMPLIANCE", formComponent: EquipmentForm, apiCall: "equipment" },

  // ── Operations ───────────────────────────────────────────────────────────
  { id: "sop-library", title: "SOP Library", subtitle: "Builder", icon: "📋", category: "operations", status: "core", desc: "SOPs for check-in, inspection, estimates, parts ordering, QC, test drives, delivery, warranty claims, complaints, hazmat.", impact: "Enables scaling & consistency", tag: "SCALE", formComponent: SopForm, apiCall: "sop-library" },
  { id: "expenses", title: "Shop Expenses", subtitle: "Categorization & Reports", icon: "💰", category: "operations", status: "core", desc: "Categorizes all expenses — parts, labor, rent, utilities, insurance, marketing, tools, training. Trends, ratios & budget variance.", impact: "Reveals hidden waste", tag: "FINANCIAL", formComponent: ExpensesForm, apiCall: "expenses" },
  { id: "tech-productivity", title: "Tech Productivity", subtitle: "& Labor Summary", icon: "👨‍🔧", category: "operations", status: "suggested", desc: "Weekly per-tech summaries — efficiency rates, over-estimate flagging, revenue per tech breakdown. Stops margin leaks.", impact: "Protects profit margins", tag: "FINANCIAL", formComponent: TechForm, apiCall: "tech-productivity" },
]

export const categoryMeta = {
  all: { label: "ALL MODULES", count: modules.length },
  "front-office": { label: "FRONT OFFICE", count: modules.filter(m => m.category === "front-office").length },
  mechanics: { label: "MECHANICS", count: modules.filter(m => m.category === "mechanics").length },
  inventory: { label: "INVENTORY", count: modules.filter(m => m.category === "inventory").length },
  operations: { label: "OPERATIONS", count: modules.filter(m => m.category === "operations").length },
}

export const featureData = {
  appointments: ["Appointment confirmation (SMS + email)", "Day-before reminder with prep instructions", "Day-of notification with arrival details", "Post-service thank-you message", "30-day follow-up health check", "6-month maintenance reminder", "Phone script versions for staff", "Customizable by service type"],
  "welcome-kit": ["Personalized thank-you letter", "Shop overview & team intro sheet", "Vehicle-specific maintenance schedule", "New customer discount coupons", "Referral cards with tracking codes", "Digital email version", "Branded PDF for print"],
  "wait-time": ["Initial check-in confirmation", "Technician-assigned notification", "Mid-service progress updates", "Parts delay notifications", "Completion alerts", "Pickup-ready messages", "Estimated time adjustments"],
  declined: ["Multi-touch email sequence", "Service-specific educational content", "Seasonal urgency triggers", "Re-engagement offers", "Segmented by service type", "Time-since-visit escalation", "SMS + email versions"],
  "service-history": ["Complete maintenance timeline", "Upcoming service recommendations", "Vehicle health summary score", "Visual timeline with milestones", "Color-coded status indicators", "Branded PDF export", "Shareable for vehicle resale"],
  "estimate-narrator": ["Technical-to-plain-language translation", "Why-this-repair-matters explanation", "Risk-of-deferral warnings", "Pricing context and breakdown", "Customer-friendly estimate PDF", "Service advisor talking points"],
  "inspection-forms": ["Multi-point digital inspection", "Condition rating system", "Photo documentation placeholders", "Urgency color coding", "Customer-facing summary report", "Customizable by vehicle type"],
  recall: ["VIN-based recall lookup", "Year/make/model cross-reference", "Personalized safety notifications", "Recall severity explanations", "Service scheduling integration", "Monthly batch scanning"],
  equipment: ["Equipment inventory tracking", "Maintenance schedule calendar", "Calibration due date alerts", "Service history log per unit", "Vendor warranty tracking", "Annual compliance reports"],
  "sop-library": ["17 built-in procedures ready to generate", "Customer check-in & delivery workflows", "Vehicle inspection & QC checklists", "Parts ordering & warranty claim procedures", "Hazmat disposal & compliance SOPs", "Custom SOP builder for shop-specific processes"],
  "parts-inventory": ["Real-time stock tracking", "Minimum threshold alerts", "Auto-generated purchase orders", "Vendor management database", "Cost tracking per part", "Dead inventory flagging"],
  warranty: ["Claim initiation forms", "Documentation checklists", "Vendor contact database", "Claim status tracking board", "Reimbursement reconciliation", "Monthly recovery reports"],
  expenses: ["Multi-category expense tracking", "Monthly & annual reports", "Trend analysis visualizations", "Expense-to-revenue ratios", "Budget variance calculations", "Tax preparation summaries"],
  seasonal: ["AI-generated campaign copy per season", "SMS + email + social versions", "Service-specific promotions", "Staff briefing per campaign", "Offer & expiry date injection"],
  referrals: ["Referrer-to-referee tracking", "Automated thank-you messages", "Reward notification system", "Referral source analytics", "Custom reward tiers"],
  "tech-productivity": ["Hours logged per technician", "Efficiency rate calculations", "Over-estimate job flagging", "Revenue per tech breakdown", "Weekly summary reports"],
  anniversaries: ["1-year anniversary messages", "Visit milestone triggers", "Personalized outreach templates", "SMS + email versions", "Automated scheduling"],
  "vehicle-lookup": ["Direct database query", "Zero AI token cost", "Torque specifications", "Maintenance intervals", "Known issues & recalls", "Fluid capacities and specs"],
  "repair-assistant": ["Symptom + OBD code input", "Vehicle KB auto-injection", "Ranked likely causes with confidence", "Specific diagnostic tests to run", "Parts needed & labor estimate", "Plain-language service advisor script"],
}
