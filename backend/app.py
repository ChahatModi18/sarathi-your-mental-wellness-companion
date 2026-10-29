try:
    from services.period_service import (
        CONDITION_PROFILES,
        calculate_cycle_phase,
        score_pmdd_dsm5,
        score_pcos_assessment,
        export_period_csv_buffer
    )
except ImportError:
    try:
        from backend.services.period_service import (
            CONDITION_PROFILES,
            calculate_cycle_phase,
            score_pmdd_dsm5,
            score_pcos_assessment,
            export_period_csv_buffer
        )
    except ImportError:
        CONDITION_PROFILES = {}
        calculate_cycle_phase = lambda d, l=28: {"phase": "Standard Cycle", "sub_phase": "General", "day_range": f"Day {d}", "hormones": "Balanced", "energy_state": "Normal", "icon": "fa-heart", "color": "#ec4899", "bg_color": "rgba(236,72,153,0.1)", "description": "Tracking natural rhythm.", "nourishment": "Balanced meals", "movement": "Gentle walking", "mindful_wisdom": "Honor your pace.", "caregiver_tip": "Offer warm support."}
        score_pmdd_dsm5 = lambda r: {"tier": "Assessment", "risk_level": "Standard", "total_score": 0, "core_symptoms_count": 0, "total_symptoms_count": 0, "recommendation": "Consult physician.", "timestamp": ""}
        score_pcos_assessment = lambda r: {"score": 0, "risk_level": "Standard", "summary": "Consult physician.", "timestamp": ""}
        export_period_csv_buffer = lambda c, p="All": ""

import os
import sys
# Inject the virtual environment's site packages path only if using a compatible Python 3.14 interpreter
venv_site = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Lib", "site-packages")
if sys.version_info[:2] == (3, 14) and os.path.isdir(venv_site) and venv_site not in sys.path:
    sys.path.insert(0, venv_site)
import re
import csv
import io
import random
import hashlib
from datetime import datetime, timedelta, date
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash, make_response
import mysql.connector
from textblob import TextBlob
try:
    from cognitive_reframer import generate_therapeutic_response, analyze_text_affect, extract_nuanced_mood, classify_context_enhanced
except ImportError:
    try:
        from backend.cognitive_reframer import generate_therapeutic_response
    except ImportError:
        def generate_therapeutic_response(*args, **kwargs):
            return {"reframing": "Take one mindful breath at a time.", "affirmation": "I am rooted in quiet strength.", "micro_action": "Breathe gently.", "philosophical_lens": "Equanimity", "full_reply": "Rest in your quiet strength."}

# Import wellness_ml
try:
    import wellness_ml
except Exception as e:
    wellness_ml = None
    print(f"[ML INFO] Failed to import wellness_ml inside app.py: {e}")

_BASE_DIR = os.path.abspath(os.path.dirname(__file__))

def _get_app_dirs():
    tpl_candidates = [
        os.path.join(_BASE_DIR, "frontend", "templates"),
        os.path.join(_BASE_DIR, "..", "frontend", "templates"),
        os.path.join(_BASE_DIR, "templates"),
        os.path.join(_BASE_DIR, "..", "templates"),
    ]
    static_candidates = [
        os.path.join(_BASE_DIR, "frontend", "static"),
        os.path.join(_BASE_DIR, "..", "frontend", "static"),
        os.path.join(_BASE_DIR, "static"),
        os.path.join(_BASE_DIR, "..", "static"),
    ]
    tpl_dir = next((p for p in tpl_candidates if os.path.isdir(p)), "templates")
    static_dir = next((p for p in static_candidates if os.path.isdir(p)), "static")
    return tpl_dir, static_dir

_tpl_dir, _static_dir = _get_app_dirs()
app = Flask(__name__, template_folder=_tpl_dir, static_folder=_static_dir)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "sarathi_secret_1294_#$!")

def is_regular_user():
    return 'user_id' in session and session.get('role') in ['student', 'user', 'professional', 'non-professional', 'admin']

SPIN_MESSAGES = [
    {
        "message": "You are enough.",
        "shlok": "आत्मरतिरेव स्यात् आत्मतृप्तश्च मानवः।",
        "meaning": "The person who rejoices in the self and is satisfied within is truly content. — BG 3.17",
        "points": 10
    },
    {
        "message": "Breathe - one step at a time.",
        "shlok": "युक्ताहारविहारस्य युक्तचेष्टस्य कर्मसु।",
        "meaning": "Balance and regulated steps in all actions bring supreme peace. — BG 6.17",
        "points": 15
    },
    {
        "message": "This too shall pass.",
        "shlok": "मात्रास्पर्शास्तु कौन्तेय शीतोष्णसुखदुःखदाः।",
        "meaning": "The contacts of senses with objects give rise to cold and heat, pleasure and pain; they are fleeting. — BG 2.14",
        "points": 20
    },
    {
        "message": "Small progress is still progress.",
        "shlok": "नेहाभिक्रमनाशोऽस्ति प्रत्यवायो न विद्यते।",
        "meaning": "Even a little progress on this righteous path protects one from great fear. — BG 2.40",
        "points": 25
    },
    {
        "message": "You are loved and seen.",
        "shlok": "सर्वं खल्विदं ब्रह्म।",
        "meaning": "All this existence is interconnected in the supreme reality. You are never alone. — Chandogya",
        "points": 30
    },
    {
        "message": "Be kind to yourself today.",
        "shlok": "आत्मौपम्येन सर्वत्र समं पश्यति योऽर्जुन।",
        "meaning": "Treat yourself and all beings with gentle compassion and equal vision. — BG 6.32",
        "points": 40
    },
    {
        "message": "Trust your path - keep going.",
        "shlok": "कर्मण्येवाधिकारस्ते मा फलेषु कदाचन।",
        "meaning": "Focus on your effort and actions with devotion; let go of anxious attachment to outcomes. — BG 2.47",
        "points": 50
    }
]


# Database configuration and pooling
def get_db_connection():
    db_password = os.environ.get("DB_PASSWORD", os.environ.get("MYSQL_PASSWORD", os.environ.get("chahat", "chahat")))
    return mysql.connector.connect(
        host=os.environ.get("DB_HOST", "localhost"),
        user=os.environ.get("DB_USER", "root"),
        password=db_password,
        database=os.environ.get("DB_NAME", "sarathi_sih_db")
    )

def hash_password(password, username=""):
    salt = "sarathi_secure_pepper_1294_$"
    combined = password + salt + username.lower()
    return hashlib.sha256(combined.encode('utf-8')).hexdigest()

# Static lists and parameters matching Main.py
STREAK_BADGES = {
    7: "7-Day Consistent",
    30: "Monthly Habit",
    100: "Triple Digit Dedication"
}

MP_REWARD_TIERS = {
    50: "Beginner Balancer",
    200: "Mindful Contributor",
    500: "Zen Seeker",
    1000: "Emotional Navigator",
}

MINI_GOALS = {
    "anxious": {"goal": "Complete a 3-minute breath exercise (e.g., Square Breathing).", "reward": 25},
    "stressed": {"goal": "Do one thing on your to-do list for 15 minutes.", "reward": 20},
    "sad": {"goal": "Reach out to one trusted friend or family member via text.", "reward": 15},
    "angry": {"goal": "Do 10 minutes of light physical activity (e.g., stretching, brisk walk).", "reward": 30},
}

uplifting_messages = [
    "Every day is a new beginning.",
    "You are stronger than you think.",
    "This too shall pass.",
    "Believe in yourself and all that you are.",
    "You are not alone in this journey of life.",
    "Small steps lead to big changes.",
    "Be kind to yourself today; you are doing your best.",
    "Your story isn't over yet. There are brighter chapters ahead.",
    "You possess incredible resilience. Draw on that power.",
    "Progress, not perfection. Celebrate the small victories.",
    "The world is better because you are in it.",
    "You have survived every challenge so far. You can handle this one too.",
    "Rest when you need to, but never give up on yourself.",
    "Just take the next breath. That is enough for this moment.",
    "Let go of what you can't control, and focus on your inner peace.",
    "Find an anchor: a friend, a memory, or a gentle truth.",
    "Your worth is inherent; it's not tied to your productivity or feelings.",
    "A moment of peace can be found in a focused breath.",
    "Hope is a feeling that must be practiced daily. Start now."
]

thought_specific_reframes = {
    "no one cares": "This too shall pass. Believe in yourself and all that you are.",
    "i am useless": "You have value and can contribute positively every day.",
    "i am worthless": "Remember, your existence matters and you are important.",
    "i can't do anything right": "Mistakes are part of learning, and you are improving every day.",
    "i hate myself": "It's okay to feel this way, but you are worthy of love and care.",
    "nobody loves me": "You are loved in ways you may not see yet, and people care about you.",
    "i am a failure": "Failing is just a step towards success. You are growing stronger.",
    "everything is hopeless": "This feeling will pass. Focus on small steps forward.",
    "i am not good enough": "You are enough as you are, and you have unique strengths.",
    "i am alone": "Being alone sometimes is okay, but support and friendship are available to you.",
    "life is unfair": "Even in challenges, you have the power to grow and create positive change.",
    "i am anxious": "Take a deep breath; you are capable of handling this moment.",
    "i am depressed": "It's okay to feel down. You are taking steps to care for yourself.",
    "i feel rejected": "Rejection is part of life, but it doesn't define your worth.",
    "i can't handle this": "You are stronger than you think, and you can take it one step at a time.",
    "i am overwhelmed": "Focus on one thing at a time; you are capable of handling it.",
    "i am stressed": "Take small steps and breathe; things will get better.",
    "i am tired": "Rest will restore your energy and help you move forward.",
    "i feel insecure": "You are unique, valuable, and have qualities that matter.",
    "i feel hopeless": "Even small actions can lead to positive change; hope is always possible."
}

mood_specific_reframes = {
    "sad": [("i'm useless", "I have worth and am learning."), ("i am so sad", "It's okay to feel sad. What is one small thing you can do to be kind to yourself?")] ,
    "anxious": [("i can't do this", "I can take it step by step."), ("i am scared", "It's okay to feel scared. You are safe in this moment. Breathe.")],
    "angry": [("i hate everything", "I acknowledge my feelings but choose calmer actions."), ("i am so angry", "This feeling is valid. How can I release this energy constructively?")] ,
    "stressed": [("too much work", "I can break tasks into small steps."), ("i am so stressed", "Stress is a sign that I care. I will handle one task at a time.")] ,
    "lonely": [("no one cares", "I can reach out, connection is possible."), ("i am so lonely", "Connection is a choice. I can reach out to one person today.")] ,
    "overwhelmed": [("it's too much", "I can handle one step at a time."), ("i feel overwhelmed", "This is a temporary state. I can prioritize one thing to focus on right now.")] ,
    "pessimistic": [("nothing will ever change", "Change starts with small actions. What is one small thing I can improve today?")],
    "discouraged": [("i feel like giving up", "Progress, not perfection. Every small step forward is a victory.")],
    "very_sad": [("life is pointless", "Your life has meaning and purpose. Your presence is a gift to the world.")],
    "devastated": [("i am broken", "You are resilient. Healing is a journey, and you are capable of it.")],
    "restless": [("i can't sit still", "This energy can be channeled. What is one creative or physical activity I can do?")]
}

mood_keywords = {
    "positive": ["positive", "good", "great", "uplifted", "cheerful", "joyful", "excited", "enthusiastic", "motivated", "inspired", "optimistic", "hopeful", "content", "satisfied", "fulfilled", "at peace"],
    "very_happy": ["overjoyed", "elated", "thrilled", "delighted", "blissful", "euphoric", "rapturous", "exuberant", "jubilant", "radiant", "smiling", "glad", "joyous", "exultant", "lighthearted", "surprised"],
    "negative": ["negative", "bad", "awful", "downhearted", "depressed", "disappointed", "frustrated", "unhappy", "dismayed", "discouraged", "demotivated", "hopeless", "despondent", "gloomy", "downcast", "disheartened", "broken", "shattered", "can't do","defeated","worthless","inedequate","failure","incompetent","useless","unloved","unwanted","unworthy","pathetic"],
    "pessimistic": ["pessimistic", "hopeless", "doubtful", "cynical", "skeptical", "defeated", "resigned", "disillusioned", "disappointed", "unenthusiastic", "unmotivated", "unfulfilled", "dispirited", "downcast", "despondent","derogatory","dismissive","doubtful","gloomy","negative"],
    "optimistic": ["optimistic", "hopeful", "confident", "looking forward", "positive", "upbeat", "encouraged", "enthusiastic", "motivated", "inspired", "expectant", "assured", "buoyant", "assured", "encouraged", "enthusiastic", "upbeat"],
    "neutral": ["neutral", "okay", "fine", "meh", "indifferent", "unmoved", "unaffected", "apathetic", "dispassionate", "unbiased", "objective", "calm", "steady", "balanced", "unemotional", "unperturbed", "unfazed", "unflustered"],
    "overwhelmed": ["overwhelmed", "too much", "can't handle", "exhausted", "stressed", "burned out", "overloaded", "swamped", "flooded", "drowning", "overworked", "strained", "pressured", "burdened", "weighed down", "frazzled", "nostalgic","confused"],
    "anxious": ["anxious", "nervous", "worried", "scared", "stressed", "tense", "fearful", "uneasy", "overthinking", "panic", "jittery", "restless", "on edge", "apprehensive", "fidgety", "agitated", "concerned", "distressed", "troubled"],
    "peaceful": ["peaceful", "calm", "serene", "relaxed", "tranquil", "at ease", "untroubled", "content", "harmonious", "balanced", "composed", "unperturbed", "unfazed", "unflustered", "unruffled", "placid", "still", "quiet","restful"," soothing","pacified"," tranquilized"],
    "restless": ["restless", "fidgety", "uneasy", "bored", "jittery", "antsy", "impatient", "agitated", "unsettled", "discontented", "unfulfilled", "disquieted", "unrestful", "unpeaceful", "unrelaxed"," edgy"," nervous","anxious"," unsettled"," uneasy","impatient"," agitated"," disturbed"," pertubed"],
    "very_sad": ["heartbroken", "devastated", "hopeless", "crying", "lonely", "empty", "despairing", "miserable", "dejected", "downcast", "disheartened", "dispirited", "dismal", "gloomy", "forlorn", "woeful", "sorrowful", "grief-stricken"],
    "sad": ["sad", "down", "upset", "low", "disappointed", "unhappy", "blue", "melancholy", "sorrowful", "depressed", "disheartened", "dispirited", "dismal", "gloomy", "forlorn", "woeful", "sorrowful", "grief-stricken", "downcast", "despondent", "mournful"," unhappy"," downhearted"," heartbroken"," tearful"," regretful"," remorseful"," desolate"," bereaved"],
    "discouraged": ["discouraged", "demotivated", "frustrated", "let down", "disheartened", "dispirited", "unmotivated", "downcast", "dejected", "disappointed", "unfulfilled"," disc"," dismayed","dillusioned","disenchanted"," discontented"," disillusioned"," disenchanted"," discontented"," disheartened"," downcast"," dejected"," demoralized"," dispirited"," unmotivated"],
    "devastated": ["devastated", "shattered", "crushed", "broken", "heartbroken", "desolate", "despairing", "distraught", "overwhelmed", "sorrowful", "grief-stricken", "mournful"," bereaved"," inconsolable"," anguished"," forlorn"," woeful"," despondent"," downcast"," disconsolate"," disheartened"," brokenhearted"],
    "ecstatic": ["ecstatic", "blissful", "euphoric", "rapturous", "elated", "overjoyed", "thrilled", "exhilarated", "exuberant", "jubilant", "radiant", "happy vala emotional"],
    "content": ["content", "satisfied", "fulfilled", "at peace", "pleased", "gratified", "happy", "serene", "untroubled", "complacent", "self-satisfied", "pleased", "gratified","fulfilled","at peace"," contented"],
    "angry": ["angry", "mad", "furious", "irritated", "annoyed", "frustrated", "enraged", "infuriated", "livid", "exasperated", "indignant", "outraged", "incensed", "resentful","cross","irate","wrathful","heated","fuming","seething","raging","stormy","tempestuous","volatile","fierce","ferocious","vicious","savage","belligerent"],
    "happy": ["happy","awesome","fabulous","joyful", "glad", "smiling", "cheerful", "content", "satisfied", "pleased", "delighted", "jovial", "jubilant", "radiant", "exuberant"," merry","sunny","lighthearted","elated","thrilled","euphoric","jocund"],
    "grateful": ["grateful", "thankful", "blessed", "appreciative", "indebted", "obliged","pleased" , " content","satisfied","joyful","happy","cheerful","delighted","jovial","jubilant","radiant","exuberant","thankful","blessed","appreciative","indebted","obliged","pleased","content","satisfied"],
    "hopeful": ["hopeful", "looking forward", "optimistic", "confident", "expectant", "assured", "buoyant", "encouraged", "enthusiastic", "inspired", "positive", "upbeat","expectant"]
}

shloks = {
    "positive": [("कर्मण्येवाधिकारस्ते मा फलेषु कदाचन।", "You have a right to perform your duties, but never to the fruits of those actions.")],
    "negative": [("श्रेयान्स्वधर्मो विगुणः परधर्मात्स्वनुष्ठितात्।", "It is better to fail in one's own duty than to succeed in another’s.")],
    "neutral": [("योगस्थः कुरु कर्माणि सङ्गं त्यक्त्वा धनञ्जय।", "Perform your duty equipoised, abandoning all attachment to success or failure.")],
    "anxious": [("मा ते संगोऽस्त्वकर्मणि。", "Do not be attached to inaction.")],
    "peaceful": [("शान्तिमाप्नोति नैष्ठिकीम्。", "One attains supreme peace.")],
    "angry": [("क्रोधाद्भवति सम्मोहः सम्मोहात्स्मृतिविभ्रमः。", "From anger comes delusion, from delusion the loss of memory.")],
    "spin_message": [("सर्वं खल्विदं ब्रह्म।", "All this is indeed Brahman. (A reminder of the interconnectedness of all things.)")],
    "very_happy": [("न हि कश्चित्क्षणमपि जातु तिष्ठत्यकर्मकृत्。", "No one can remain without action even for a moment."),("आत्मौपम्येन सर्वत्र समं पश्यति योऽर्जुन。", "That yogi sees all beings with an equal vision, rejoicing in the welfare of all.")],
    "pessimistic": [("मात्मानं अवसादयेत्。", "Do not allow yourself to sink into despair."),("न हि कल्याणकृत्कश्चिद् दुर्गतिं तात गच्छति。", "One who does good, My friend, never comes to grief.")],
    "optimistic": [("मां अनन्याश्चिन्तयन्तो ये जनाः पर्युपासते。", "Those who worship me with unwavering devotion — I carry what they lack."),("न हि कल्याणकृत्कश्चिद् दुर्गतिं taata गच्छति。", "One who does good, My friend, never comes to grief.")],
    "overwhelmed": [("समं सर्वेषु भूतेषु तिष्ठन्तं परमेश्वरम्。", "See the Lord equally present in all beings."),("युक्ताहारविहारस्य युक्तचेष्टस्य कर्मसु।", "Balance in eating, recreation, and actions brings peace.")],
    "restless": [("चञ्चलं हि मनः कृष्ण", "The mind is restless, turbulent, obstinate, and very strong."),("असंशयं महाबाहो मनो दुर्निग्रहं चलम्。", "Undoubtedly, the mind is restless and hard to control.")],
    "very_sad": [("न जायते म्रियते वा कदाचित्。", "The soul is eternal; it neither dies nor is born. — BG 2.20"),("सर्वधर्मान्परित्यज्य मामेकं शरणं व्रज।", "Even the darkest night will end, and the sun will rise. — BG 18.66")],
    "sad": [(" जातस्य हि ध्रुवो मृत्युर्ध्रुवं जन्म मृतस्य च。", "Do not grieve for the living or the dead. — BG 2.27"),("नेहाभिक्रमनाशोऽस्ति प्रत्यवायो न विद्यते。", "Even a little progress on this path protects one from great fear. — BG 2.40")],
    "discouraged": [("यथा दीपो निवातस्थो नेङ्गते सोपमा स्मृता。", "Just as a lamp in a windless place does not flicker, remain steady in the self."),("दुःखेष्वनुद्विग्नमनाः सुखेषु विगतस्पृहः", "One who is undisturbed in sorrow and free from desire in happiness is wise.")],
    "devastated": [("नैनं छिन्दन्ति शस्त्राणि नैनं दहति पावकः。", "Weapons do not cut the soul, fire does not burn it."),("अजो नित्यः शाश्वतोऽयं पुराणो。", "The soul is unborn, eternal, ever-existing, and primeval.")],
    "ecstatic": [("हृष्यन्ति पश्यतां सर्वे लोकाः。", "All worlds rejoice beholding the divine form."),("विस्मयोऽस्मि महात्मन्。", "I am filled with wonder, O great-souled one.")],
    "content": [("सन्तुष्टः सततं योगी यथा लभते तिष्ठति。", "The yogi who is always content remains steady in whatever comes."),("आत्मरतिरेव स्यात् आत्मतृप्तश्च मानवः。", "The person who rejoices in the self and is satisfied in the self is truly content.")],
    "angry": [("क्रोधाद्भवति सम्मोहः सम्मोहात्स्मृतिविभ्रमः。", "From anger comes delusion, from delusion the loss of memory.")],
    "happy": [("सुखदुःखे समे कृत्वा लाभालाभौ जयाजयौ。", "Treating happiness and distress, gain and loss, victory and defeat alike."),("सुखं तु नित्यं सुखिनः सदा", "The one who is always happy is truly blessed.")],
    "grateful": [("सन्तुष्टः सततं योगी यथा लभते तिष्ठति。", "The yogi who is always content remains steady in whatever comes."),("आत्मरतिरेव स्यात् आत्मतृप्तश्च मानवः。", "The person who rejoices in the self and is satisfied in the self is truly content.")],
    "hopeful": [("मां अनन्याश्चिन्तयन्तो ये जनाः पर्युपासते。", "Those who worship me with unwavering devotion — I carry what they lack."),("न हि कल्याणकृत्कश्चिद् दुर्गतिं taata गच्छति。", "One who does good, My friend, never comes to grief.")],
    "lonely": [("मय्येव मन आधत्स्व मयि बुद्धिं निवेशय। निवसिष्यसि मय्येव अत ऊर्ध्वं न संशयः॥", "Anchor your heart in the sacred presence within; you are eternally accompanied and never truly alone. — BG 12.8")],
    "burned_out": [("युक्ताहारविहारस्य युक्तचेष्टस्य कर्मसु। युक्तस्वप्नावबोधस्य योगो भवति दुःखहा॥", "For one who is balanced in recreation, rest, and work, yoga removes all exhaustion and restores vitality. — BG 6.17")],
    "guilty": [("अपि चेत्सुदुराचारो भजते मामनन्यभाक्। साधुरेव स मन्तव्यः सम्यग्व्यवसितो हि सः॥", "Even if one has made errors in the past, a sincere turning toward truth and goodness restores the spirit to virtue. — BG 9.30")],
    "insecure": [("उद्धरेदात्मनात्मानं नात्मानमवसादयेत्। आत्मैव ह्यात्मनो बन्धुरात्मैव रिपुरात्मनः॥", "Elevate yourself by your own mind; never debase yourself. For the mind alone is your greatest friend, or your fiercest adversary. — BG 6.5")],
    "confused": [("कार्पण्यदोषोपहतस्वभावः पृच्छामि त्वां धर्मसंमूढचेताः। यच्छ्रेयः स्यान्निश्चितं ब्रूहि तन्मे॥", "When the path feels obscured by doubt, pause and seek the inner light; decisive clarity will emerge from stillness. — BG 2.7")],
    "envious": [("अद्वेष्टा सर्वभूतानां मैत्रः करुण एव च। निर्ममो निरहङ्कारः समदुःखसुखः क्षमी॥", "One who holds goodwill toward all, free from envy and possessiveness, steady in joy and sorrow, discovers supreme peace. — BG 12.13")],
    "grief_stricken": [("न जायते म्रियते वा कदाचित्। अजो नित्यः शाश्वतोऽयं पुराणो न हन्यते हन्यमाने शरीरे॥", "The true essence is eternal; it was never born and never dies. Love transcends physical form and remains timeless. — BG 2.20")],
    "serene": [("प्रसादे सर्वदुःखानां हानिरस्योपजायते। प्रसन्नचेतसो ह्याशु बुद्धिः पर्यवतिष्ठते॥", "In tranquil serenity, all distress dissolves away; the intellect of a serene mind becomes steadfast and clear. — BG 2.65")],
    "inspired": [("उत्तिष्ठोत्तिष्ठ भारत। तस्मात्त्वमुत्तिष्ठ यशो लभस्व जित्वा शत्रून्भुङ्क्ष्व राज्यं समृद्धम्॥", "Arise and awaken! Stand forth with noble purpose, channel your gifts, and bring your authentic light to the world. — BG 11.33")],
    "resilient": [("तं विद्याद् दुःखसंयोगवियोगं योगसञ्ज्ञितम्। स निश्चयेन योक्तव्यो योगोऽनिर्विण्णचेतसा॥", "Know that steadfast state of freedom from sorrow as true yoga. Cultivate this resilience with an undaunted spirit. — BG 6.23")]
}

CRISIS_KEYWORDS = [
    r"\bsuicid(?:e|al)\b", r"\bkill (?:myself|me)\b", r"\bend (?:my )?life\b",
    r"\boverdos(?:e|ing)\b", r"\bwant to die\b", r"\bcan'?t go on\b",
    r"\bworthless\b", r"\bnot worth living\b", r"\bcut(ting)? myself\b",
    r"\bharm myself\b", r"\btake my life\b", r"\bend it all\b",
    r"\bsevere chest pain\b", r"\bcan'?t breathe\b", r"\buncontrollable bleeding\b",
    r"\bhaving a stroke\b", r"\bsudden numbness\b", r"\bcollapsed\b",
    r"\bpoisoning\b", r"\bchoking\b", r"\bheart attack\b", r"\bhigh fever\b",
    r"\bunconsciousness\b", r"\bmajor accident\b"
]

FORUM_BLOCK_KEYWORDS = [
    r"\bidiot\b", r"\bstupid\b", r"\bhate you\b", r"\bfailur[e]?\b",
    r"\bruin[s]?(?: my)? life\b"
]

HELPLINES = {
    "IN": {
        "mental_health": [
            {"name": "Tele MANAS (24/7)", "number": "14416 / 1-800-891-4416"},
            {"name": "Vandrevala Foundation (24/7)", "number": "+91 9999666555"},
            {"name": "KIRAN Helpline (24/7)", "number": "1800-599-0019"},
        ],
        "emergency": "112"
    },
    "DEFAULT": {
        "mental_health": [
            {"name": "Local Crisis Line", "number": "Please check local resources or emergency services"}
        ],
        "emergency": "Call your local emergency number"
    }
}

openai_client = None
if os.environ.get("OPENAI_API_KEY"):
    try:
        from openai import OpenAI
        openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    except Exception as e:
        print(f"[OpenAI Info] Initialization failed inside Flask: {e}")

# Helper Functions
def _matches_any(patterns, text):
    for pattern in patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False

def _choose_helplines(locale="IN"):
    return HELPLINES.get(locale, HELPLINES["DEFAULT"])

def create_crisis_message(locale="IN"):
    helplines = _choose_helplines(locale)
    emergency_line = helplines.get("emergency", "Call local emergency")
    mh_lines = helplines.get("mental_health", [])

    message = (
        "🚨 URGENT CRISIS ALERT 🚨\n\n"
        "Your recent entries suggest you may be in distress. Please reach out for immediate, "
        "confidential support. You are not alone.\n\n"
        "---------------------------------------------------\n"
        f"## 📞 CRISIS & MENTAL HEALTH SUPPORT ({locale.upper()})\n"
        "---------------------------------------------------\n"
        f"| Service | Number | Availability |\n"
        f"| :--- | :--- | :--- |\n"
        f"| **National Emergency** | **{emergency_line}** | **Life-Threatening Situations** |\n"
    )
    if mh_lines:
        for h in mh_lines:
            message += f"| {h['name']} | **{h['number']}** | Emotional/Crisis Counseling |\n"

    message += (
        "---------------------------------------------------\n"
        "\n### Immediate Self-Care Actions:\n"
        "1. **Breathe Slowly**: Inhale for 4 seconds, hold for 4, exhale for 4 (Box Breathing).\n"
        "2. **Ground Yourself**: Find 5 things you can see, 4 you can touch, 3 you can hear, 2 smell, 1 taste.\n"
        "3. **Minimize Stimuli**: Dim lights, reduce noises.\n"
        "4. **Reach Out**: Call a trusted person immediately, even if it's just to distract you.\n"
        "5. **Safe Space Visualization**: Close your eyes and picture a place where you feel completely safe.\n\n"
    )
    return message

def detect_text_context(text):
    text_lower = text.lower()
    context_mapping = {
        "Academic Stress": ["exam", "assignment", "college", "university", "semester", "grades", "deadline", "study", "class", "tuition", "professor", "quiz"],
        "Career / Work": ["job", "work", "office", "boss", "career", "promotion", "interview", "salary", "deadline", "burnout", "manager", "client"],
        "Relationships": ["relationship", "partner", "girlfriend", "boyfriend", "family", "friend", "marriage", "dating", "breakup", "argument"],
        "Health & Body": ["health", "pain", "illness", "doctor", "sleep", "diet", "exercise", "body", "physical", "headache", "stomach"],
        "Financial Pressure": ["money", "debt", "loan", "rent", "bills", "savings", "budget", "finance", "expensive", "afford"],
        "Self-Esteem": ["confidence", "self-worth", "esteem", "worthless", "compare", "body image", "appearance", "imposter", "inadequate"],
        "Loss & Grief": ["loss", "grief", "bereavement", "death", "lost", "heartbroken", "mourning", "miss them"],
        "Social Anxiety & Loneliness": ["lonely", "alone", "isolated", "social anxiety", "party", "awkward", "left out", "no friends", "shyness"],
        "Family & Home Dynamics": ["parent", "mother", "father", "dad", "mom", "sibling", "household", "home", "relative"],
        "Burnout & Overwork": ["exhaustion", "no energy", "non-stop", "drained", "can't go on working", "swamped", "overworked"],
        "Identity & Life Purpose": ["purpose", "meaning of life", "direction", "calling", "passion", "future path", "existential"],
        "Romantic Heartbreak & Dating": ["broken heart", "rejection", "divorce", "ghosted", "unrequited"],
        "Sleep & Physical Fatigue": ["insomnia", "can't sleep", "sleep deprivation", "tired", "nightmare", "fatigue"],
        "Habits & Mind Wandering": ["distracted", "procrastination", "bad habit", "phone addiction", "scroll", "attention", "can't focus"],
        "General Wellbeing": ["stress", "anxious", "sad", "happy", "overwhelmed", "angry", "tired", "peaceful", "grateful"]
    }
    for label, keywords in context_mapping.items():
        if any(re.search(r'\b' + re.escape(word) + r'\b', text_lower) for word in keywords):
            return label
    return "General Wellbeing"

def check_recent_mood_trends(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    one_week_ago = datetime.now() - timedelta(days=7)
    cursor.execute("SELECT mood FROM journal WHERE user_id = %s AND timestamp >= %s", (user_id, one_week_ago))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    mood_counts = {}
    for row in rows:
        for mood in row[0].split(','):
            mood_key = mood.strip().lower()
            mood_counts[mood_key] = mood_counts.get(mood_key, 0) + 1

    feedback = ""
    negative_moods = ["sad", "anxious", "overwhelmed", "stressed", "very_sad", "devastated", "angry"]
    top_negative_mood = None
    max_count = 0

    for mood in negative_moods:
        count = mood_counts.get(mood, 0)
        if count >= max_count and count >= 3:
            max_count = count
            top_negative_mood = mood

    if top_negative_mood:
        feedback = f"📈 **Trend Alert:** We noticed your mood has been **{top_negative_mood.title()}** {max_count} times in the last 7 days. This persistent feeling is valid. Remember to focus on your coping goals."
    return feedback

def check_risk_escalation(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    two_weeks_ago = datetime.now() - timedelta(days=14)
    cursor.execute("SELECT risk_level, DATE(timestamp) FROM journal WHERE user_id = %s AND timestamp >= %s", (user_id, two_weeks_ago))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    high_risk_days = set()
    HIGH_DISTRESS_RISKS = ['high', 'very high risk', 'medium-high']
    for level, entry_date in rows:
        if level in HIGH_DISTRESS_RISKS:
            high_risk_days.add(entry_date)

    return len(high_risk_days) >= 3

def analyze_and_reframe(thought: str, mood: str, locale: str = "IN"):
    if not thought:
        return {"level": "reframe", "message": None, "helplines": None, "reframed_text": "", "risk_level": "low"}
    lowered = thought.lower()

    # --- Crisis Detection ---
    is_crisis_ml = False
    if wellness_ml is not None:
        try:
            is_crisis_ml, _ = wellness_ml.predict_crisis(thought)
        except Exception:
            pass

    if is_crisis_ml or _matches_any(CRISIS_KEYWORDS, lowered):
        crisis_message = create_crisis_message(locale)
        return {"level": "crisis", "message": crisis_message, "helplines": HELPLINES.get(locale), "reframed_text": None, "risk_level": "high"}

    global openai_client
    if openai_client:
        try:
            context = detect_text_context(thought)
            response = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a compassionate mental health AI counselor. "
                            f"The user is experiencing '{context}' and their detected mood is '{mood}'. "
                            "Help the user reframe their difficult thought by acknowledging their feelings, offering empathy, and suggesting a gentle perspective shift. "
                            "Use Cognitive Behavioral Therapy (CBT) style language but keep it warm, supportive, and simple. "
                            "Output a JSON object containing: 'personalized_response' (a warm, validating message), 'reframed_text' (a constructive reframe of the user's thought), and 'risk_level' (either 'low' or 'medium')."
                        )
                    },
                    {"role": "user", "content": thought}
                ],
                response_format={"type": "json_object"},
                timeout=6
            )
            import json
            data = json.loads(response.choices[0].message.content)
            p_response = data.get("personalized_response", "I hear you. Remember that feelings are valid even when they feel heavy.")
            reframed = data.get("reframed_text", "")
            risk_level = data.get("risk_level", "low")
            
            llm_response = f"✨ **AI Personalized Response:** {p_response}\n\n🧘 **Reframing Insight:** {reframed}"
            mini_goal_message = ""
            if mood in MINI_GOALS and mood in ["anxious", "stressed", "sad", "angry"]:
                goal_data = MINI_GOALS[mood]
                mini_goal_message = f"\n\n🎯 **Mini-Goal for {mood.title()}:** {goal_data['goal']} (Reward: {goal_data['reward']} MP)"
                
            return {
                "level": "reframe",
                "message": None,
                "helplines": None,
                "reframed_text": llm_response + mini_goal_message,
                "risk_level": risk_level
            }
        except Exception as e:
            print(f"[OpenAI Warning] Reframing failed: {e}")

    # Fallback to local rules
    core_challenge = thought[:80].strip() + ("..." if len(thought) > 80 else ".")
    llm_response = (
        f"**Supportive Response:** I hear you. The core challenge in your thought seems to be: **'{core_challenge}'**\n\n"
    )
    replaced = False
    reframed = ""
    for old_phrase, new_phrase in thought_specific_reframes.items():
        if old_phrase in lowered:
            reframed = new_phrase
            replaced = True
            break

    if not replaced:
        mood_reframe_options = mood_specific_reframes.get(mood.lower(), [])
        custom_reframe = False
        for trigger, response in mood_reframe_options:
            if re.search(re.escape(trigger), thought, re.IGNORECASE):
                reframed = response
                custom_reframe = True
                break

        if not custom_reframe:
            negative_or_neutral_moods = ["negative", "neutral", "sad", "anxious", "overwhelmed", "pessimistic", "discouraged", "very_sad", "devastated", "restless", "angry"]
            if mood.lower() in negative_or_neutral_moods:
                reframed = f"Your original thought: **'{thought}'** \n\n**Reframing Tip:** {random.choice(uplifting_messages)}"
            else:
                reframed = f"Your inner voice is heard. A universal truth for your mood ({mood.title()}): {random.choice(uplifting_messages)}"

    llm_response += f"🧘 **Reframing Insight:** {reframed}"
    mini_goal_message = ""
    if mood in MINI_GOALS and mood in ["anxious", "stressed", "sad", "angry"]:
        goal_data = MINI_GOALS[mood]
        mini_goal_message = f"\n\n🎯 **Mini-Goal for {mood.title()}:** {goal_data['goal']} (Reward: {goal_data['reward']} MP)"

    risk_level = "low"
    if mood in ["very_sad", "devastated", "discouraged", "pessimistic", "angry"]:
        risk_level = "medium"
    elif mood in ["anxious", "overwhelmed"]:
        risk_level = "medium-high"

    return {
        "level": "reframe",
        "message": None,
        "helplines": None,
        "reframed_text": llm_response + mini_goal_message,
        "risk_level": risk_level
    }

# Flask Routes
@app.route('/')
def home():
    is_logged_in = 'user_id' in session
    return render_template('index.html', is_logged_in=is_logged_in, active_tab='home')

# Dedicated Role-Specific Login Routes
@app.route('/login/student')
@app.route('/login/user')
def login_student():
    if 'user_id' in session:
        return redirect_dashboard()
    return render_template('login.html', default_role='student', portal_title='Student & General User Portal')

@app.route('/login/counselor')
def login_counselor():
    if 'user_id' in session:
        return redirect_dashboard()
    return render_template('login.html', default_role='counselor', portal_title='Counselor & Clinical Specialist Portal')

@app.route('/login/admin')
def login_admin():
    if 'user_id' in session:
        return redirect_dashboard()
    return render_template('login.html', default_role='admin', portal_title='Enterprise Administration & Security Gateway')

# Dedicated Counselor Registration Portal
@app.route('/register/counselor', methods=['GET', 'POST'])
def register_counselor():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        email = request.form.get('email', '').strip()
        specialization = request.form.get('specialization', 'General Wellness').strip()
        qualifications = request.form.get('qualifications', '').strip()
        exp_years = request.form.get('experience_years', '3')
        exp_years = int(exp_years) if exp_years.isdigit() else 3
        bio = request.form.get('bio', '').strip()

        if not username or not password:
            flash("Username and password are required.", "error")
            return render_template('register_counselor.html')

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            hashed = hash_password(password, username)
            cursor.execute("""
                INSERT INTO counselors (username, password, specialization, qualifications, experience_years, bio)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (username, hashed, specialization, qualifications, exp_years, bio))
            conn.commit()
            flash("Counselor registration successful! Please sign in with your credentials.", "success")
            return redirect(url_for('login_counselor'))
        except mysql.connector.Error as err:
            flash(f"Counselor registration error: {err.msg}", "error")
        finally:
            cursor.close()
            conn.close()

    return render_template('register_counselor.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect_dashboard()
        
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        role = request.form.get('role', 'student')
        
        if not username or not password:
            flash("Please enter both username and password.", "error")
            return render_template('login.html')
            
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if role == 'admin':
            if username == "admin":
                cursor.execute("SELECT id, password FROM users WHERE username = 'admin'")
                user = cursor.fetchone()
                if user and (user[1] == hash_password(password, "admin") or user[1] == password):
                    session['user_id'] = user[0]
                    session['username'] = "admin"
                    session['role'] = "admin"
                    cursor.close()
                    conn.close()
                    return redirect(url_for('admin_dashboard'))
            flash("Invalid admin credentials.", "error")
            
        elif role == 'counselor':
            cursor.execute("SELECT id, username, password FROM counselors WHERE username = %s", (username,))
            counselor = cursor.fetchone()
            if counselor:
                stored_pwd = counselor[2]
                hashed = hash_password(password, username)
                if stored_pwd == hashed or stored_pwd == password:
                    # Migrate if plain text
                    if stored_pwd == password:
                        cursor.execute("UPDATE counselors SET password = %s WHERE id = %s", (hashed, counselor[0]))
                        conn.commit()
                    session['user_id'] = counselor[0]
                    session['username'] = counselor[1]
                    session['role'] = "counselor"
                    cursor.execute("UPDATE counselors SET online_status = True, last_login = %s WHERE id = %s", (datetime.now(), counselor[0]))
                    conn.commit()
                    cursor.close()
                    conn.close()
                    return redirect(url_for('counselor_dashboard'))
            flash("Invalid counselor credentials.", "error")
            
        else: # Student / Regular User
            cursor.execute("SELECT id, username, password, gender, journal_streak, last_journal_date, mindful_points FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()
            if user:
                uid, uname, stored_pwd, gender, streak, last_date, points = user
                hashed = hash_password(password, username)
                if stored_pwd == hashed or stored_pwd == password:
                    if stored_pwd == password:
                        cursor.execute("UPDATE users SET password = %s WHERE id = %s", (hashed, uid))
                        conn.commit()
                    session['user_id'] = uid
                    session['username'] = uname
                    session['role'] = "student"
                    session['gender'] = gender or 'not_specified'
                    session['streak'] = streak or 0
                    session['points'] = points or 0
                    session['last_journal_date'] = last_date.isoformat() if last_date else None
                    cursor.close()
                    conn.close()
                    return redirect(url_for('dashboard'))
            flash("Invalid student credentials.", "error")
            
        cursor.close()
        conn.close()
    default_role = request.args.get('role', 'student')
    return render_template('login.html', default_role=default_role)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        email = request.form.get('email', '').strip() or None
        gender = request.form.get('gender', 'not_specified')
        age = request.form.get('age', '').strip()
        age = int(age) if age.isdigit() else None
        conditions = request.form.get('conditions', '').strip() or None
        role = request.form.get('role', 'student')
        
        if not username or not password:
            flash("Username and password are required.", "error")
            return render_template('login.html')
            
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            hashed = hash_password(password, username)
            if role == 'counselor':
                specialization = request.form.get('specialization', 'General Wellness')
                cursor.execute("INSERT INTO counselors (username, password, specialization) VALUES (%s, %s, %s)", (username, hashed, specialization))
            else:
                account_for = request.form.get('account_for', 'Self')
                managing_rel = request.form.get('managing_relationship', 'Self')
                cursor.execute("""
                    INSERT INTO users (username, password, email, gender, age, diagnosed_conditions, journal_streak, mindful_points, account_for, managing_relationship) 
                    VALUES (%s, %s, %s, %s, %s, %s, 0, 0, %s, %s)
                """, (username, hashed, email, gender, age, conditions, account_for, managing_rel))
                new_uid = cursor.lastrowid
                
                # If registering for dependent or male managing for women, create initial profile
                if account_for != 'Self' or gender.lower() == 'male':
                    init_name = request.form.get('initial_profile_name') or (f"{username}'s {managing_rel}" if managing_rel != 'Self' else f"{username}'s Partner")
                    init_rel = managing_rel if managing_rel != 'Self' else 'Partner'
                    cursor.execute("""
                        INSERT INTO managed_profiles (user_id, profile_name, relationship, gender, notes)
                        VALUES (%s, %s, %s, 'Female', 'Initial family wellness profile')
                    """, (new_uid, init_name, init_rel))
            conn.commit()
            flash("Registration successful! Please login.", "success")
            return redirect(url_for('login'))
        except mysql.connector.Error as err:
            flash(f"Error during registration: {err.msg}", "error")
        finally:
            cursor.close()
            conn.close()
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    role = session.get('role')
    uid = session.get('user_id')
    if role == 'counselor' and uid:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE counselors SET online_status = False WHERE id = %s", (uid,))
            conn.commit()
            cursor.close()
            conn.close()
        except Exception:
            pass
    session.clear()
    flash("Successfully logged out.", "success")
    return redirect(url_for('login'))

def redirect_dashboard():
    role = session.get('role')
    if role == 'admin':
        return redirect(url_for('admin_dashboard'))
    elif role == 'counselor':
        return redirect(url_for('counselor_dashboard'))
    else:
        return redirect(url_for('dashboard'))

# Student Dashboard Dashboard
@app.route('/dashboard')
def dashboard():
    if not is_regular_user():
        return redirect(url_for('login'))
    
    # Reload streak & points
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT journal_streak, last_journal_date, mindful_points, gender FROM users WHERE id = %s", (session['user_id'],))
    row = cursor.fetchone()
    if row:
        session['streak'] = row[0]
        session['last_journal_date'] = row[1].isoformat() if row[1] else None
        session['points'] = row[2]
        session['gender'] = row[3] or 'not_specified'
    
    # Load managed profiles
    cursor.execute("SELECT id, profile_name, relationship, gender, age FROM managed_profiles WHERE user_id = %s ORDER BY id ASC", (session['user_id'],))
    managed_profiles = cursor.fetchall()

    # Load journal history
    cursor.execute("SELECT id, mood, thought, shlok, shlok_meaning, timestamp, risk_level FROM journal WHERE user_id = %s ORDER BY timestamp DESC", (session['user_id'],))
    journals = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('dashboard.html', active_tab='chatbot', journals=journals, profiles=managed_profiles)

# Journal Submit Route
@app.route('/journal/submit', methods=['POST'])
def journal_submit():
    if not is_regular_user():
        return jsonify({"error": "Unauthorized"}), 401
        
    thought = request.form.get('thought', '').strip()
    if not thought:
        return jsonify({"error": "Empty thought"}), 400
        
    # Analyze sentiment/mood
    mood = "neutral"
    polarity = 0.0
    subjectivity = 0.0
    context = detect_text_context(thought)
    
    # Try OpenAI sentiment first
    global openai_client
    if openai_client:
        try:
            response = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a compassionate psychological sentiment analysis assistant. "
                            "Analyze the user's journal text. Output a JSON object containing: "
                            "'mood' (one of: positive, very_happy, negative, pessimistic, optimistic, neutral, overwhelmed, anxious, peaceful, restless, very_sad, sad, discouraged, devastated, ecstatic, content, angry, happy, grateful, hopeful), "
                            "'context' (a short label), 'polarity' (float from -1.0 to 1.0), and 'subjectivity' (float from 0.0 to 1.0)."
                        )
                    },
                    {"role": "user", "content": thought}
                ],
                response_format={"type": "json_object"},
                timeout=5
            )
            import json
            data = json.loads(response.choices[0].message.content)
            mood = data.get("mood", "neutral").lower()
            context = data.get("context", context)
            polarity = float(data.get("polarity", 0.0))
            subjectivity = float(data.get("subjectivity", 0.0))
        except Exception:
            pass
            
    if mood == "neutral" and wellness_ml is not None:
        try:
            predicted_mood, _ = wellness_ml.predict_mood(thought)
            mood = predicted_mood
            # Simple heuristic mapping for textblob
            blob = TextBlob(thought)
            polarity = blob.sentiment.polarity
            subjectivity = blob.sentiment.subjectivity
        except Exception:
            pass
            
    if mood not in mood_keywords:
        mood = "neutral"
        
    shlok_pair = random.choice(shloks.get(mood, [("योगस्थः कुरु कर्माणि सङ्गं त्यक्त्वा धनञ्जय।", "Perform your duty equipoised, abandoning all attachment to success or failure.")]))
    shlok, meaning = shlok_pair
    
    # Process reframing
    result = analyze_and_reframe(thought, mood)
    risk_level = result['risk_level']
    reframed_clean = result['reframed_text'].replace("*", "") if result['reframed_text'] else ""
    
    # Database Logging
    conn = get_db_connection()
    cursor = conn.cursor()
    timestamp = datetime.now()
    cursor.execute("""
        INSERT INTO journal (user_id, username, mood, thought, shlok, shlok_meaning, timestamp, risk_level)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (session['user_id'], session['username'], mood, thought, shlok, meaning, timestamp, risk_level))
    
    # Gamification: Streak and Points calculation
    points_awarded = 0
    current_date = date.today()
    last_journal_date = None
    cursor.execute("SELECT journal_streak, last_journal_date, mindful_points FROM users WHERE id = %s", (session['user_id'],))
    streak_row = cursor.fetchone()
    
    if streak_row:
        user_streak, last_date, mindful_points = streak_row
        if last_date != current_date:
            new_streak = 1
            if last_date is not None and (current_date - last_date).days == 1:
                new_streak = user_streak + 1
                
            points_awarded += 10
            # Milestone badges
            badge_alert = None
            if new_streak in STREAK_BADGES and new_streak > user_streak:
                points_awarded += 50
                badge_alert = f"Achievement Unlocked! You earned the '{STREAK_BADGES[new_streak]}' badge and 50 MP!"
                
            session['streak'] = new_streak
            session['last_journal_date'] = current_date.isoformat()
            session['points'] = mindful_points + points_awarded
            
            cursor.execute("""
                UPDATE users SET journal_streak = %s, last_journal_date = %s, mindful_points = %s WHERE id = %s
            """, (new_streak, current_date, session['points'], session['user_id']))
            conn.commit()
            
    conn.commit()
    cursor.close()
    conn.close()
    
    # Escalation/Trend feedback
    risk_escalation_alert = ""
    if check_risk_escalation(session['user_id']):
        risk_escalation_alert = (
            "🚨 Sustained Risk Alert: We've detected a pattern of high distress over the past two weeks. "
            "We strongly recommend you reach out to a professional counselor. Please check the Booking tab."
        )
        
    trend_feedback = check_recent_mood_trends(session['user_id'])
    
    # Extract structured mini-goal if available
    mini_goal_obj = None
    if mood.lower() in MINI_GOALS and mood.lower() in ["anxious", "stressed", "sad", "angry"]:
        g_info = MINI_GOALS[mood.lower()]
        mini_goal_obj = {"mood": mood.title(), "goal": g_info["goal"], "reward": g_info["reward"]}

    therapeutic = generate_therapeutic_response(thought, mood, context, polarity)

    response_data = {
        "level": result["level"],
        "mood": mood.upper(),
        "risk_level": risk_level.title(),
        "context": context,
        "shlok": shlok,
        "meaning": meaning,
        "insight": reframed_clean,
        "reframing": therapeutic.get("reframing", ""),
        "affirmation": therapeutic.get("affirmation", ""),
        "micro_action": therapeutic.get("micro_action", ""),
        "philosophical_lens": therapeutic.get("philosophical_lens", ""),
        "full_reply": therapeutic.get("full_reply", ""),
        "mini_goal": mini_goal_obj,
        "points_awarded": points_awarded,
        "total_points": session.get('points', 0),
        "streak": session.get('streak', 0),
        "risk_escalation": risk_escalation_alert,
        "trend_feedback": trend_feedback,
        "badge_alert": badge_alert if 'badge_alert' in locals() else None,
        "message": result.get("message") # for crisis
    }
    
    return jsonify(response_data)

# Screenings Tab
@app.route('/screenings', methods=['GET', 'POST'])
def screenings():
    if not is_regular_user():
        return redirect(url_for('login'))
        
    if request.method == 'POST':
        tool = request.form.get('tool_name') # PHQ-9 or GAD-7
        score = int(request.form.get('score', 0))
        
        # Calculate risk level
        risk_level = "Low Risk"
        if tool == "PHQ-9":
            if score >= 20: risk_level = "Severe Depression (Very High Risk)"
            elif score >= 15: risk_level = "Moderately Severe Depression (High Risk)"
            elif score >= 10: risk_level = "Moderate Depression (Medium-High Risk)"
            elif score >= 5: risk_level = "Mild Depression (Medium Risk)"
        else: # GAD-7
            if score >= 15: risk_level = "Severe Anxiety (High Risk)"
            elif score >= 10: risk_level = "Moderate Anxiety (Medium-High Risk)"
            elif score >= 5: risk_level = "Mild Anxiety (Medium Risk)"
            
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO screenings (user_id, timestamp, tool_name, score, risk_level) VALUES (%s, %s, %s, %s, %s)",
                       (session['user_id'], datetime.now(), tool, score, risk_level))
        conn.commit()
        cursor.close()
        conn.close()
        flash(f"Screening logged successfully! Score: {score} ({risk_level})", "success")
        return redirect(url_for('screenings'))
        
    # Get previous screenings
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT tool_name, score, risk_level, timestamp FROM screenings WHERE user_id = %s ORDER BY timestamp DESC", (session['user_id'],))
    screenings_history = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template('screenings.html', screenings=screenings_history)

# Machine Learning Recommendation & Resources Tab
@app.route('/resources')
def resources():
    if not is_regular_user():
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Fetch age, gender
    cursor.execute("SELECT age, gender FROM users WHERE id = %s", (session['user_id'],))
    user = cursor.fetchone()
    age = user[0] if user and user[0] is not None else 20
    gender = user[1] or 'female'
    
    # 2. Fetch last screening scores
    cursor.execute("SELECT score FROM screenings WHERE user_id = %s AND tool_name = 'PHQ-9' ORDER BY timestamp DESC LIMIT 1", (session['user_id'],))
    phq_row = cursor.fetchone()
    phq = phq_row[0] if phq_row else 0
    
    cursor.execute("SELECT score FROM screenings WHERE user_id = %s AND tool_name = 'GAD-7' ORDER BY timestamp DESC LIMIT 1", (session['user_id'],))
    gad_row = cursor.fetchone()
    gad = gad_row[0] if gad_row else 0
    
    # 3. Calculate avg journal polarity
    cursor.execute("SELECT thought FROM journal WHERE user_id = %s ORDER BY timestamp DESC LIMIT 5", (session['user_id'],))
    thoughts = cursor.fetchall()
    
    avg_pol = 0.0
    if thoughts:
        pols = []
        for row in thoughts:
            blob = TextBlob(row[0] or "")
            pols.append(blob.sentiment.polarity)
        avg_pol = sum(pols) / len(pols)
        
    # Make prediction using wellness_ml PyTorch model
    class_idx = 0
    probs = [0.25, 0.25, 0.25, 0.25]
    if wellness_ml is not None:
        try:
            class_idx, probs = wellness_ml.recommend_resource(age, gender, phq, gad, avg_pol)
        except Exception as e:
            print(f"[ML Prediction Error] {e}")

    # Fetch community resources from user_resources table
    community_resources = []
    try:
        cursor.execute("SELECT resource_type, title, description, username, timestamp FROM user_resources ORDER BY timestamp DESC LIMIT 20")
        rows = cursor.fetchall()
        for r in rows:
            community_resources.append({
                "type": r[0],
                "title": r[1],
                "desc": r[2],
                "user": r[3],
                "time": r[4].strftime("%b %d, %Y") if r[4] else ""
            })
    except Exception as e:
        print("[DB Error] Fetch user_resources:", e)
            
    cursor.close()
    conn.close()
    
    classes_details = {
        0: {
            "title": "Recommended: Self-Care & Info Guides",
            "desc": f"Your current metrics (PHQ-9: {phq}, GAD-7: {gad}, Mood: {avg_pol:.2f}) indicate stable emotional patterns. We recommend reviewing our self-care guides, breathing techniques, and practice saying 'no' to protect boundaries.",
            "type": "Guides"
        },
        1: {
            "title": "Recommended: Stress Management Videos",
            "desc": f"Your stress indicators are slightly elevated (PHQ-9: {phq}, GAD-7: {gad}). Watching expert-guided videos on managing exam burnout and breathing techniques can provide immediate relief.",
            "type": "Videos"
        },
        2: {
            "title": "Recommended: Relaxation & Mindfulness Audios",
            "desc": f"Your logs suggest a high degree of tension or anxiety (PHQ-9: {phq}, GAD-7: {gad}, Mood: {avg_pol:.2f}). We highly recommend taking a break to listen to Forest Rain Soundscapes or doing a 10-minute guided mindfulness meditation.",
            "type": "Audio"
        },
        3: {
            "title": "Recommended: Book a Counselor Session",
            "desc": f"Your screening results indicate a severe clinical risk level (PHQ-9: {phq}, GAD-7: {gad}, Mood: {avg_pol:.2f}). Please consider taking a private, anonymous session with our certified professional counselors for guidance.",
            "type": "Counseling"
        }
    }
    
    recommendation = classes_details[class_idx]
    
    return render_template('resources.html', rec=recommendation, phq=phq, gad=gad, pol=avg_pol, probs=probs, community_resources=community_resources)

@app.route('/api/resources/submit', methods=['POST'])
def api_submit_resource():
    if not is_regular_user():
        return jsonify({"error": "Unauthorized"}), 401
    data = request.get_json(silent=True) or request.form
    title = data.get('title', '').strip()
    resource_type = data.get('resource_type', 'Community Suggestion').strip()
    description = data.get('description', '').strip()
    
    if not title or not description:
        return jsonify({"error": "Title and description are required"}), 400
        
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO user_resources (user_id, username, resource_type, title, description, timestamp) VALUES (%s, %s, %s, %s, %s, %s)",
            (session['user_id'], session['username'], resource_type, title, description, datetime.now())
        )
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"success": True, "message": "Resource submitted successfully!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Peer Support Forum Tab
@app.route('/forum', methods=['GET', 'POST'])
def forum():
    if not is_regular_user():
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        category = request.form.get('category', 'Mental Health')
        message = request.form.get('message', '').strip()
        
        if not title or not message:
            flash("Title and message cannot be empty.", "error")
            return redirect(url_for('forum'))
            
        # Moderation check
        full_text = (title + " " + message).lower()
        if _matches_any(FORUM_BLOCK_KEYWORDS, full_text):
            flash("Post blocked: Detected disrespectful or abusive content. Please keep discussions supportive and positive.", "error")
            return redirect(url_for('forum'))
            
        cursor.execute("INSERT INTO forum_posts (title, username, category, message) VALUES (%s, %s, %s, %s)",
                       (title, "Anonymous Student", category, message))
        conn.commit()
        flash("Post submitted anonymously to the forum!", "success")
        return redirect(url_for('forum'))
        
    category_filter = request.args.get('category', 'All')
    search_q = request.args.get('q', '').strip()
    if search_q:
        if category_filter == 'All':
            cursor.execute("SELECT title, username, category, message, timestamp FROM forum_posts WHERE title LIKE %s OR message LIKE %s ORDER BY timestamp DESC", (f"%{search_q}%", f"%{search_q}%"))
        else:
            cursor.execute("SELECT title, username, category, message, timestamp FROM forum_posts WHERE category = %s AND (title LIKE %s OR message LIKE %s) ORDER BY timestamp DESC", (category_filter, f"%{search_q}%", f"%{search_q}%"))
    elif category_filter == 'All':
        cursor.execute("SELECT title, username, category, message, timestamp FROM forum_posts ORDER BY timestamp DESC")
    else:
        cursor.execute("SELECT title, username, category, message, timestamp FROM forum_posts WHERE category = %s ORDER BY timestamp DESC", (category_filter,))
        
    posts = cursor.fetchall()
    cursor.close()
    conn.close()
    
    categories = ["All", "Student Life", "Professional Work", "Physical Health", "Mental Health"]
    return render_template('forum.html', posts=posts, categories=categories, active_category=category_filter)

# Counselor Booking Tab
@app.route('/booking', methods=['GET', 'POST'])
@app.route('/counselors', methods=['GET', 'POST'])
def booking():
    if not is_regular_user():
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        counselor_id = request.form.get('counselor_id')
        slot_id = request.form.get('slot_id')
        specialization = request.form.get('specialization', 'General')
        reason = request.form.get('reason', '').strip()
        
        # Verify slot is still available
        cursor.execute("SELECT available, slot_time FROM counselor_slots WHERE id = %s", (slot_id,))
        slot = cursor.fetchone()
        
        if slot and slot[0]:
            # Create booking
            cursor.execute("""
                INSERT INTO bookings (user_id, counselor_id, booking_time, slot_id, specialization_requested, reason, status)
                VALUES (%s, %s, %s, %s, %s, %s, 'Pending')
            """, (session['user_id'], counselor_id, slot[1], slot_id, specialization, reason))
            
            # Make slot unavailable
            cursor.execute("UPDATE counselor_slots SET available = False WHERE id = %s", (slot_id,))
            conn.commit()
            flash("Counseling slot booked successfully! Waiting for approval.", "success")
        else:
            flash("Selected slot is no longer available.", "error")
            
        return redirect(url_for('booking'))
        
    # Get counselors
    cursor.execute("SELECT id, username, specialization, online_status FROM counselors")
    counselors = cursor.fetchall()
    
    # Get available slots
    cursor.execute("""
        SELECT s.id, s.counselor_id, c.username, s.slot_time 
        FROM counselor_slots s 
        JOIN counselors c ON s.counselor_id = c.id 
        WHERE s.available = True AND s.slot_time >= %s
        ORDER BY s.slot_time ASC
    """, (datetime.now(),))
    slots = cursor.fetchall()
    
    # Get user booking history
    cursor.execute("""
        SELECT b.id, c.username, b.booking_time, b.specialization_requested, b.reason, b.status 
        FROM bookings b 
        JOIN counselors c ON b.counselor_id = c.id 
        WHERE b.user_id = %s 
        ORDER BY b.booking_time DESC
    """, (session['user_id'],))
    bookings_history = cursor.fetchall()
    
    # Get active counselor sharing permissions granted by user
    cursor.execute("""
        SELECT p.id, c.username, c.specialization, p.allowed_until, p.can_view_journal, p.can_view_screenings, p.can_view_wellness, p.status 
        FROM counselor_permissions p 
        JOIN counselors c ON p.counselor_id = c.id 
        WHERE p.user_id = %s AND p.status = 'Active' AND p.allowed_until >= %s 
        ORDER BY p.allowed_until DESC
    """, (session['user_id'], datetime.now().date()))
    active_permissions = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('booking.html', counselors=counselors, slots=slots, bookings=bookings_history, permissions=active_permissions)

# Multi-Profile & Dependent Management Endpoints
@app.route('/api/profile/add', methods=['POST'])
def api_profile_add():
    if not is_regular_user():
        return redirect(url_for('login'))
        
    profile_name = request.form.get('profile_name', '').strip()
    relationship = request.form.get('relationship', 'Dependent').strip()
    gender = request.form.get('gender', 'Female').strip()
    age = request.form.get('age', '').strip()
    age = int(age) if age.isdigit() else None
    notes = request.form.get('notes', '').strip()
    
    if not profile_name:
        flash("Profile name is required.", "error")
        return redirect(request.referrer or url_for('period'))
        
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO managed_profiles (user_id, profile_name, relationship, gender, age, notes)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (session['user_id'], profile_name, relationship, gender, age, notes))
    conn.commit()
    cursor.close()
    conn.close()
    
    flash(f"Profile '{profile_name}' ({relationship}) added successfully!", "success")
    return redirect(request.referrer or url_for('period'))

@app.route('/api/profile/switch/<int:profile_id>')
def api_profile_switch(profile_id):
    if not is_regular_user():
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    cursor = conn.cursor()
    if profile_id == 0:
        session['active_profile_id'] = None
        session['active_profile_name'] = session.get('username')
        session['active_relationship'] = 'Self'
        flash("Switched to primary personal account.", "success")
    else:
        cursor.execute("SELECT id, profile_name, relationship FROM managed_profiles WHERE id = %s AND user_id = %s", (profile_id, session['user_id']))
        prof = cursor.fetchone()
        if prof:
            session['active_profile_id'] = prof[0]
            session['active_profile_name'] = prof[1]
            session['active_relationship'] = prof[2]
            flash(f"Active profile switched to {prof[1]} ({prof[2]}).", "success")
    cursor.close()
    conn.close()
    return redirect(request.referrer or url_for('dashboard'))

@app.route('/api/profile/delete/<int:profile_id>', methods=['POST'])
def api_profile_delete(profile_id):
    if not is_regular_user():
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM managed_profiles WHERE id = %s AND user_id = %s", (profile_id, session['user_id']))
    conn.commit()
    cursor.close()
    conn.close()
    
    if session.get('active_profile_id') == profile_id:
        session['active_profile_id'] = None
        session['active_profile_name'] = session.get('username')
        session['active_relationship'] = 'Self'
        
    flash("Managed profile removed.", "success")
    return redirect(request.referrer or url_for('period'))

# Counselor Clinical Access Sharing Endpoints
@app.route('/api/permissions/grant', methods=['POST'])
def api_permissions_grant():
    if not is_regular_user():
        return redirect(url_for('login'))
        
    counselor_id = request.form.get('counselor_id')
    allowed_until = request.form.get('allowed_until')
    can_view_journal = bool(request.form.get('can_view_journal', True))
    can_view_screenings = bool(request.form.get('can_view_screenings', True))
    can_view_wellness = bool(request.form.get('can_view_wellness', True))
    notes = request.form.get('notes', '').strip()
    
    if not counselor_id or not allowed_until:
        flash("Please select a counselor and custom allowed-until date.", "error")
        return redirect(url_for('booking'))
        
    conn = get_db_connection()
    cursor = conn.cursor()
    # Revoke any prior active permission for this counselor and insert new
    cursor.execute("UPDATE counselor_permissions SET status = 'Revoked' WHERE user_id = %s AND counselor_id = %s", (session['user_id'], counselor_id))
    cursor.execute("""
        INSERT INTO counselor_permissions (user_id, counselor_id, allowed_until, status, can_view_journal, can_view_screenings, can_view_wellness, notes)
        VALUES (%s, %s, %s, 'Active', %s, %s, %s, %s)
    """, (session['user_id'], counselor_id, allowed_until, can_view_journal, can_view_screenings, can_view_wellness, notes))
    conn.commit()
    cursor.close()
    conn.close()
    
    flash(f"Clinical access permission granted to counselor until {allowed_until}!", "success")
    return redirect(url_for('booking'))

@app.route('/api/permissions/revoke/<int:perm_id>', methods=['POST'])
def api_permissions_revoke(perm_id):
    if not is_regular_user():
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE counselor_permissions SET status = 'Revoked' WHERE id = %s AND user_id = %s", (perm_id, session['user_id']))
    conn.commit()
    cursor.close()
    conn.close()
    flash("Counselor access permission revoked immediately.", "success")
    return redirect(url_for('booking'))

# Counselor Client Case Progress View
@app.route('/counselor/client/<int:client_id>')
def counselor_client_view(client_id):
    if 'role' not in session or session['role'] not in ['counselor', 'admin']:
        flash("Counselor credentials required to view client records.", "error")
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    perm = None
    if session['role'] == 'counselor':
        cursor.execute("""
            SELECT id, allowed_until, can_view_journal, can_view_screenings, can_view_wellness
            FROM counselor_permissions
            WHERE counselor_id = %s AND user_id = %s AND status = 'Active' AND allowed_until >= %s
        """, (session['user_id'], client_id, datetime.now().date()))
        perm_row = cursor.fetchone()
        if not perm_row:
            cursor.close()
            conn.close()
            flash("Access expired or permission has not been granted by this client.", "error")
            return redirect(url_for('counselor_dashboard'))
        perm = {
            "id": perm_row[0],
            "allowed_until": perm_row[1],
            "can_view_journal": perm_row[2],
            "can_view_screenings": perm_row[3],
            "can_view_wellness": perm_row[4]
        }
    else: # admin has full visibility
        perm = {
            "allowed_until": datetime.now().date() + timedelta(days=365),
            "can_view_journal": True,
            "can_view_screenings": True,
            "can_view_wellness": True
        }
        
    cursor.execute("SELECT id, username, email, gender, age, diagnosed_conditions, journal_streak FROM users WHERE id = %s", (client_id,))
    client_row = cursor.fetchone()
    if not client_row:
        cursor.close()
        conn.close()
        flash("Client record not found.", "error")
        return redirect(url_for('counselor_dashboard'))
        
    client_data = {
        "id": client_row[0],
        "username": client_row[1],
        "email": client_row[2],
        "gender": client_row[3] or 'Not Specified',
        "age": client_row[4],
        "diagnosed_conditions": client_row[5],
        "journal_streak": client_row[6]
    }
    
    journals = []
    if perm['can_view_journal']:
        cursor.execute("SELECT id, mood, thought, shlok, shlok_meaning, timestamp, risk_level FROM journal WHERE user_id = %s ORDER BY timestamp DESC LIMIT 15", (client_id,))
        journals = cursor.fetchall()
        
    screenings = []
    if perm['can_view_screenings']:
        cursor.execute("SELECT id, timestamp, tool_name, tool_name, score, risk_level FROM screenings WHERE user_id = %s ORDER BY timestamp DESC LIMIT 10", (client_id,))
        screenings = cursor.fetchall()
        
    cursor.close()
    conn.close()
    return render_template('counselor_client_view.html', client_data=client_data, permission=perm, journals=journals, screenings=screenings)


# Period Tracker Tab (With Multi-Profile & Male Ally Mode)

@app.route('/period', methods=['GET', 'POST'])
def period():
    if not is_regular_user():
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Retrieve user gender & managed profiles
    session_gender = (session.get('gender') or '').lower()
    cursor.execute("SELECT gender, account_for, managing_relationship FROM users WHERE id = %s", (session['user_id'],))
    u_info = cursor.fetchone()
    db_gender = (u_info[0] or '').lower() if u_info else ''
    user_gender = session_gender or db_gender
    is_male = (user_gender == 'male' or session_gender == 'male')
    
    cursor.execute("SELECT id, profile_name, relationship, gender, age, notes FROM managed_profiles WHERE user_id = %s ORDER BY id ASC", (session['user_id'],))
    managed_profiles = cursor.fetchall()
    
    active_pid = request.args.get('profile_id', type=int) or session.get('active_profile_id')
    active_prof = None
    if active_pid:
        for p in managed_profiles:
            if p[0] == active_pid:
                active_prof = p
                break
                
    is_caregiver_mode = is_male or len(managed_profiles) > 0
    
    if request.method == 'POST':
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date') or None
        moods = request.form.getlist('moods') or [request.form.get('mood', 'peaceful')]
        moods_str = ",".join(moods) if isinstance(moods, list) else str(moods)
        symptoms = request.form.get('symptoms', '').strip()
        flow = request.form.get('flow', 'Normal')
        energy = request.form.get('energy', '5')
        sleep = request.form.get('sleep', 'Normal')
        gratitude = request.form.get('gratitude', '').strip()
        notes = request.form.get('notes', '').strip()
        
        if not start_date:
            flash("Please specify a cycle start date.", "error")
            return redirect(url_for('period'))

        # Check if entry with this start_date already exists for desktop parity
        cursor.execute("SELECT id FROM period_cycles WHERE user_id = %s AND start_date = %s", (session['user_id'], start_date))
        existing_cycle = cursor.fetchone()
        
        # Clinical diagnostic fields (PCOS, PMDD, PMS, Endometriosis, Pain Score)
        condition_list = request.form.getlist('conditions')
        condition_tags = ", ".join(condition_list) if condition_list else (request.form.get('condition_tags') or '')
        pain_score = request.form.get('pain_score', type=int)
        flow_texture = request.form.get('flow_texture', 'Standard')
        cycle_phase_req = request.form.get('cycle_phase', '')

        if existing_cycle:
            if end_date or condition_tags or pain_score is not None:
                cursor.execute("""
                    UPDATE period_cycles 
                    SET end_date = COALESCE(%s, end_date), 
                        notes = %s, 
                        condition_tags = COALESCE(%s, condition_tags), 
                        pain_score = COALESCE(%s, pain_score), 
                        flow_texture = COALESCE(%s, flow_texture),
                        cycle_phase = COALESCE(%s, cycle_phase)
                    WHERE id = %s
                """, (end_date, notes or symptoms, condition_tags or None, pain_score, flow_texture or None, cycle_phase_req or None, existing_cycle[0]))
        else:
            prof_id = request.form.get('profile_id', type=int) or (active_prof[0] if active_prof else None)
            prof_name = request.form.get('profile_name') or (active_prof[1] if active_prof else 'Self')
            rel_tag = request.form.get('relation_tag') or (active_prof[2] if active_prof else ('Partner' if is_male else 'Self'))
            cursor.execute("""
                INSERT INTO period_cycles 
                (user_id, start_date, end_date, notes, profile_id, profile_name, relation_tag, condition_tags, pain_score, cycle_phase, flow_texture) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (session['user_id'], start_date, end_date, notes or symptoms, prof_id, prof_name, rel_tag, condition_tags or None, pain_score, cycle_phase_req or None, flow_texture))
        
        # Log to journal for desktop parity
        thought_summary = f"Symptoms: {symptoms}\nFlow: {flow}\nEnergy: {energy}/10\nSleep: {sleep}\nGratitude: {gratitude}\nNotes: {notes}"
        cursor.execute("""
            INSERT INTO journal (user_id, username, mood, thought, shlok, shlok_meaning, timestamp, risk_level)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (session['user_id'], session['username'], moods_str, thought_summary, "Period Journal Entry", "Honoring natural bodily rhythms", datetime.now(), "low"))
        
        # Award Mindful Points (+15 MP)
        cursor.execute("UPDATE users SET mindful_points = mindful_points + 15 WHERE id = %s", (session['user_id'],))
        session['points'] = session.get('points', 0) + 15
        
        conn.commit()
        flash("Cycle & wellness check-in saved successfully! (+15 Mindful Points)", "success")
        return redirect(url_for('period'))
        
    # Get cycles history with full clinical parameters
    cursor.execute("""
        SELECT start_date, end_date, notes, DATEDIFF(end_date, start_date), 
               profile_id, profile_name, relation_tag, condition_tags, pain_score, 
               cycle_phase, flow_texture, cervical_fluid, basal_temp, id
        FROM period_cycles 
        WHERE user_id = %s 
        ORDER BY start_date DESC
    """, (session['user_id'],))
    cycles = cursor.fetchall()
    
    # Calculate simple cycle statistics (averages & predictions)
    cycle_lengths = []
    intervals = []
    avg_cycle = "28.0 Days (Est.)"
    avg_interval = "28.0 Days (Est.)"
    current_cycle_day = "Day 1 (Ready)"
    next_period_estimate = "Upcoming Cycle"
    
    if len(cycles) > 0:
        cycle_lengths = [row[3] for row in cycles if row[3] is not None and row[3] > 0]
        if cycle_lengths:
            avg_cycle = f"{sum(cycle_lengths) / len(cycle_lengths):.1f} Days"
            
        if len(cycles) > 1:
            for i in range(len(cycles) - 1):
                diff = (cycles[i][0] - cycles[i+1][0]).days
                if diff > 0:
                    intervals.append(diff)
            if intervals:
                avg_interval = f"{sum(intervals) / len(intervals):.1f} Days"
        
        # Current cycle day
        latest_start = cycles[0][0]
        if latest_start:
            days_since = (datetime.now().date() - latest_start).days + 1
            if days_since >= 1:
                current_cycle_day = f"Day {days_since}"
            
            # Forecast next period
            est_interval = int(round(sum(intervals) / len(intervals))) if intervals else 28
            est_next_date = latest_start + timedelta(days=est_interval)
            next_period_estimate = est_next_date.strftime('%b %d, %Y')
    
    # Calculate Biological Cycle Phase Biofeedback
    days_since_num = 1
    avg_cycle_num = 28
    if len(cycles) > 0 and cycles[0][0]:
        days_since_num = max(1, (datetime.now().date() - cycles[0][0]).days + 1)
        if cycle_lengths:
            avg_cycle_num = max(21, int(round(sum(cycle_lengths) / len(cycle_lengths))))
    current_phase_info = calculate_cycle_phase(days_since_num, avg_cycle_num)

    # Retrieve recent diagnostic screenings (PCOS / PMDD)
    cursor.execute("""
        SELECT id, screener_type, total_score, risk_level, details, created_at, profile_name 
        FROM period_screenings 
        WHERE user_id = %s 
        ORDER BY created_at DESC LIMIT 10
    """, (session['user_id'],))
    screenings_history = cursor.fetchall()
    
    # Retrieve recent daily wellness check-ins from journal (including id for editing)
    cursor.execute("""
        SELECT timestamp, mood, thought, id FROM journal 
        WHERE user_id = %s AND shlok = 'Period Journal Entry' 
        ORDER BY timestamp DESC LIMIT 12
    """, (session['user_id'],))
    wellness_rows = cursor.fetchall()
    
    wellness_logs = []
    mood_counts = {}
    for row in wellness_rows:
        ts = row[0]
        mood_val = row[1]
        thought_val = row[2]
        entry_id = row[3] if len(row) > 3 else None
        symptoms_val = flow_val = energy_val = sleep_val = gratitude_val = notes_val = ""
        for line in (thought_val or "").split("\n"):
            l = line.lower()
            if l.startswith("symptoms:"): symptoms_val = line.split(":", 1)[1].strip()
            elif l.startswith("flow:"): flow_val = line.split(":", 1)[1].strip()
            elif l.startswith("energy:"): energy_val = line.split(":", 1)[1].strip()
            elif l.startswith("sleep:"): sleep_val = line.split(":", 1)[1].strip()
            elif l.startswith("gratitude:"): gratitude_val = line.split(":", 1)[1].strip()
            elif l.startswith("notes:"): notes_val = line.split(":", 1)[1].strip()
        
        wellness_logs.append({
            'id': entry_id,
            'timestamp': ts,
            'mood': mood_val,
            'symptoms': symptoms_val,
            'flow': flow_val,
            'energy': energy_val,
            'sleep': sleep_val,
            'gratitude': gratitude_val,
            'notes': notes_val
        })

        for m in (mood_val or '').split(','):
            m_clean = m.strip().replace('_', ' ').title()
            if m_clean:
                mood_counts[m_clean] = mood_counts.get(m_clean, 0) + 1
                
    cursor.close()
    conn.close()
    
    return render_template(
        'period.html', 
        cycles=cycles, 
        avg_cycle=avg_cycle, 
        avg_interval=avg_interval,
        current_cycle_day=current_cycle_day,
        next_period_estimate=next_period_estimate,
        wellness_logs=wellness_logs,
        mood_counts=mood_counts,
        profiles=managed_profiles,
        active_profile=active_prof,
        is_male=is_male,
        is_caregiver_mode=is_caregiver_mode,
        current_phase=current_phase_info,
        condition_profiles=CONDITION_PROFILES,
        screenings=screenings_history
    )

# To-Do list Tab
@app.route('/todo', methods=['GET', 'POST'])
def todo():
    if not is_regular_user():
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'add':
            task = request.form.get('task', '').strip()
            if task:
                cursor.execute("INSERT INTO to_do_list (user_id, task, completed, points_awarded) VALUES (%s, %s, False, False)", (session['user_id'], task))
                conn.commit()
                flash("Task added!", "success")
                
        elif action == 'complete':
            task_id = request.form.get('task_id')
            cursor.execute("SELECT completed, points_awarded FROM to_do_list WHERE id = %s", (task_id,))
            task = cursor.fetchone()
            if task and not task[0]:
                points_to_award = 15 # 15 MP for task completion
                # Update task
                cursor.execute("UPDATE to_do_list SET completed = True, points_awarded = True WHERE id = %s", (task_id,))
                # Award points
                cursor.execute("UPDATE users SET mindful_points = mindful_points + %s WHERE id = %s", (points_to_award, session['user_id']))
                conn.commit()
                flash(f"Task completed! You earned {points_to_award} Mindful Points!", "success")
                
        elif action == 'delete':
            task_id = request.form.get('task_id')
            cursor.execute("DELETE FROM to_do_list WHERE id = %s AND user_id = %s", (task_id, session['user_id']))
            conn.commit()
            flash("Task deleted.", "success")
            
        return redirect(url_for('todo'))
        
    cursor.execute("SELECT id, task, completed FROM to_do_list WHERE user_id = %s ORDER BY completed ASC, id DESC", (session['user_id'],))
    tasks = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template('todo.html', tasks=tasks)

# Spin Wheel Tab
@app.route('/spinwheel', methods=['GET', 'POST'])
def spinwheel():
    if not is_regular_user():
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        data = request.get_json(silent=True) or {}
        spin_idx = data.get('index')
        if spin_idx is not None and 0 <= int(spin_idx) < len(SPIN_MESSAGES):
            selected = SPIN_MESSAGES[int(spin_idx)]
        else:
            selected = random.choice(SPIN_MESSAGES)
            
        points_won = selected.get("points", 20)
        msg_text = selected.get("message", "You are enough.")
        shlok = selected.get("shlok", "सर्वं खल्विदं ब्रह्म।")
        meaning = selected.get("meaning", "All this is interconnected.")
        
        # Award points
        cursor.execute("UPDATE users SET mindful_points = mindful_points + %s WHERE id = %s", (points_won, session['user_id']))
        
        # Log to journal as spin_message just like desktop SpinWheelFrame
        try:
            cursor.execute(
                "INSERT INTO journal (user_id, username, mood, thought, shlok, shlok_meaning, timestamp) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (session['user_id'], session['username'], 'spin_message', msg_text, shlok, meaning, datetime.now())
            )
        except Exception as e:
            print("Failed to save spin message:", e)
            
        conn.commit()
        
        # Get new total
        cursor.execute("SELECT mindful_points FROM users WHERE id = %s", (session['user_id'],))
        total = cursor.fetchone()[0]
        session['points'] = total
        
        cursor.close()
        conn.close()
        return jsonify({
            "points_won": points_won,
            "total_points": total,
            "message": msg_text,
            "shlok": shlok,
            "meaning": meaning
        })
        
    cursor.execute("SELECT thought, shlok, shlok_meaning, timestamp FROM journal WHERE user_id = %s AND mood = 'spin_message' ORDER BY timestamp DESC LIMIT 7", (session['user_id'],))
    recent_spins = []
    for row in cursor.fetchall():
        recent_spins.append({
            "thought": row[0],
            "shlok": row[1],
            "meaning": row[2],
            "time": row[3].strftime("%b %d, %H:%M") if row[3] else ""
        })
        
    cursor.close()
    conn.close()
    return render_template('spinwheel.html', spin_messages=SPIN_MESSAGES, recent_spins=recent_spins)

# Export Data Tab
@app.route('/export')
@app.route('/export/csv', endpoint='export_csv')
def export_data():
    if not is_regular_user():
        return redirect(url_for('login'))
        
    format_type = request.args.get('format', 'csv')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT timestamp, mood, thought, risk_level, shlok FROM journal WHERE user_id = %s ORDER BY timestamp ASC", (session['user_id'],))
    entries = cursor.fetchall()
    cursor.close()
    conn.close()
    
    if format_type == 'csv':
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Timestamp", "Mood", "Journal Thought", "Distress Risk Level", "Bhagvad Gita Shlok"])
        for row in entries:
            writer.writerow(row)
        
        response = make_response(output.getvalue())
        response.headers["Content-Disposition"] = f"attachment; filename=sarathi_journal_export.csv"
        response.headers["Content-type"] = "text/csv"
        return response
        
    else: # HTML Printable
        html_out = "<html><head><title>My Sarathi Journal Export</title>"
        html_out += "<style>body{font-family: Arial; padding: 25px; background: #fafafa;} h1{color: #8b4513;} table{width: 100%; border-collapse: collapse; margin-top: 15px;} th, td{border: 1px solid #ddd; padding: 10px; text-align: left;} th{background-color: #f2e6d9;}</style>"
        html_out += "</head><body>"
        html_out += f"<h1>Bhagvad Mood Journal - Export for {session['username']}</h1>"
        html_out += f"<p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>"
        html_out += "<table><thead><tr><th>Date</th><th>Mood</th><th>Thought</th><th>Risk Level</th><th>Shlok</th></tr></thead><tbody>"
        for row in entries:
            html_out += f"<tr><td>{row[0]}</td><td>{row[1].upper()}</td><td>{row[2]}</td><td>{row[3].title()}</td><td>{row[4]}</td></tr>"
        html_out += "</tbody></table></body></html>"
        
        response = make_response(html_out)
        response.headers["Content-Disposition"] = f"attachment; filename=sarathi_journal_export.html"
        response.headers["Content-type"] = "text/html"
        return response

# Counselor Dashboard
@app.route('/counselor/dashboard', methods=['GET', 'POST'])
def counselor_dashboard():
    if 'user_id' not in session or session.get('role') not in ['counselor', 'admin']:
        flash("Unauthorized: Counselor credentials required.", "error")
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add_slot':
            slot_time = request.form.get('slot_time')
            if slot_time:
                cursor.execute("INSERT INTO counselor_slots (counselor_id, slot_time, available) VALUES (%s, %s, True)", (session['user_id'], slot_time))
                conn.commit()
                flash("Availability slot added successfully!", "success")
            return redirect(url_for('counselor_dashboard'))
            
        booking_id = request.form.get('booking_id')
        new_status = request.form.get('status') # Approved or Rejected
        
        if booking_id and new_status:
            cursor.execute("UPDATE bookings SET status = %s WHERE id = %s AND counselor_id = %s", (new_status, booking_id, session['user_id']))
            if new_status == 'Rejected':
                cursor.execute("SELECT slot_id FROM bookings WHERE id = %s", (booking_id,))
                slot = cursor.fetchone()
                if slot and slot[0]:
                    cursor.execute("UPDATE counselor_slots SET available = True WHERE id = %s", (slot[0],))
                    
            conn.commit()
            flash(f"Booking {new_status.lower()} successfully!", "success")
            return redirect(url_for('counselor_dashboard'))
        
    # Get counselor bookings
    cursor.execute("""
        SELECT b.id, u.username, b.booking_time, b.specialization_requested, b.reason, b.status 
        FROM bookings b 
        JOIN users u ON b.user_id = u.id 
        WHERE b.counselor_id = %s 
        ORDER BY b.booking_time DESC
    """, (session['user_id'],))
    bookings = cursor.fetchall()
    
    # Get clients who have granted clinical consent to this counselor
    cursor.execute("""
        SELECT p.id, u.id, u.username, p.allowed_until, p.can_view_journal, p.can_view_screenings, p.can_view_wellness, p.notes,
               DATEDIFF(p.allowed_until, CURRENT_DATE) as days_remaining
        FROM counselor_permissions p
        JOIN users u ON p.user_id = u.id
        WHERE p.counselor_id = %s AND p.status = 'Active' AND p.allowed_until >= %s
        ORDER BY p.allowed_until ASC
    """, (session['user_id'], datetime.now().date()))
    permitted_clients = cursor.fetchall()
    
    # Get counselor slots
    cursor.execute("SELECT id, slot_time, available FROM counselor_slots WHERE counselor_id = %s ORDER BY slot_time DESC LIMIT 20", (session['user_id'],))
    counselor_slots = cursor.fetchall()
    
    cursor.close()
    conn.close()
    return render_template('counselor_dashboard.html', bookings=bookings, permitted_clients=permitted_clients, slots=counselor_slots)

# Full-Fledged Admin Dashboard & Operations Console
@app.route('/admin/dashboard', methods=['GET', 'POST'])
def admin_dashboard():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'toggle_status':
            counselor_id = request.form.get('counselor_id')
            cursor.execute("SELECT online_status FROM counselors WHERE id = %s", (counselor_id,))
            current = cursor.fetchone()
            if current:
                new_status = not current[0]
                cursor.execute("UPDATE counselors SET online_status = %s WHERE id = %s", (new_status, counselor_id))
                conn.commit()
                flash("Counselor online status updated!", "success")

        elif action == 'add_counselor':
            new_username = request.form.get('username', '').strip()
            new_password = request.form.get('password', '').strip()
            new_spec = request.form.get('specialization', 'General Wellness').strip()
            if new_username and new_password:
                hashed_pw = hash_password(new_password, new_username)
                try:
                    cursor.execute(
                        "INSERT INTO counselors (username, password, specialization, online_status) VALUES (%s, %s, %s, %s)",
                        (new_username, hashed_pw, new_spec, True)
                    )
                    conn.commit()
                    flash(f"Counselor '{new_username}' added successfully!", "success")
                except Exception as e:
                    flash(f"Error adding counselor: {e}", "error")
            else:
                flash("Counselor username and password cannot be empty.", "error")

        elif action == 'create_slots':
            c_id = request.form.get('counselor_id')
            days_ahead = int(request.form.get('days_ahead', 3))
            slot_hour = int(request.form.get('slot_hour', 10))
            now = datetime.now()
            created_count = 0
            for d in range(1, days_ahead + 1):
                st = datetime(now.year, now.month, now.day, slot_hour, 0) + timedelta(days=d)
                cursor.execute("SELECT id FROM counselor_slots WHERE counselor_id = %s AND slot_time = %s", (c_id, st))
                if not cursor.fetchone():
                    cursor.execute("INSERT INTO counselor_slots (counselor_id, slot_time, available) VALUES (%s, %s, %s)", (c_id, st, True))
                    created_count += 1
            conn.commit()
            flash(f"Generated {created_count} consultation slots successfully!", "success")

        elif action == 'update_booking_status':
            b_id = request.form.get('booking_id')
            new_st = request.form.get('status', 'Approved')
            cursor.execute("UPDATE bookings SET status = %s WHERE id = %s", (new_st, b_id))
            if new_st == 'Rejected':
                cursor.execute("SELECT slot_id FROM bookings WHERE id = %s", (b_id,))
                sl = cursor.fetchone()
                if sl and sl[0]:
                    cursor.execute("UPDATE counselor_slots SET available = True WHERE id = %s", (sl[0],))
            conn.commit()
            flash(f"Booking #{b_id} marked as {new_st}!", "success")

        elif action == 'reset_points':
            u_id = request.form.get('user_id')
            new_pts = int(request.form.get('points', 0))
            cursor.execute("UPDATE users SET mindful_points = %s WHERE id = %s", (new_pts, u_id))
            conn.commit()
            flash(f"User #{u_id} Mindful Points updated to {new_pts} MP!", "success")

        elif action == 'delete_counselor':
            c_id = request.form.get('counselor_id')
            cursor.execute("DELETE FROM counselor_slots WHERE counselor_id = %s", (c_id,))
            cursor.execute("DELETE FROM bookings WHERE counselor_id = %s", (c_id,))
            cursor.execute("DELETE FROM counselors WHERE id = %s", (c_id,))
            conn.commit()
            flash(f"Counselor #{c_id} and associated slots deleted successfully.", "success")

        elif action == 'delete_slot':
            s_id = request.form.get('slot_id')
            cursor.execute("DELETE FROM counselor_slots WHERE id = %s AND available = True", (s_id,))
            conn.commit()
            flash(f"Slot #{s_id} deleted successfully.", "success")

        elif action == 'delete_user':
            u_id = request.form.get('user_id')
            cursor.execute("SELECT role FROM users WHERE id = %s", (u_id,))
            user_r = cursor.fetchone()
            if user_r and user_r[0] != 'admin':
                cursor.execute("DELETE FROM journal WHERE user_id = %s", (u_id,))
                cursor.execute("DELETE FROM period_cycles WHERE user_id = %s", (u_id,))
                cursor.execute("DELETE FROM screenings WHERE user_id = %s", (u_id,))
                cursor.execute("DELETE FROM bookings WHERE user_id = %s", (u_id,))
                cursor.execute("DELETE FROM to_do_list WHERE user_id = %s", (u_id,))
                cursor.execute("DELETE FROM users WHERE id = %s", (u_id,))
                conn.commit()
                flash(f"User #{u_id} removed from system.", "success")
            else:
                flash("Cannot delete an administrative user.", "error")
                
        return redirect(url_for('admin_dashboard'))
        
    # Get stats
    cursor.execute("SELECT COUNT(*) FROM users")
    num_users = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM counselors")
    num_counselors = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM bookings")
    num_bookings = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM journal")
    num_entries = cursor.fetchone()[0]
    cursor.execute("SELECT COALESCE(SUM(mindful_points), 0) FROM users")
    total_points = cursor.fetchone()[0]
    
    # Get counselor list
    cursor.execute("SELECT id, username, specialization, online_status, last_login FROM counselors ORDER BY id ASC")
    counselors = cursor.fetchall()
    
    # Get recent bookings
    cursor.execute("""
        SELECT b.id, u.username, c.username, b.booking_time, b.status 
        FROM bookings b 
        JOIN users u ON b.user_id = u.id 
        JOIN counselors c ON b.counselor_id = c.id 
        ORDER BY b.booking_time DESC LIMIT 20
    """)
    recent_bookings = cursor.fetchall()

    # Get slots list
    cursor.execute("""
        SELECT cs.id, c.username, cs.slot_time, cs.available 
        FROM counselor_slots cs
        JOIN counselors c ON cs.counselor_id = c.id
        ORDER BY cs.slot_time DESC LIMIT 20
    """)
    slots = cursor.fetchall()

    # Get users list
    cursor.execute("SELECT id, username, mindful_points, age, gender, journal_streak FROM users ORDER BY id ASC")
    users_list = cursor.fetchall()

    # Get screenings audit
    cursor.execute("""
        SELECT s.id, u.username, s.tool_name, s.score, s.risk_level, s.timestamp
        FROM screenings s
        JOIN users u ON s.user_id = u.id
        ORDER BY s.timestamp DESC LIMIT 15
    """)
    screenings_audit = cursor.fetchall()

    # Database table statistics
    table_names = ["users", "journal", "counselors", "counselor_slots", "bookings", "forum_posts", "to_do_list", "user_resources", "screenings", "period_cycles"]
    db_stats = []
    for t in table_names:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {t}")
            cnt = cursor.fetchone()[0]
            db_stats.append({"name": t, "count": cnt, "status": "Operational"})
        except Exception:
            db_stats.append({"name": t, "count": 0, "status": "Error"})
            
    cursor.close()
    conn.close()
    
    stats = {
        "users": num_users,
        "counselors": num_counselors,
        "bookings": num_bookings,
        "entries": num_entries,
        "total_points": total_points
    }
    
    return render_template(
        'admin_dashboard.html', 
        stats=stats, 
        counselors=counselors, 
        bookings=recent_bookings,
        slots=slots,
        users_list=users_list,
        screenings_audit=screenings_audit,
        db_stats=db_stats
    )

# --- REST API Endpoints ---
@app.route('/api/health', methods=['GET'])
def api_health():
    return jsonify({
        "status": "healthy",
        "service": "BhagvadMood Platform API",
        "version": "1.0.0"
    }), 200

@app.route('/api/sentiment', methods=['POST'])
def api_sentiment():
    payload = request.get_json(silent=True) or {}
    text = payload.get("text", "").strip()
    if not text:
        return jsonify({"error": "No text provided"}), 400
    
    affect_data = analyze_text_affect(text) if 'analyze_text_affect' in globals() else {"polarity": float(TextBlob(text).sentiment.polarity), "subjectivity": float(TextBlob(text).sentiment.subjectivity)}
    polarity = affect_data["polarity"]
    subjectivity = affect_data["subjectivity"]
    
    mood = "neutral"
    if wellness_ml:
        try:
            mood, _ = wellness_ml.predict_mood(text)
        except Exception:
            mood = "neutral"
    
    if 'extract_nuanced_mood' in globals():
        mood = extract_nuanced_mood(text, mood)
            
    is_crisis = False
    crisis_prob = 0.0
    if wellness_ml:
        try:
            is_crisis, crisis_prob = wellness_ml.predict_crisis(text)
        except Exception:
            pass
            
    shlok_pair = random.choice(shloks.get(mood, [("कर्मण्येवाधिकारस्ते मा फलेषु कदाचन।", "Perform your duty with equanimity.")]))
    context = detect_text_context(text)
    therapeutic = generate_therapeutic_response(text, mood, context, polarity)
    
    return jsonify({
        "mood": mood,
        "polarity": polarity,
        "subjectivity": subjectivity,
        "context": context,
        "is_crisis": is_crisis,
        "crisis_probability": crisis_prob,
        "shlok": shlok_pair[0],
        "shlok_meaning": shlok_pair[1],
        "reframing": therapeutic.get("reframing", ""),
        "affirmation": therapeutic.get("affirmation", ""),
        "micro_action": therapeutic.get("micro_action", ""),
        "philosophical_lens": therapeutic.get("philosophical_lens", ""),
        "full_reply": therapeutic.get("full_reply", "")
    }), 200


@app.route('/api/complete-minigoal', methods=['POST'])
def api_complete_minigoal():
    if not is_regular_user():
        return jsonify({"error": "Unauthorized"}), 401
    payload = request.get_json(silent=True) or {}
    reward = int(payload.get('reward', 20))
    goal = payload.get('goal', 'Mindful mini-goal')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET mindful_points = mindful_points + %s WHERE id = %s", (reward, session['user_id']))
    conn.commit()
    cursor.execute("SELECT mindful_points FROM users WHERE id = %s", (session['user_id'],))
    new_points = cursor.fetchone()[0]
    session['points'] = new_points
    cursor.close()
    conn.close()
    
    return jsonify({
        "success": True,
        "reward": reward,
        "total_points": new_points,
        "message": f"Bravo! You accomplished: '{goal}' and claimed +{reward} Mindful Points!"
    }), 200

@app.route('/api/analytics', methods=['GET'])
def api_analytics():
    if not is_regular_user():
        return jsonify({"error": "Unauthorized"}), 401
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT mood, COUNT(*) FROM journal WHERE user_id = %s GROUP BY mood", (session['user_id'],))
    mood_counts = {row[0].lower(): row[1] for row in cursor.fetchall()}
    
    cursor.execute("SELECT mood, timestamp FROM journal WHERE user_id = %s ORDER BY timestamp DESC LIMIT 14", (session['user_id'],))
    timeline = [{"mood": row[0], "date": row[1].strftime('%b %d')} for row in cursor.fetchall()]
    timeline.reverse()
    
    cursor.close()
    conn.close()
    
    return jsonify({
        "mood_counts": mood_counts,
        "timeline": timeline,
        "streak": session.get('streak', 0),
        "points": session.get('points', 0)
    }), 200

@app.route('/api/journal/delete/<int:entry_id>', methods=['POST', 'DELETE'])
def api_delete_journal(entry_id):
    if not is_regular_user():
        return jsonify({"error": "Unauthorized"}), 401
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM journal WHERE id = %s AND user_id = %s", (entry_id, session['user_id']))
    deleted = cursor.rowcount > 0
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"success": deleted}), 200

@app.route('/api/gita/verses', methods=['GET'])
def api_gita_verses():
    category = request.args.get('category', 'all').lower()
    verse_library = [
        {
            "chapter": 2, "verse": 47, "theme": "Anxiety & Action",
            "sanskrit": "कर्मण्येवाधिकारस्ते मा फलेषु कदाचन। मा कर्मफलहेतुर्भूर्मा ते सङ्गोऽस्त्वकर्मणि॥",
            "meaning": "You have a right to perform your prescribed duty, but never to the fruits of action. Never let outcomes be your motive, nor be attached to inaction.",
            "guidance": "Focus deeply on what is within your control right now. Anxiety arises when you fixate on future consequences rather than current duty."
        },
        {
            "chapter": 2, "verse": 20, "theme": "Fear & Mortality",
            "sanskrit": "न जायते म्रियते वा कदाचित् नायं भूत्वा भविता वा न भूयः। अजो नित्यः शाश्वतोऽयं पुराणो न हन्यते हन्यमाने शरीरे॥",
            "meaning": "The soul is neither born nor does it ever die. Unborn, eternal, ever-existing, and primeval, it is not slain when the body is slain.",
            "guidance": "Your true core is indestructible and transcends temporary emotional storms. Rest in this timeless sanctuary."
        },
        {
            "chapter": 6, "verse": 5, "theme": "Self-Doubt & Despair",
            "sanskrit": "उद्धरेदात्मनाऽऽत्मानं नात्मानमवसादयेत्। आत्मैव ह्यात्मनो बन्धुरात्मैव रिपुरात्मनः॥",
            "meaning": "Elevate yourself by your own mind; do not degrade yourself. For the mind alone is the friend of the self, and the mind alone is the enemy.",
            "guidance": "Treat yourself with the kindness you would extend to a dear friend. Your mind can become your greatest ally through mindful patience."
        },
        {
            "chapter": 2, "verse": 63, "theme": "Anger & Frustration",
            "sanskrit": "क्रोधाद्भवति सम्मोहः सम्मोहात्स्मृतिविभ्रमः। स्मृतिभ्रंशाद् बुद्धिनाशो बुद्धिनाशात्प्रणश्यति॥",
            "meaning": "From anger arises delusion; from delusion comes confusion of memory; from confusion of memory comes loss of intellect; and from loss of intellect, destruction ensues.",
            "guidance": "When anger rises, pause before reacting. Recognize that reactive anger clouds your wisdom. Take 5 grounding breaths."
        },
        {
            "chapter": 6, "verse": 17, "theme": "Burnout & Overwhelm",
            "sanskrit": "युक्ताहारविहारस्य युक्तचेष्टस्य कर्मसु। युक्तस्वप्नावबोधस्य योगो भवति दुःखहा॥",
            "meaning": "He who is regulated in eating, recreation, work, sleep, and wakefulness attains yoga that destroys all sorrow.",
            "guidance": "Balance is sacred. Give yourself permission to pause, sleep, and nourish your body when feeling overwhelmed."
        },
        {
            "chapter": 3, "verse": 17, "theme": "Contentment & Peace",
            "sanskrit": "यस्त्वात्मरतिरेव स्यादात्मतृप्तश्च मानवः। आत्मन्येव च सन्तुष्टस्तस्य कार्यं न विद्यते॥",
            "meaning": "One who rejoices solely in the self, is satisfied with the self, and is content within, for him there are no anxious obligations.",
            "guidance": "True fulfillment comes from within, not external validation. Breathe and rest in your inherent completeness."
        }
    ]
    return jsonify({"verses": verse_library}), 200


@app.route('/api/period/export', methods=['GET'])
def api_period_export():
    if not is_regular_user():
        return redirect(url_for('login'))
    import io, csv
    from flask import Response
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, timestamp, mood, thought, shlok, shlok_meaning 
        FROM journal 
        WHERE user_id = %s AND shlok = 'Period Journal Entry' 
        ORDER BY timestamp DESC
    """, (session['user_id'],))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "timestamp", "mood", "symptoms", "flow", "energy", "sleep", "gratitude", "notes", "shlok", "shlok_meaning"])
    
    for r in rows:
        ts = r[1].strftime("%Y-%m-%d %H:%M:%S") if hasattr(r[1], 'strftime') else str(r[1])
        mood = r[2]
        thought = r[3] or ""
        shlok_text = r[4]
        shlok_meaning = r[5]
        symptoms = flow = energy = sleep = gratitude = notes = ""
        for line in thought.split("\n"):
            l = line.lower()
            if l.startswith("symptoms:"): symptoms = line.split(":", 1)[1].strip()
            elif l.startswith("flow:"): flow = line.split(":", 1)[1].strip()
            elif l.startswith("energy:"): energy = line.split(":", 1)[1].strip()
            elif l.startswith("sleep:"): sleep = line.split(":", 1)[1].strip()
            elif l.startswith("gratitude:"): gratitude = line.split(":", 1)[1].strip()
            elif l.startswith("notes:"): notes = line.split(":", 1)[1].strip()
        writer.writerow([r[0], ts, mood, symptoms, flow, energy, sleep, gratitude, notes, shlok_text, shlok_meaning])
        
    output.seek(0)
    return Response(output.getvalue(), mimetype="text/csv", headers={"Content-Disposition": f"attachment;filename={session['username']}_period_journal.csv"})






# Advanced Period Diagnostic Endpoints (PMDD DSM-5 & PCOS Rotterdam Screeners)
@app.route('/api/period/screener/pmdd', methods=['POST'])
def api_period_screener_pmdd():
    if not is_regular_user():
        if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({"error": "Unauthorized"}), 401
        return redirect(url_for('login'))
        
    data = request.get_json(silent=True) or request.form.to_dict()
    symptom_data = {}
    for k in ['mood_swings', 'irritability_anger', 'depressed_hopeless', 'anxiety_tension',
              'decreased_interest', 'concentration_diff', 'lethargy_fatigue',
              'appetite_cravings', 'sleep_disturbances', 'overwhelmed_control', 'physical_somatic']:
        val = data.get(k, 0)
        try:
            symptom_data[k] = int(val)
        except (ValueError, TypeError):
            symptom_data[k] = 0
            
    res = score_pmdd_dsm5(symptom_data)
    profile_id = session.get('active_profile_id')
    profile_name = session.get('active_profile_name') or 'Self'
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO period_screenings (user_id, profile_id, profile_name, screener_type, total_score, risk_level, details)
        VALUES (%s, %s, %s, 'PMDD', %s, %s, %s)
    """, (session['user_id'], profile_id, profile_name, res['total_score'], res['risk_level'], res['recommendation']))
    cursor.execute("UPDATE users SET mindful_points = mindful_points + 20 WHERE id = %s", (session['user_id'],))
    conn.commit()
    cursor.close()
    conn.close()
    
    session['points'] = session.get('points', 0) + 20
    flash(f"PMDD Screening Completed: {res['tier']} (+20 Mindful Points)", "success")
    
    if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({"success": True, "assessment": res}), 200
    return redirect(url_for('period'))

@app.route('/api/period/screener/pcos', methods=['POST'])
def api_period_screener_pcos():
    if not is_regular_user():
        if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({"error": "Unauthorized"}), 401
        return redirect(url_for('login'))
        
    data = request.get_json(silent=True) or request.form.to_dict()
    pcos_data = {
        'cycle_irregularity': int(data.get('cycle_irregularity', 0)),
        'androgen_signs': int(data.get('androgen_signs', 0)),
        'metabolic_signs': int(data.get('metabolic_signs', 0)),
        'ultrasound_cysts': data.get('ultrasound_cysts') in [True, 'true', '1', 'yes', 'on']
    }
    
    res = score_pcos_assessment(pcos_data)
    profile_id = session.get('active_profile_id')
    profile_name = session.get('active_profile_name') or 'Self'
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO period_screenings (user_id, profile_id, profile_name, screener_type, total_score, risk_level, details)
        VALUES (%s, %s, %s, 'PCOS', %s, %s, %s)
    """, (session['user_id'], profile_id, profile_name, res['score'], res['risk_level'], res['summary']))
    cursor.execute("UPDATE users SET mindful_points = mindful_points + 20 WHERE id = %s", (session['user_id'],))
    conn.commit()
    cursor.close()
    conn.close()
    
    session['points'] = session.get('points', 0) + 20
    flash(f"PCOS Risk Assessment Completed: {res['risk_level']} (+20 Mindful Points)", "success")
    
    if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({"success": True, "assessment": res}), 200
    return redirect(url_for('period'))

# Global Error Handlers (404 and 500)

# Period Cycle Edit & Delete Endpoints
@app.route('/api/period/cycle/edit/<int:cycle_id>', methods=['POST'])
def api_period_cycle_edit(cycle_id):
    if not is_regular_user():
        if request.is_json:
            return jsonify({"error": "Unauthorized"}), 401
        return redirect(url_for('login'))
        
    start_date = request.form.get('start_date') or (request.json.get('start_date') if request.is_json else None)
    end_date = request.form.get('end_date') or (request.json.get('end_date') if request.is_json else None)
    notes = request.form.get('notes', '').strip() if not request.is_json else (request.json.get('notes', '') or '').strip()
    
    conditions = request.form.getlist('conditions') if not request.is_json else (request.json.get('conditions', []) or [])
    condition_tags = ", ".join(conditions) if conditions else (request.form.get('condition_tags') or (request.json.get('condition_tags') if request.is_json else ''))
    
    pain_val = request.form.get('pain_score') if not request.is_json else request.json.get('pain_score')
    pain_score = int(pain_val) if pain_val is not None and str(pain_val).isdigit() else None
    
    flow_texture = request.form.get('flow_texture', 'Standard') if not request.is_json else request.json.get('flow_texture', 'Standard')
    cycle_phase = request.form.get('cycle_phase') if not request.is_json else request.json.get('cycle_phase')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM period_cycles WHERE id = %s AND user_id = %s", (cycle_id, session['user_id']))
    row = cursor.fetchone()
    if not row:
        cursor.close()
        conn.close()
        flash("Cycle record not found or access denied.", "error")
        if request.is_json:
            return jsonify({"error": "Not found"}), 404
        return redirect(url_for('period'))
        
    cursor.execute("""
        UPDATE period_cycles
        SET start_date = COALESCE(%s, start_date),
            end_date = %s,
            notes = %s,
            condition_tags = %s,
            pain_score = %s,
            flow_texture = %s,
            cycle_phase = %s
        WHERE id = %s AND user_id = %s
    """, (start_date or None, end_date or None, notes or None, condition_tags or None, pain_score, flow_texture or None, cycle_phase or None, cycle_id, session['user_id']))
    conn.commit()
    cursor.close()
    conn.close()
    
    flash("Cycle record updated successfully!", "success")
    if request.is_json:
        return jsonify({"success": True, "message": "Cycle record updated"}), 200
    return redirect(url_for('period'))

@app.route('/api/period/cycle/delete/<int:cycle_id>', methods=['POST', 'DELETE'])
def api_period_cycle_delete(cycle_id):
    if not is_regular_user():
        if request.is_json:
            return jsonify({"error": "Unauthorized"}), 401
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM period_cycles WHERE id = %s AND user_id = %s", (cycle_id, session['user_id']))
    deleted = cursor.rowcount > 0
    conn.commit()
    cursor.close()
    conn.close()
    
    flash("Cycle record deleted successfully.", "success")
    if request.is_json:
        return jsonify({"success": deleted}), 200
    return redirect(url_for('period'))

# Daily Wellness Log Edit Endpoint
@app.route('/api/period/wellness/edit/<int:entry_id>', methods=['POST'])
def api_period_wellness_edit(entry_id):
    if not is_regular_user():
        if request.is_json:
            return jsonify({"error": "Unauthorized"}), 401
        return redirect(url_for('login'))
        
    moods = request.form.getlist('moods') or [request.form.get('mood', 'peaceful')]
    moods_str = ",".join(moods) if isinstance(moods, list) else str(moods)
    symptoms = request.form.get('symptoms', '').strip()
    flow = request.form.get('flow', 'Normal')
    energy = request.form.get('energy', '5')
    sleep = request.form.get('sleep', 'Normal')
    gratitude = request.form.get('gratitude', '').strip()
    notes = request.form.get('notes', '').strip()
    
    thought_summary = f"Symptoms: {symptoms}\nFlow: {flow}\nEnergy: {energy}/10\nSleep: {sleep}\nGratitude: {gratitude}\nNotes: {notes}"
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE journal 
        SET mood = %s, thought = %s 
        WHERE id = %s AND user_id = %s AND shlok = 'Period Journal Entry'
    """, (moods_str, thought_summary, entry_id, session['user_id']))
    conn.commit()
    cursor.close()
    conn.close()
    
    flash("Daily wellness entry updated successfully!", "success")
    if request.is_json:
        return jsonify({"success": True}), 200
    return redirect(url_for('period'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    from database_setup import init_db
    try:
        init_db()
        print("[DB INFO] Database initialized successfully.")
    except Exception as e:
        print(f"[DB WARNING] Failed to initialize database: {e}. Check if MySQL is running.")
        
    app.run(debug=True)
