"""
Period & Hormonal Wellness Service (period_service.py)
Provides clinical diagnostics for PCOS/PCOD, PMDD, PMS, and Endometriosis,
cycle phase biofeedback, hormonal mapping, and caregiver intelligence.
"""

from datetime import datetime, timedelta
import io
import csv

# Clinical Condition Taxonomies & Symptoms
CONDITION_PROFILES = {
    "PCOS": {
        "name": "PCOS / PCOD (Polycystic Ovary Syndrome / Disease)",
        "category": "Endocrine & Metabolic",
        "description": "Hormonal imbalance characterized by irregular ovulatory cycles, elevated androgens, and metabolic sensitivities.",
        "common_symptoms": [
            "Irregular cycles (>35 days or skipped periods)",
            "Cystic acne along jawline / chin",
            "Hirsutism (excess facial or body hair)",
            "Hair thinning or androgenic alopecia",
            "Weight changes & insulin resistance cravings",
            "Pelvic discomfort or ovarian cyst sensation",
            "Chronic daytime fatigue"
        ],
        "lifestyle_pillars": [
            "Low-glycemic anti-inflammatory nutrition to stabilize insulin",
            "Gentle resistance training & daily walking over intense HIIT",
            "Spearmint tea (anti-androgenic properties) & Inositol supplementation",
            "Consistent sleep rhythms to regulate cortisol"
        ],
        "vedic_equanimity": "Honor the body's natural pace. Release the illusion of mechanical perfection; steady balance in diet, rest, and action dissolves metabolic strain. — BG 6.17"
    },
    "PMDD": {
        "name": "PMDD (Premenstrual Dysphoric Disorder)",
        "category": "Neuro-Endocrine / Mood Disruption",
        "description": "Severe affective disorder tied to abnormal neurochemical sensitivity to normal luteal progesterone and estrogen shifts.",
        "common_symptoms": [
            "Acute depressive drops or sudden hopelessness in late luteal phase",
            "Marked irritability, rage, or interpersonal conflict escalation",
            "Extreme anxiety, tension, or panic sensations",
            "Rejection sensitive dysphoria (RSD)",
            "Severe brain fog & subjective concentration difficulty",
            "Insomnia or hypersomnia with lethargy",
            "Symptoms vanish within 1-3 days after menses start"
        ],
        "lifestyle_pillars": [
            "Prospective tracking across 2-3 cycles for clinical validation",
            "Targeted magnesium glycinate (300-400mg) and Vitamin B6 (50-100mg)",
            "Luteal workload lightening — protect calendar during days 21-28",
            "Mindful self-compassion — recognize chemical storm vs true reality"
        ],
        "vedic_equanimity": "The senses and transient hormonal currents are like fluctuating seasons. Witness them as passing clouds; your core consciousness remains unstained and pure. — BG 2.14"
    },
    "PMS": {
        "name": "PMS (Premenstrual Syndrome)",
        "category": "Cyclical Somatic & Affective",
        "description": "Common cyclical symptoms occurring 7-10 days before menstruation.",
        "common_symptoms": [
            "Abdominal bloating and fluid retention",
            "Breast tenderness and swelling",
            "Mild emotional volatility or tearfulness",
            "Sugar or salty food cravings",
            "Headaches or fatigue"
        ],
        "lifestyle_pillars": [
            "Hydration and reduced sodium intake in late luteal phase",
            "Warm chamomile and ginger herbal infusions",
            "Consistent light movement and stretching"
        ],
        "vedic_equanimity": "Equanimity in pleasure and mild discomfort restores mental vitality. — BG 2.48"
    },
    "Endometriosis": {
        "name": "Endometriosis & Chronic Pelvic Pain",
        "category": "Inflammatory & Gynecological",
        "description": "Tissue similar to uterine lining growing outside the uterus, causing cyclical inflammatory pain and adhesions.",
        "common_symptoms": [
            "Severe dysmenorrhea (pain score >= 7/10)",
            "Radiating pain to lower back, hips, and thighs",
            "Heavy menstrual flow with clotting (menorrhagia)",
            "Deep pelvic ache and bowel/bladder pain during menses",
            "Exhaustion and systemic inflammation"
        ],
        "lifestyle_pillars": [
            "Anti-inflammatory Mediterranean diet rich in omega-3s",
            "Continuous heat therapy (heating pads, warm baths)",
            "Pelvic floor physical therapy and gentle restorative yoga"
        ],
        "vedic_equanimity": "The body is the sacred temple of the spirit; treat chronic pain with gentle patience, self-holding, and medical advocacy. — BG 13.2"
    }
}

def calculate_cycle_phase(cycle_day, avg_cycle_length=28):
    """
    Computes biological cycle phase, energetic trajectory, hormonal biofeedback,
    and relationship/caregiver guidance based on cycle day.
    """
    if avg_cycle_length is None or avg_cycle_length < 21:
        avg_cycle_length = 28
    
    # Estimate ovulation day (typically 14 days prior to expected menses)
    ovulation_day = max(10, int(avg_cycle_length - 14))
    
    if cycle_day <= 5:
        return {
            "phase": "Menstrual Phase",
            "sub_phase": "Inner Winter",
            "day_range": f"Days 1 - 5 of {avg_cycle_length}",
            "hormones": "Low Estrogen & Progesterone; Prostaglandins active",
            "energy_state": "Restorative / Low Physical Energy",
            "icon": "fa-snowflake",
            "color": "#ef4444",
            "bg_color": "rgba(239, 68, 68, 0.12)",
            "description": "The uterine lining is shedding. Energy turns inward for rest, cellular renewal, and intuitive reflection.",
            "nourishment": "Iron-rich broths, beets, dark leafy greens, warm ginger tea, and adequate hydration.",
            "movement": "Slow gentle walks, yin yoga, gentle spinal twists, and ample sleep.",
            "mindful_wisdom": "Honor the natural winter of the cycle. Rest is not a luxury or a setback; it is the sacred seed of tomorrow's energy. — BG 6.16",
            "caregiver_tip": "Prepare warm soothing drinks, take over heavy physical chores, provide a hot water bottle, and create a calm, quiet environment without pressure."
        }
    elif cycle_day < (ovulation_day - 2):
        return {
            "phase": "Follicular Phase",
            "sub_phase": "Inner Spring",
            "day_range": f"Days 6 - {ovulation_day - 3} of {avg_cycle_length}",
            "hormones": "FSH Stimulating Follicles; Estrogen rising steadily",
            "energy_state": "Rising Vitality & Cognitive Sharpness",
            "icon": "fa-seedling",
            "color": "#10b981",
            "bg_color": "rgba(16, 185, 129, 0.12)",
            "description": "Estrogen is climbing. Neurotransmitters (serotonin and dopamine) increase, boosting creativity, learning, and optimistic forward momentum.",
            "nourishment": "Light, fresh, protein-rich meals, fermented foods (kimchi, kefir), broccoli sprouts, and vibrant citrus.",
            "movement": "Cardio, brisk jogging, dance, creative projects, and learning new skills.",
            "mindful_wisdom": "Awaken your noble potential. Channel your rising vitality into virtuous, purposeful action with an unclouded mind. — BG 3.30",
            "caregiver_tip": "Great time for shared outdoor activities, brainstorming, planning social outings, and trying new creative endeavors together."
        }
    elif (ovulation_day - 2) <= cycle_day <= (ovulation_day + 2):
        return {
            "phase": "Ovulatory Phase",
            "sub_phase": "Inner Summer",
            "day_range": f"Days {ovulation_day - 2} - {ovulation_day + 2} of {avg_cycle_length}",
            "hormones": "Estrogen Peak & Luteinizing Hormone (LH) Surge",
            "energy_state": "Peak Magnetic Vitality & Social Confidence",
            "icon": "fa-sun",
            "color": "#f59e0b",
            "bg_color": "rgba(245, 158, 11, 0.12)",
            "description": "Ovulation occurs. Estrogen peaks and testosterone spikes briefly. Communication, confidence, and metabolic stamina reach their apex.",
            "nourishment": "Fiber-rich vegetables, antioxidant berries, avocados, seeds, and light refreshing meals.",
            "movement": "High-intensity workouts, social presentations, challenging athletic goals.",
            "mindful_wisdom": "Radiate your natural light without ego. Offer your peak energy as a selfless contribution to the world. — BG 4.24",
            "caregiver_tip": "Connect deeply in conversation, celebrate accomplishments, and support her active creative or professional pursuits."
        }
    elif cycle_day < (avg_cycle_length - 5):
        return {
            "phase": "Early Luteal Phase",
            "sub_phase": "Inner Autumn (Steady)",
            "day_range": f"Days {ovulation_day + 3} - {avg_cycle_length - 6} of {avg_cycle_length}",
            "hormones": "Progesterone Rising; Secondary Estrogen Bump",
            "energy_state": "Grounded Productivity & Detail Focus",
            "icon": "fa-leaf",
            "color": "#8b5cf6",
            "bg_color": "rgba(139, 92, 246, 0.12)",
            "description": "Progesterone becomes dominant, creating a calming, grounding effect. Metabolic rate increases slightly. Great for detail work and organization.",
            "nourishment": "Complex carbohydrates (sweet potatoes, brown rice), magnesium-rich pumpkin seeds, and healthy fats.",
            "movement": "Strength training, pilates, steady swimming, and organized home routines.",
            "mindful_wisdom": "Steadfast concentration and regulated effort bring tranquil clarity to every endeavor. — BG 6.26",
            "caregiver_tip": "Offer steady companionship, enjoy comforting home-cooked dinners, and support organized routines."
        }
    else:
        return {
            "phase": "Late Luteal Phase",
            "sub_phase": "Inner Autumn (Pre-Menstrual Window)",
            "day_range": f"Days {avg_cycle_length - 5} - {avg_cycle_length} of {avg_cycle_length}",
            "hormones": "Progesterone & Estrogen Falling (PMDD Vulnerability Window)",
            "energy_state": "Sensitive / Introspective / Vulnerable",
            "icon": "fa-cloud-moon",
            "color": "#ec4899",
            "bg_color": "rgba(236, 72, 153, 0.15)",
            "description": "Hormones are dropping sharply. If affected by PMDD or PMS, chemical sensitivities peak. Central nervous system is more reactive to stress.",
            "nourishment": "Dark chocolate (>=70%), magnesium glycinate, warm herbal infusions, root vegetables, avoiding excess caffeine/sugar.",
            "movement": "Slow mindful walking, gentle stretching, restorative yoga, and warm baths.",
            "mindful_wisdom": "When emotional storms rage, remain steady like the lamp in a windless sanctuary. Feelings are waves; you are the ocean. — BG 6.19",
            "caregiver_tip": "COMPASSION ALERT: High sensitivity window. Do not take sharp words personally, de-escalate conflicts, prepare warm meals, and offer gentle presence without demands."
        }

def score_pmdd_dsm5(symptom_responses):
    """
    Evaluates standardized DSM-5 criteria for Premenstrual Dysphoric Disorder (PMDD).
    Requires at least 5 symptoms in late luteal phase, with at least 1 core affective symptom:
    Core Affective Symptoms:
      1. Marked affective lability (mood swings, tearfulness, rejection sensitivity)
      2. Marked irritability or anger / increased conflicts
      3. Markedly depressed mood, hopelessness, self-deprecating thoughts
      4. Marked anxiety, tension, feeling keyed-up / on edge
    Additional Symptoms:
      5. Decreased interest in usual activities
      6. Subjective difficulty in concentration
      7. Lethargy, easy fatigability, or lack of energy
      8. Marked change in appetite, overeating, or specific food cravings
      9. Hypersomnia or insomnia
      10. Sense of being overwhelmed or out of control
      11. Physical symptoms (breast tenderness, swelling, headaches, joint/muscle pain)
    """
    core_keys = ['mood_swings', 'irritability_anger', 'depressed_hopeless', 'anxiety_tension']
    all_keys = core_keys + [
        'decreased_interest', 'concentration_diff', 'lethargy_fatigue',
        'appetite_cravings', 'sleep_disturbances', 'overwhelmed_control', 'physical_somatic'
    ]
    
    core_count = sum(1 for k in core_keys if symptom_responses.get(k, 0) >= 3)
    total_count = sum(1 for k in all_keys if symptom_responses.get(k, 0) >= 3)
    sum_score = sum(symptom_responses.get(k, 0) for k in all_keys)
    
    if core_count >= 1 and total_count >= 5:
        tier = "Provisional PMDD (Meets DSM-5 Criteria)"
        risk_level = "High Clinical Indication"
        recommendation = "Your symptoms align with DSM-5 criteria for Premenstrual Dysphoric Disorder. We strongly recommend sharing this prospective symptom log with your gynecologist or psychiatrist for formal clinical care."
    elif total_count >= 3 or sum_score >= 18:
        tier = "Moderate to Severe PMS"
        risk_level = "Moderate"
        recommendation = "You experience significant premenstrual discomfort. Targeted nutritional interventions (magnesium, B6, calcium) and stress modulation during days 21-28 can provide substantial relief."
    elif total_count >= 1 or sum_score >= 10:
        tier = "Mild PMS"
        risk_level = "Mild"
        recommendation = "Common somatic and mild affective premenstrual symptoms. Hydration, herbal infusions, and light exercise are recommended."
    else:
        tier = "Sub-clinical / Minimal Premenstrual Disruption"
        risk_level = "Minimal"
        recommendation = "Your cycle indicates healthy hormonal baseline equanimity."
        
    return {
        "tier": tier,
        "risk_level": risk_level,
        "total_score": sum_score,
        "core_symptoms_count": core_count,
        "total_symptoms_count": total_count,
        "recommendation": recommendation,
        "timestamp": datetime.now().isoformat()
    }

def score_pcos_assessment(responses):
    """
    Evaluates Rotterdam criteria indicators for PCOS / PCOD.
    Features:
      1. Cycle irregularity (cycle length > 35 days, skipped periods)
      2. Androgenic signs (cystic acne, hirsutism, alopecia)
      3. Metabolic signs (weight resistance, sugar cravings, skin tags)
      4. Prior diagnostic ultrasound (polycystic ovarian appearance)
    """
    irregularity = int(responses.get('cycle_irregularity', 0))
    androgens = int(responses.get('androgen_signs', 0))
    metabolic = int(responses.get('metabolic_signs', 0))
    ultrasound = bool(responses.get('ultrasound_cysts', False))
    
    score = irregularity + androgens + metabolic + (3 if ultrasound else 0)
    
    if ultrasound or score >= 6:
        risk_level = "High Clinical Indication of PCOS/PCOD"
        summary = "Significant clinical markers for PCOS (hyperandrogenism and ovulatory dysfunction). Consultation with an endocrinologist or gynecologist for pelvic imaging and fasting insulin/lipid profiles is advised."
    elif score >= 3:
        risk_level = "Moderate Risk / Hormonal Imbalance"
        summary = "Moderate indicators present. Anti-inflammatory low-glycemic dietary protocols, inositol, and stress reduction can assist ovulatory regularity."
    else:
        risk_level = "Low Risk / Standard Baseline"
        summary = "Minimal markers for PCOS/PCOD. Continue healthy nutritional and sleep habits."
        
    return {
        "score": score,
        "risk_level": risk_level,
        "summary": summary,
        "timestamp": datetime.now().isoformat()
    }

def export_period_csv_buffer(cycles, profile_name="All"):
    """
    Generates a streamable RFC 4180 CSV export containing cycle records,
    diagnosed condition tags, pain score, flow intensity, and care notes.
    """
    output = io.StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)
    
    # Comprehensive Clinical Header
    writer.writerow([
        "Profile Name",
        "Relationship",
        "Cycle Start Date",
        "Cycle End Date",
        "Duration (Days)",
        "Diagnosed Conditions",
        "Pain Severity (1-10)",
        "Flow Intensity",
        "Logged Symptoms",
        "Clinical & Self-Care Notes",
        "Exported Timestamp"
    ])
    
    for row in cycles:
        # Expected tuple: start_date, end_date, notes, duration, profile_name, relation_tag, condition_tags, pain_score
        start_d = row[0].strftime('%Y-%m-%d') if hasattr(row[0], 'strftime') else str(row[0])
        end_d = row[1].strftime('%Y-%m-%d') if row[1] and hasattr(row[1], 'strftime') else (str(row[1]) if row[1] else "Ongoing / Active")
        duration = str(row[3]) if len(row) > 3 and row[3] is not None else "N/A"
        prof = row[4] if len(row) > 4 and row[4] else profile_name
        rel = row[5] if len(row) > 5 and row[5] else "Self"
        cond = row[6] if len(row) > 6 and row[6] else "None Reported"
        pain = str(row[7]) if len(row) > 7 and row[7] is not None else "Not Recorded"
        notes = row[2] if row[2] else ""
        
        writer.writerow([
            prof,
            rel,
            start_d,
            end_d,
            duration,
            cond,
            pain,
            "Logged in check-in",
            notes,
            notes,
            datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ])
        
    return output.getvalue()
