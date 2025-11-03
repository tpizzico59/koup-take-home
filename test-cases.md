# Test Scenarios
## Overview
This document provides comprehensive test scenarios to demonstrate the full capabilities of the Care Coordinator Assistant, covering all requirements, edge cases, and advanced features.

---

## 1. BASIC APPOINTMENT BOOKING (Happy Path)

### Scenario 1.1: Complete Appointment Booking Flow
**Goal:** Book a complete appointment from start to finish

**User:** "I need to book an appointment for John Doe"

**Expected Agent Behavior:**
- Proactively asks for DOB to search patient
- Calls `search_patient` tool
- Reviews patient's referrals and suggests Dr. House for Orthopedics (patient has referral)
- Mentions patient last saw Dr. House on 8/12/24 (ESTABLISHED visit)
- Asks which provider the nurse prefers

**User:** "Let's go with Dr. House"

**Expected Agent Behavior:**
- Asks about insurance
- Calls `check_insurance` tool after receiving answer
- If accepted: proceeds to find times
- Calls `check_appointment_history` to confirm ESTABLISHED (15 min)
- Calls `list_available_slots` with correct duration
- Presents 3-5 available time slots with arrival times

**User:** "Monday at 9:00 AM works"

**Expected Agent Behavior:**
- Summarizes ALL details:
  - Patient: John Doe (DOB: 01/01/1975)
  - Provider: Dr. Gregory House at PPTH Orthopedics
  - Date & Time: [specific date] at 9:00 AM
  - Type: ESTABLISHED (15 minutes)
  - Insurance: [name]
  - Arrival: 8:50 AM (10 minutes early)
- Asks for explicit confirmation

**User:** "Yes, book it"

**Expected Agent Behavior:**
- Calls `create_appointment` tool
- Returns confirmation with appointment ID
- Provides complete summary

**Success Criteria:**
✓ All 4 required pieces gathered (patient, provider, type, location)
✓ Correct appointment type determined (ESTABLISHED)
✓ Only books after explicit approval
✓ Provides confirmation number

---

## 2. INSURANCE VERIFICATION

### Scenario 2.1: Accepted Insurance
**User:** "Does this patient have Blue Cross Blue Shield?"

**Expected Agent Behavior:**
- Calls `check_insurance` with "Blue Cross Blue Shield"
- Matches against "Blue Cross Blue Shield of North Carolina"
- Confirms it's accepted
- Proceeds with booking

**Success Criteria:**
✓ Smart matching (partial name matching)
✓ Clear confirmation message

### Scenario 2.2: Rejected Insurance with Self-Pay Option
**User:** "The patient has Kaiser Permanente"

**Expected Agent Behavior:**
- Calls `check_insurance` tool
- Returns that Kaiser is NOT accepted
- Proactively calls `get_self_pay_rate` for the specialty
- Lists all accepted insurances
- Provides self-pay cost ($300 for Orthopedics)
- Asks if they want to proceed with self-pay or choose different provider

**Success Criteria:**
✓ Clear explanation that insurance isn't accepted
✓ Provides list of accepted insurances
✓ Proactively shows self-pay cost
✓ Offers alternatives

### Scenario 2.3: Partial Insurance Name
**User:** "They have Aetna"

**Expected Agent Behavior:**
- Calls `check_insurance`
- Matches "Aetna" exactly
- Confirms acceptance

**Success Criteria:**
✓ Handles partial/exact matches intelligently

---

## 3. PROVIDER SELECTION & AVAILABILITY

### Scenario 3.1: Provider Not Available at Requested Time
**User:** "Can Dr. House see the patient on Thursday at 6pm?"

**Expected Agent Behavior:**
- Recognizes 6pm is outside office hours (M-W 9am-5pm, Th-F 9am-5pm)
- Calls `list_available_slots` for Thursday
- Explains Dr. House's hours at PPTH are M-W, but he's at Jefferson Hospital Th-F
- Suggests nearest available times within office hours
- Offers alternative: "Would you like to see Dr. House at Jefferson Hospital on Thursday, or at PPTH earlier in the week?"

**Success Criteria:**
✓ Respects office hours
✓ Suggests alternatives proactively
✓ Handles multiple department locations

### Scenario 3.2: Alternative Providers
**User:** "Who else is available for Orthopedics?"

**Expected Agent Behavior:**
- Calls `list_providers` with specialty="Orthopedics"
- Lists both Dr. House and Dr. Brennan
- Shows their locations and hours
- Notes which ones patient has referrals for
- Highlights Dr. Brennan's different hours (Tu-Th 10am-4pm)

**Success Criteria:**
✓ Lists all providers for specialty
✓ Shows locations and hours
✓ Helps nurse compare options

### Scenario 3.3: Checking Specific Provider Availability
**User:** "What days does Dr. Brennan work?"

**Expected Agent Behavior:**
- Calls `list_providers` or references cached data
- States: "Dr. Brennan works at Jefferson Hospital on Tuesday through Thursday, 10am-4pm"

**Success Criteria:**
✓ Accurate provider information
✓ Clear schedule details

---

## 4. APPOINTMENT TYPE DETERMINATION (NEW vs ESTABLISHED)

### Scenario 4.1: Established Patient
**User:** "Book John Doe with Dr. House"

**Expected Agent Behavior:**
- Calls `check_appointment_history`
- Finds appointment on 8/12/24 (within 5 years)
- Determines: ESTABLISHED
- Uses 15-minute duration
- States: "Since John last saw Dr. House on 8/12/24, this will be an ESTABLISHED appointment (15 minutes). Please arrive 10 minutes early."

**Success Criteria:**
✓ Correctly identifies ESTABLISHED
✓ Uses 15-minute slots
✓ Mentions 10-minute early arrival

### Scenario 4.2: New Patient (No History)
**User:** "Book John Doe with Dr. Yang for surgery"

**Expected Agent Behavior:**
- Calls `check_appointment_history`
- No previous appointments with Dr. Yang found
- Determines: NEW
- Uses 30-minute duration
- States: "John hasn't seen Dr. Yang before, so this will be a NEW patient appointment (30 minutes). Please arrive 30 minutes early."

**Success Criteria:**
✓ Correctly identifies NEW
✓ Uses 30-minute slots
✓ Mentions 30-minute early arrival

### Scenario 4.3: Old History (>5 years)
**User:** "Has John Doe seen Dr. Grey before?"

**Expected Agent Behavior:**
- Calls `check_appointment_history`
- Finds appointment on 3/05/18 (>5 years ago)
- Explains: "John last saw Dr. Grey on 3/05/18, which is more than 5 years ago, so this would be considered a NEW patient appointment."

**Success Criteria:**
✓ Correctly applies 5-year rule
✓ Explains reasoning clearly

---

## 5. PATIENT CONTEXT & REFERRALS

### Scenario 5.1: Patient with Referral
**User:** "I need to schedule John Doe"

**Expected Agent Behavior:**
- Calls `search_patient`
- Reviews referrals in patient data
- Proactively suggests: "I see John has a referral for Orthopedics with Dr. House. Would you like to schedule with him?"
- Shows initiative by already knowing the referral

**Success Criteria:**
✓ Proactively identifies referrals
✓ Suggests appropriate provider
✓ Streamlines conversation

### Scenario 5.2: Specialty Referral Without Specific Provider
**User:** "John needs a Primary Care appointment"

**Expected Agent Behavior:**
- Sees referral for "Primary Care" specialty (no specific provider)
- Calls `list_providers` with specialty="Primary Care"
- Lists options: Dr. Grey and Chris Perry
- Notes John's PCP is Dr. Grey
- Suggests: "John's PCP is Dr. Grey. Would you like to book with her?"

**Success Criteria:**
✓ Handles specialty-only referrals
✓ Uses PCP information intelligently
✓ Provides multiple options

### Scenario 5.3: No Referral for Specialist
**User:** "Book John with Dr. Yang for surgery"

**Expected Agent Behavior:**
- Checks patient referrals
- No surgery referral found
- Warns: "I notice John doesn't have a referral for Dr. Yang's surgery specialty. The patient can:
  a) Book with their PCP (Dr. Grey) first to get a referral
  b) Proceed without a referral (insurance may not cover it)
  c) Use self-pay (no referral needed - $1,000)
  Which option would you prefer?"

**Success Criteria:**
✓ Identifies missing referral
✓ Provides clear options
✓ Includes self-pay information

---

## 6. EDGE CASES & ERROR HANDLING

### Scenario 6.1: Patient Not Found
**User:** "Find patient Jane Smith, DOB 05/15/1990"

**Expected Agent Behavior:**
- Calls `search_patient`
- Returns patient not found
- Suggests: "I'm not finding that patient in our system. Could you double-check the spelling or verify they're registered?"
- Doesn't proceed without valid patient

**Success Criteria:**
✓ Graceful error handling
✓ Helpful suggestion
✓ Doesn't make up data

### Scenario 6.2: No Available Slots
**User:** "Book John with Dr. Brennan next week"

**Expected Agent Behavior:**
- Calls `list_available_slots` for next week
- If no slots: "I don't see any openings for Dr. Brennan next week. Let me check the following week..."
- Proactively calls tool again with later dates
- Presents alternatives

**Success Criteria:**
✓ Handles no availability gracefully
✓ Proactively suggests alternatives
✓ Doesn't give up immediately

### Scenario 6.3: Ambiguous Provider Request
**User:** "Book with House"

**Expected Agent Behavior:**
- Clarifies: "I found Dr. Gregory House. He has two locations:
  - PPTH Orthopedics (Mon-Wed)
  - Jefferson Hospital (Thu-Fri)
  Which location works best?"

**Success Criteria:**
✓ Handles multiple departments
✓ Asks for clarification
✓ Provides context to help decision

### Scenario 6.4: Conflicting Information
**User:** "Book a 15-minute appointment with Dr. Yang for John"

**Expected Agent Behavior:**
- Checks appointment history
- Determines this should be NEW (30 minutes)
- Politely corrects: "Actually, since John hasn't seen Dr. Yang before, this needs to be a NEW patient appointment, which is 30 minutes. Shall I find 30-minute slots?"

**Success Criteria:**
✓ Validates user input against business rules
✓ Corrects politely
✓ Explains reasoning

---

## 7. CONVERSATIONAL FLOW & PROACTIVITY

### Scenario 7.1: Efficient Multi-Step Booking
**User:** "Schedule John Doe for orthopedics with Dr. House next Monday using Blue Cross"

**Expected Agent Behavior:**
- Recognizes all information provided
- Calls tools in parallel/sequence:
  1. `search_patient` for John Doe
  2. `check_insurance` for Blue Cross
  3. `check_appointment_history` for Dr. House
  4. `list_available_slots` for next Monday
- Presents: "I found John Doe. Blue Cross Blue Shield is accepted. Since he saw Dr. House on 8/12/24, this will be ESTABLISHED (15 min). Here are Monday's available times: ..."

**Success Criteria:**
✓ Doesn't ask for info already provided
✓ Processes efficiently
✓ Confirms all details at once

### Scenario 7.2: Contextual Suggestions
**User:** "John needs a follow-up"

**Expected Agent Behavior:**
- Calls `search_patient`
- Reviews appointment history
- Suggests: "I see John last saw Dr. House on 8/12/24 for Orthopedics and Dr. Grey on 9/17/24 for Primary Care (no-show). Would you like to schedule a follow-up with either of them?"

**Success Criteria:**
✓ Uses historical context
✓ Makes intelligent suggestions
✓ Saves nurse time

### Scenario 7.3: Mid-Conversation Question
**User (during booking flow):** "Wait, how much is self-pay for orthopedics?"

**Expected Agent Behavior:**
- Calls `get_self_pay_rate` immediately
- Answers: "$300 for Orthopedics"
- Smoothly returns to booking: "Would you like to continue with insurance or switch to self-pay?"

**Success Criteria:**
✓ Handles interruptions gracefully
✓ Answers questions immediately
✓ Returns to main flow

---

## 8. COMPLEX SCENARIOS

### Scenario 8.1: Multiple Appointments
**User:** "John needs to see both Dr. House for orthopedics and Dr. Grey for a checkup"

**Expected Agent Behavior:**
- Handles sequentially
- Books first appointment completely
- Then: "Great! John is scheduled with Dr. House. Now, let's book with Dr. Grey..."
- Tracks both bookings separately
- Provides both confirmation numbers

**Success Criteria:**
✓ Handles multiple bookings
✓ Keeps them organized
✓ Provides separate confirmations

### Scenario 8.2: Changing Details Mid-Booking
**User:** "Actually, can we do Thursday instead of Monday?"

**Expected Agent Behavior:**
- Acknowledges change
- Calls `list_available_slots` with new date
- Presents new options
- Doesn't lose other confirmed details

**Success Criteria:**
✓ Flexible to changes
✓ Maintains context
✓ Re-validates availability

### Scenario 8.3: Provider Comparison Request
**User:** "Compare Dr. House and Dr. Brennan for me"

**Expected Agent Behavior:**
- Calls `list_providers` for both
- Presents side-by-side:
  - Dr. House: PPTH (M-W 9-5) & Jefferson (Th-F 9-5), John has referral, saw him 8/12/24
  - Dr. Brennan: Jefferson (Tu-Th 10-4), no referral needed for same location
- Helps nurse make informed decision

**Success Criteria:**
✓ Provides comparison
✓ Includes relevant patient context
✓ Helps decision-making

---

## 9. SYSTEM INFORMATION QUERIES

### Scenario 9.1: General Insurance Question
**User:** "What insurances do you accept?"

**Expected Agent Behavior:**
- Calls `check_insurance` tool (or has cached list)
- Lists all: Medicaid, United Health Care, Blue Cross Blue Shield of North Carolina, Aetna, Cigna
- Offers: "Which one does the patient have?"

**Success Criteria:**
✓ Provides complete list
✓ Clear presentation

### Scenario 9.2: All Self-Pay Rates
**User:** "What are your self-pay rates?"

**Expected Agent Behavior:**
- Calls `get_self_pay_rate` or lists all
- Presents:
  - Primary Care: $150
  - Orthopedics: $300
  - Surgery: $1,000

**Success Criteria:**
✓ Complete pricing information
✓ Well-formatted

### Scenario 9.3: Provider Specialties
**User:** "What specialties are available?"

**Expected Agent Behavior:**
- Calls `list_providers` or aggregates
- Lists: Primary Care, Orthopedics, Surgery
- Asks: "Which specialty does the patient need?"

**Success Criteria:**
✓ Accurate specialty list
✓ Helpful follow-up

---

## 10. STRESS TESTS & BOUNDARIES

### Scenario 10.1: Rapid-Fire Questions
**User:** "Does John have insurance? What's his DOB? When did he last see Dr. House?"

**Expected Agent Behavior:**
- Handles all questions
- Explains: Patient records don't contain insurance (must ask nurse)
- Provides DOB from patient record
- States last appointment date
- Remains organized

**Success Criteria:**
✓ Handles multiple questions
✓ Accurate responses
✓ Doesn't get confused

### Scenario 10.2: Vague Request
**User:** "Help"

**Expected Agent Behavior:**
- Asks clarifying question: "I'd be happy to help! Are you looking to:
  - Book a new appointment
  - Check provider availability
  - Verify insurance coverage
  - Get patient information"

**Success Criteria:**
✓ Handles vague input
✓ Provides clear options
✓ Guides conversation

### Scenario 10.3: Out of Scope Question
**User:** "What's the weather today?"

**Expected Agent Behavior:**
- Politely redirects: "I'm specifically designed to help with appointment scheduling and care coordination. I can help you book appointments, check provider availability, or verify insurance. What would you like to do?"

**Success Criteria:**
✓ Stays on task
✓ Polite redirection
✓ Offers relevant help

---

## DEMO PRESENTATION SCRIPT (20 Minutes)

### Introduction (2 min)
"Today I'm demonstrating a Care Coordinator Assistant that helps nurses efficiently schedule appointments using AI and the ReAct pattern."

### Part 1: Basic Booking (5 min)
- Show complete flow: patient search → provider selection → insurance check → slot selection → confirmation
- Highlight: "Notice how it gathers information progressively and uses tools proactively"

### Part 2: Intelligence Features (5 min)
- Show referral awareness
- Show NEW vs ESTABLISHED determination
- Show insurance verification with self-pay fallback
- Highlight: "It uses patient history to make smart suggestions"

### Part 3: Edge Cases (4 min)
- Show rejected insurance handling
- Show provider unavailability with alternatives
- Show missing referral warning
- Highlight: "It gracefully handles real-world scenarios"

### Part 4: Technical Architecture (3 min)
- Show ReAct loop in action (tool calls in browser network tab)
- Explain: Frontend manages state, backend is stateless
- Show: Database stores all bookings

### Conclusion (1 min)
- Recap: Modern AI approach, production-ready patterns, handles edge cases
- Answer questions

---

## SUCCESS METRICS

After testing all scenarios, the system should demonstrate:

✓ **100% Coverage** of required features from assignment
✓ **Proactive behavior** - anticipates needs, doesn't just react
✓ **Error resilience** - handles edge cases gracefully
✓ **Conversational flow** - natural, not robotic
✓ **Business rule compliance** - NEW/ESTABLISHED, hours, referrals
✓ **Data accuracy** - never makes up information
✓ **Tool efficiency** - uses tools appropriately, no redundant calls
✓ **User experience** - clear confirmations, helpful suggestions

---

## NOTES FOR INTERVIEWER

**Key Differentiators to Highlight:**
1. ReAct pattern (not hardcoded rules)
2. Stateless backend (scalable architecture)
3. Proactive tool usage (smart suggestions)
4. Patient context awareness (referrals, history)
5. Graceful error handling
6. Production-ready database design

**Be Ready to Explain:**
- Why ReAct over rule-based approach
- How tool schemas guide LLM behavior
- Trade-offs in architecture decisions
- How you'd scale this to production