"""
Cognitive Reframing & Uplifting Message Engine (cognitive_reframer.py)
Generates context-aware, empathetic psychological reframings, uplifting affirmations,
and Gita-aligned cognitive shifts tailored to the user's specific life domain and mood.
Supports 30 discrete emotional moods and 15 distinct contextual life domains.
"""

import re
from textblob import TextBlob

# 15 Context-specific psychological reframings mapped by life driver
CONTEXT_REFRAMINGS = {
    "Academic Stress": {
        "lens": "Detachment from Outcome & Process-Oriented Mastery (Nishkama Karma)",
        "reframing": (
            "Exams and academic benchmarks assess your current preparation, not your human worth or future potential. "
            "In Chapter 2, Verse 47, Krishna counsels Arjuna: 'Your right is to the work itself, never to its fruits.' "
            "When you release obsessive worry about the grade and pour your calm attention into the next single concept, "
            "your nervous system shifts from fight-or-flight into optimal cognitive focus."
        ),
        "affirmation": "I am capable of learning one concept at a time. My value is unconditional.",
        "micro_action": "Complete a 25-minute Pomodoro block on one topic, then take 5 deep belly breaths."
    },
    "Career / Work": {
        "lens": "Sthitaprajna — Inner Stability Amid Workplace Turbulence",
        "reframing": (
            "Professional pressure and workplace chaos test our internal equanimity. "
            "Chapter 2, Verse 38 teaches us to treat triumph and setback with equal calm. "
            "Workplace demands are external circumstances; your peace of mind is an internal sanctuary that no meeting, "
            "boss, or deadline has the authority to disturb unless you surrender it."
        ),
        "affirmation": "I work with diligence and excellence while remaining anchored in my inner peace.",
        "micro_action": "Step away from your workstation for 3 minutes, un-clench your shoulders, and drink a glass of water."
    },
    "Relationships": {
        "lens": "Atmavat Sarvabhuteshu — Compassionate Boundaries & Universal Vision",
        "reframing": (
            "Interpersonal conflict often arises when we expect others to fulfill what only inner peace can provide. "
            "Chapter 6, Verse 32 guides us to view others through the lens of our own self. "
            "Recognize that people often react out of their own unhealed distress. "
            "Establish gentle, clear boundaries while protecting your heart from lingering bitterness."
        ),
        "affirmation": "I choose compassion for others while honoring my sacred emotional boundaries.",
        "micro_action": "Write down one boundary you need to protect today, without needing to justify or apologize for it."
    },
    "Health & Body": {
        "lens": "Yukta-Ahara-Vihara — Sacred Bodily Stewardship",
        "reframing": (
            "Your physical body is the sacred instrument of consciousness. "
            "Chapter 6, Verse 17 highlights that balanced eating, restorative sleep, and regulated movement destroy all sorrow. "
            "Treat physical discomfort not as an adversary to fight, but as communication asking for gentleness, hydration, and rest."
        ),
        "affirmation": "I honor my body's need for rest, healing, and patient nourishment.",
        "micro_action": "Lie down flat for 5 minutes with a warm compress or do gentle neck and shoulder rotations."
    },
    "Financial Pressure": {
        "lens": "Present-Moment Agency over Future Scarcity Anxiety",
        "reframing": (
            "Financial stress is largely anxiety projecting into an uncertain future. "
            "The Gita teaches us that rumination cannot generate abundance; only clear, deliberate action in the present moment can. "
            "Focus today solely on what is within your direct agency: one expense reviewed, one skill built, one small step taken."
        ),
        "affirmation": "I face financial realities with clarity and patience, taking one deliberate step each day.",
        "micro_action": "List the single most important practical financial action you can complete today."
    },
    "Self-Esteem": {
        "lens": "Uddharet Atmana Atmanam — Self-Elevation as Your Own Ally",
        "reframing": (
            "The harshest critic you will ever encounter is usually your own runaway mind. "
            "Chapter 6, Verse 5 gives this timeless injunction: 'Elevate yourself by your own mind; do not degrade yourself. "
            "For the mind alone is your greatest friend, or your fiercest enemy.' "
            "Decide today to become the ally of your own consciousness. Treat your perceived flaws with patient kindness."
        ),
        "affirmation": "I am enough as I am in this moment. I choose to be my own kindest friend.",
        "micro_action": "Speak aloud three genuine qualities or small acts of goodness you demonstrated this week."
    },
    "Loss & Grief": {
        "lens": "Shashwata — The Eternal Essence Beyond Form",
        "reframing": (
            "Grief is profound because love is profound. It is completely natural to weep and ache. "
            "Chapter 2, Verse 20 reminds us that the fundamental spirit is never born and never dies—it is timeless, indestructible, and sacred. "
            "Hold your grief with gentle hands; your connection with what was loved is woven permanently into who you are."
        ),
        "affirmation": "I give myself permission to grieve. The love I hold is eternal and transcends absence.",
        "micro_action": "Place your hand over your heart, close your eyes, and take three slow, grounding breaths."
    },
    "Social Anxiety & Loneliness": {
        "lens": "Sarva-Bhuta-Stitam — Divine Belonging in All Creation",
        "reframing": (
            "Feeling isolated or self-conscious in social settings arises from the illusion that everyone else has it figured out while you stand apart. "
            "In Chapter 6, Verse 29, Krishna reveals that the enlightened soul sees the self in all beings and all beings in the self. "
            "You do not need to perform or wear a mask to earn belonging; your honest, quiet presence is valuable as it is."
        ),
        "affirmation": "I belong in this world. My quiet presence is genuine, safe, and worthy.",
        "micro_action": "Reach out to one person with a simple 'Thinking of you' note, or take a gentle walk among people without needing to interact."
    },
    "Family & Home Dynamics": {
        "lens": "Titiksha — Forbearance with Loving Disentanglement",
        "reframing": (
            "Family environments often trigger our deepest wounds because the emotional stakes feel so high. "
            "The Gita counsels *Titiksha*—patient endurance without absorbing the bitterness of external friction. "
            "You can love your family deeply while declining to accept their anxiety, comparisons, or projections as your truth."
        ),
        "affirmation": "I cultivate peace within my own center, regardless of the chaos in my surroundings.",
        "micro_action": "Step outside for 4 minutes of fresh air before replying to any charged family discussion."
    },
    "Burnout & Overwork": {
        "lens": "Yukta-Chesta — Harmonious Action & Restorative Sacred Rest",
        "reframing": (
            "Burnout is not a personal failure; it is your soul and nervous system sounding the alarm on an unsustainable pace. "
            "Chapter 6, Verse 16 warns that yoga cannot be achieved by one who overworks without pause. "
            "Rest is not an indulgence or prize you must earn through exhaustion—it is a vital, sacred duty (*Dharma*) to renew your spirit."
        ),
        "affirmation": "Rest is productive. Recharging my spirit is essential to my life's journey.",
        "micro_action": "Block out 30 minutes tonight with zero screens, sipping warm tea and listening to calming sounds."
    },
    "Identity & Life Purpose": {
        "lens": "Swadharma — Walking Your Unique Authentic Truth",
        "reframing": (
            "Feeling lost or questioning your direction is the doorway to authentic self-discovery. "
            "In Chapter 3, Verse 35, Krishna declares: 'Better is one’s own duty, though devoid of merit, than another's duty well-performed.' "
            "Stop measuring your timeline against social benchmarks. Trust your inner compass and cultivate what is uniquely yours."
        ),
        "affirmation": "My journey has its own divine timing. I step forward into my own authenticity.",
        "micro_action": "Write down two values that genuinely excite you, independent of money or outside approval."
    },
    "Romantic Heartbreak & Dating": {
        "lens": "Atma-Rati — The Unshakable Sanctuary of Self-Wholeness",
        "reframing": (
            "Heartbreak feels shattering because love expands our boundaries. But remember: the love you felt was generated from inside your own heart. "
            "Chapter 2, Verse 14 reminds us that outer attachments come and go like seasons. "
            "Grieve what was lost, but recognize that your wholeness, dignity, and capacity for joy remain fully intact."
        ),
        "affirmation": "I am whole within myself. My heart is resilient and open to gentle healing.",
        "micro_action": "Write a short letter of gratitude to your own heart for having the courage to love and be vulnerable."
    },
    "Sleep & Physical Fatigue": {
        "lens": "Nidra & Shanti — Surrendering the Burdens of the Day",
        "reframing": (
            "When the physical body is exhausted, mental thoughts inevitably become distorted and anxious. "
            "Do not try to solve your life's problems when you are tired. Surrender the worries of today to the night. "
            "Tomorrow will arrive with fresh light, restored perspective, and renewed strength."
        ),
        "affirmation": "I give myself permission to sleep peacefully. Tomorrow holds new beginnings.",
        "micro_action": "Do 3 rounds of the 4-7-8 breathing exercise, loosen your jaw, and let your mattress support you completely."
    },
    "Habits & Mind Wandering": {
        "lens": "Abhyasa & Vairagya — The Gentle Art of Constant Return",
        "reframing": (
            "A distracted or wandering mind is completely natural. Arjuna himself complained that the mind is as hard to tame as the wind. "
            "Krishna’s response in Chapter 6, Verse 35 is pure compassion: through *Abhyasa* (patient practice) and *Vairagya* (non-judgmental release), "
            "the mind settles. Do not berate yourself when your attention slips—simply smile and bring it back."
        ),
        "affirmation": "I gently guide my mind back with patience. Each return strengthens my presence.",
        "micro_action": "Focus on 5 consecutive mindful breaths right now, counting 'one' on inhale, 'two' on exhale."
    },
    "General Wellbeing": {
        "lens": "Samata — Equanimity & Quiet Strength",
        "reframing": (
            "True wellness is not the permanent absence of turbulence, but the cultivation of steady presence within it. "
            "As Chapter 2, Verse 48 reminds us: 'Yoga is equanimity of mind.' "
            "Anchor yourself in this single present breath; this moment is whole, safe, and complete."
        ),
        "affirmation": "I am rooted in quiet strength. I move through my day with grace and balance.",
        "micro_action": "Take 60 seconds to notice 3 things you are sincerely grateful for right now."
    }
}

# Empathetic intros for all 30 discrete moods
MOOD_EMPATHY = {
    "anxious": "I sense that a wave of anxiety or restlessness is moving through you right now. Take a soft, gentle breath—you are safe in this moment.",
    "overwhelmed": "You are carrying a heavy load right now, and it is completely understandable that you feel overwhelmed. Let us set down the future and look only at this minute.",
    "sad": "I hear the sadness in your words. Please know that it is entirely okay to feel this way; your feelings deserve tenderness and space.",
    "very_sad": "You are navigating deep sorrow. Please remember that you do not have to carry this grief alone, and this storm will not last forever.",
    "angry": "I hear how frustrating and unfair this situation feels. Anger is energy asking for boundaries; let us pause before reacting so your clarity stays intact.",
    "discouraged": "Feeling discouraged is a sign that you care deeply about your path. Take heart—small progress is still genuine progress.",
    "pessimistic": "When the mind feels dark, it projects shadows onto tomorrow. Let us ground ourselves in what is true right now.",
    "devastated": "My heart goes out to you in this painful moment. Breathe with me; you are held, you are safe, and your life is deeply precious.",
    "happy": "It is wonderful to witness your happiness and gratitude! Savor this radiant energy and let it nourish your spirit.",
    "very_happy": "What a joyful and uplifted state! Hold onto this feeling of fulfillment as a sanctuary for your journey.",
    "content": "A peaceful and contented state of mind is sacred. Celebrate this quiet equilibrium.",
    "peaceful": "Serenity is the natural essence of the self when worries settle. Rest deeply in this calm.",
    "neutral": "You are in a balanced, reflective space. An ideal moment to set gentle intentions for your day.",
    "positive": "Your perspective is uplifted and radiant. May this positive momentum carry you forward gracefully.",
    "optimistic": "Optimism is courage looking toward tomorrow with hope. Nurture this bright outlook.",
    "hopeful": "Hope is the dawn rising before the sun appears. Trust in the quiet unfolding of your journey.",
    "grateful": "A grateful heart turns what we have into enough. Your appreciation is a magnet for peace.",
    "ecstatic": "What an exhilarating rush of joy and celebration! Let your heart dance in this luminous moment.",
    "restless": "Your mind or body feels unsettled, like a river seeking its channel. Let us ground that vibrant energy.",
    "negative": "It feels heavy right now, and your pain is valid. We will take this one mindful breath at a time.",
    "lonely": "I hear the solitude and ache in your words. Please know you are heard, valued, and never truly as solitary as it feels.",
    "burned_out": "You have been giving so much for so long that your reservoir is dry. Rest without guilt; healing begins with pause.",
    "guilty": "Remorse shows your conscience is alive, but punishing yourself will not heal the past. Practice self-compassion and resolve to grow.",
    "insecure": "That quiet whisper telling you that you are not enough is an illusion of fear. You possess intrinsic, unassailable worth.",
    "confused": "Confusion is simply the space between old understanding and new clarity. Be patient with the fog; it will clear.",
    "envious": "Comparing our internal struggle to another's highlight reel hurts. Redirect that energy toward tending your own garden.",
    "grief_stricken": "Loss leaves an aching hollow in the chest. Honor your tears as love that has no place to go. You are deeply held.",
    "serene": "You are resting in pure, tranquil clarity. This serenity is your true, unblemished nature.",
    "inspired": "The spark of inspiration is alive within you! Channel this sacred vitality into purposeful action.",
    "resilient": "Look at everything you have survived to be here today. Your resilience is rooted in quiet, unshakable strength."
}


def analyze_text_affect(text: str) -> dict:
    """
    Enhanced linguistic affect and compound negation analyzer.
    Extracts raw polarity & subjectivity with custom negation inversion rules.
    """
    if not text:
        return {"polarity": 0.0, "subjectivity": 0.0, "intensity": 0.0, "negation_detected": False}

    lowered = text.lower()
    blob = TextBlob(text)
    base_polarity = float(blob.sentiment.polarity)
    base_subjectivity = float(blob.sentiment.subjectivity)
    negation_detected = False

    # Positive compound negation mappings
    positive_negations = [
        ("not bad", 0.35),
        ("not terrible", 0.4),
        ("not half bad", 0.45),
        ("not poor", 0.3),
        ("can't complain", 0.4),
        ("cannot complain", 0.4),
        ("never felt better", 0.85),
        ("couldn't be happier", 0.9),
        ("no worries", 0.35),
        ("not worried", 0.4),
        ("not too bad", 0.35)
    ]
    for pattern, val in positive_negations:
        if pattern in lowered:
            base_polarity = max(base_polarity, val)
            negation_detected = True

    # Negative compound negation mappings
    negative_negations = [
        ("not good", -0.4),
        ("not happy", -0.45),
        ("not okay", -0.5),
        ("not fine", -0.45),
        ("not feeling well", -0.4),
        ("not great", -0.35),
        ("hardly positive", -0.3),
        ("barely coping", -0.65),
        ("can't cope", -0.7),
        ("cannot cope", -0.7),
        ("can't take this", -0.75),
        ("not worth", -0.6),
        ("no hope", -0.75)
    ]
    for pattern, val in negative_negations:
        if pattern in lowered:
            base_polarity = min(base_polarity, val)
            negation_detected = True

    # Emotional intensity calculation
    exclamations = text.count("!")
    caps_ratio = sum(1 for c in text if c.isupper()) / max(len(text), 1)
    intensity = min(1.0, abs(base_polarity) + (exclamations * 0.1) + (caps_ratio * 0.3))

    return {
        "polarity": round(base_polarity, 3),
        "subjectivity": round(base_subjectivity, 3),
        "intensity": round(intensity, 3),
        "negation_detected": negation_detected
    }


def classify_context_enhanced(text: str) -> str:
    """
    Enhanced context classifier with scoring heuristics across 15 life domains.
    """
    if not text:
        return "General Wellbeing"
    
    text_lower = text.lower()
    
    # Context taxonomy keyword dictionary
    context_mapping = {
        "Academic Stress": ["exam", "assignment", "college", "university", "semester", "grades", "deadline", "study", "class", "tuition", "professor", "quiz", "homework"],
        "Career / Work": ["job", "work", "office", "boss", "career", "promotion", "interview", "salary", "client", "meeting", "manager", "project", "workplace", "overtime"],
        "Relationships": ["relationship", "partner", "girlfriend", "boyfriend", "friend", "marriage", "dating", "argument", "fight", "communication"],
        "Health & Body": ["health", "pain", "illness", "doctor", "headache", "diet", "exercise", "body", "physical", "stomach", "fever", "cramp", "symptom"],
        "Financial Pressure": ["money", "debt", "loan", "rent", "bills", "savings", "budget", "finance", "expensive", "afford", "salary", "cost", "broke"],
        "Self-Esteem": ["confidence", "self-worth", "esteem", "worthless", "compare", "body image", "appearance", "ugly", "imposter", "incompetent", "inadequate"],
        "Loss & Grief": ["grief", "bereavement", "death", "died", "passed away", "lost someone", "funeral", "mourning", "miss them deeply"],
        "Social Anxiety & Loneliness": ["lonely", "alone", "isolated", "social anxiety", "party", "awkward", "left out", "no friends", "making friends", "crowd", "shyness"],
        "Family & Home Dynamics": ["parent", "mother", "father", "dad", "mom", "sister", "brother", "sibling", "household", "home", "relative", "family"],
        "Burnout & Overwork": ["burnout", "burned out", "exhaustion", "no energy", "non-stop", "drained", "can't go on working", "swamped", "overworked"],
        "Identity & Life Purpose": ["purpose", "meaning of life", "direction", "calling", "passion", "future path", "existential", "what am i doing", "lost my way"],
        "Romantic Heartbreak & Dating": ["breakup", "broken heart", "heartbroken", "ex-boyfriend", "ex-girlfriend", "rejection", "divorce", "ghosted", "unrequited"],
        "Sleep & Physical Fatigue": ["insomnia", "can't sleep", "sleep deprivation", "tired", "exhausted", "nightmare", "waking up", "fatigue", "restless sleep"],
        "Habits & Mind Wandering": ["distracted", "procrastination", "bad habit", "phone addiction", "scroll", "attention", "can't focus", "mind wandering"],
        "General Wellbeing": ["stress", "anxious", "sad", "happy", "peace", "feeling", "today", "mindful", "thought"]
    }

    scores = {}
    for label, keywords in context_mapping.items():
        score = 0
        for kw in keywords:
            if re.search(r'\b' + re.escape(kw) + r'\b', text_lower):
                score += 2 if len(kw.split()) > 1 else 1
        if score > 0:
            scores[label] = score

    if scores:
        # Return context with highest keyword density score
        return max(scores.items(), key=lambda x: x[1])[0]

    return "General Wellbeing"


def extract_nuanced_mood(text: str, base_mood: str = "neutral") -> str:
    """
    Extracts high-granularity emotional mood from user text across 30 taxonomy states.
    """
    if not text:
        return base_mood

    text_lower = text.lower()

    # Specific nuanced keywords taking priority over generic mood
    nuanced_indicators = {
        "lonely": ["lonely", "all alone", "isolated", "alienated", "abandoned", "friendless", "nobody cares", "lonesome"],
        "burned_out": ["burned out", "burnout", "exhausted", "drained", "overworked", "depleted", "fatigued to the bone"],
        "guilty": ["guilty", "regretful", "remorseful", "ashamed", "my fault", "self-reproach", "feel awful for what i did"],
        "insecure": ["insecure", "inadequate", "self-conscious", "unconfident", "imposter", "inferior", "not good enough"],
        "confused": ["confused", "lost", "uncertain", "perplexed", "indecisive", "disoriented", "don't know what to do"],
        "envious": ["envious", "jealous", "covetous", "resentful of", "comparing myself", "bitter towards"],
        "grief_stricken": ["grief", "heartbroken", "bereaved", "mourning", "loss of my", "passed away", "miss them so much"],
        "serene": ["serene", "tranquil", "peaceful stillness", "deep calm", "unruffled", "at centered peace"],
        "inspired": ["inspired", "invigorated", "motivated to create", "electrified", "stimulated", "empowered"],
        "resilient": ["resilient", "standing strong", "persevering", "undeterred", "holding my ground", "unyielding"],
        "ecstatic": ["ecstatic", "euphoric", "overjoyed", "thrilled beyond belief", "on cloud nine", "blissful"],
        "devastated": ["devastated", "shattered", "crushed into pieces", "heartbroken", "distraught"],
        "overwhelmed": ["overwhelmed", "can't handle", "drowning in work", "swamped", "too much to bear"],
        "anxious": ["anxious", "panic", "worried sick", "terrified", "nervous wreck", "on edge"],
        "angry": ["furious", "enraged", "pissed off", "infuriated", "livid", "seething with rage"],
        "grateful": ["so grateful", "deeply thankful", "blessed beyond words", "full of gratitude"]
    }

    for mood_candidate, phrases in nuanced_indicators.items():
        if any(p in text_lower for p in phrases):
            return mood_candidate

    return base_mood if base_mood != "neutral" else "neutral"


def generate_therapeutic_response(thought: str, mood: str, context: str, polarity: float) -> dict:
    """
    Synthesizes an empathetic, context-aware therapeutic response
    combining mood validation, cognitive reframing, and uplifting affirmations.
    """
    # 1. Retrieve empathetic validation
    empathy_intro = MOOD_EMPATHY.get(
        mood.lower(),
        "Thank you for sharing your authentic reflection. Every thought you honor brings you closer to self-awareness."
    )

    # 2. Retrieve context reframing details
    reframing_data = CONTEXT_REFRAMINGS.get(context, CONTEXT_REFRAMINGS["General Wellbeing"])

    # 3. Formulate the comprehensive conversational reply
    conversational_reply = (
        f"{empathy_intro}\n\n"
        f"**Psychological Perspective ({context}):**\n"
        f"{reframing_data['reframing']}\n\n"
        f"💡 **Mindful Affirmation:** \"{reframing_data['affirmation']}\"\n\n"
        f"🌱 **Gentle Action:** {reframing_data['micro_action']}"
    )

    return {
        "empathy_intro": empathy_intro,
        "reframing": reframing_data["reframing"],
        "affirmation": reframing_data["affirmation"],
        "micro_action": reframing_data["micro_action"],
        "philosophical_lens": reframing_data["lens"],
        "full_reply": conversational_reply
    }
