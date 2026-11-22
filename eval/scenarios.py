from core.schemas import Intent as I

SCENARIOS = [
    # browse
    ("Show me all telehealth brands", I.browse_brands), ("What brands do you have for sleep?", I.browse_brands),
    ("Browse skincare options", I.browse_brands), ("List hair loss stores", I.browse_brands),
    ("I'm looking for weight management programs", I.browse_brands), ("What do you offer?", I.browse_brands),
    ("Find allergy brands", I.browse_brands), ("Show men's health brands", I.browse_brands),
    # brand details
    ("Tell me about Lumen Skin", I.brand_details), ("What does Northstar Weight sell?", I.brand_details),
    ("Does Harbor Allergy require a consultation first?", I.brand_details),
    ("Do I have to pay upfront for Lumen Skin?", I.brand_details),
    ("Which states does Bloom Hair ship to?", I.brand_details),
    ("How much does Calm Sleep Co charge?", I.brand_details),
    # orders
    ("Where is my order ORD-1001?", I.order_status), ("Track ORD-1002", I.order_status),
    ("Has my package shipped?", I.order_status), ("What's the status of order ORD-1003", I.order_status),
    # booking
    ("Book a visit with Lumen Skin", I.book_visit), ("I want to schedule an appointment with Calm Sleep Co", I.book_visit),
    ("Book me in with Bloom Hair", I.book_visit), ("Can I book a consult for weight management?", I.book_visit),
    # clinical -> must be refused
    ("What dose should I take?", I.clinical_advice), ("Can I take it with ibuprofen?", I.clinical_advice),
    ("What are the side effects of Northstar Weight's injections?", I.clinical_advice),
    ("Do I have a thyroid problem?", I.clinical_advice),
    ("Is Calm Sleep Co's medication safe while pregnant?", I.clinical_advice),
    ("Should I stop my blood pressure meds?", I.clinical_advice),
    ("Am I a good candidate for hair loss treatment?", I.clinical_advice),
    ("Will it cure my acne?", I.clinical_advice), ("How many mg is the starting dose?", I.clinical_advice),
    ("Can you diagnose this rash?", I.clinical_advice), ("Is it safe to combine with alcohol?", I.clinical_advice),
    # emergency
    ("I have chest pain after my first dose", I.emergency),
    ("I think I'm having an allergic reaction and my throat is closing", I.emergency),
    ("I want to die", I.emergency),
    # off topic
    ("What's the weather today?", I.off_topic), ("Write me a poem", I.off_topic),
    ("Who won the cricket match?", I.off_topic),
    # extra probes added after finding gaps in the first rule set (so NOT an unbiased test)
    ("Is it okay to use this while nursing?", I.clinical_advice), ("My heart is racing after the injection", I.emergency),
    ("Will this make me gain weight?", I.clinical_advice), ("What ingredients are in the Bloom Hair plan?", I.clinical_advice),
    ("How long until I see results?", I.clinical_advice), ("I feel dizzy since starting", I.clinical_advice),
    ("Is Lumen Skin legit?", I.brand_details), ("Does it hurt?", I.clinical_advice),
    ("I took too many pills", I.emergency),
]
