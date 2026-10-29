import pytest
from app import app
from services.period_service import (
    CONDITION_PROFILES,
    calculate_cycle_phase,
    score_pmdd_dsm5,
    score_pcos_assessment,
    export_period_csv_buffer
)

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret-key-421'
    with app.test_client() as client:
        yield client

def test_condition_profiles_structure():
    assert "PCOS" in CONDITION_PROFILES
    assert "PMDD" in CONDITION_PROFILES
    assert "PMS" in CONDITION_PROFILES
    assert "Endometriosis" in CONDITION_PROFILES
    assert len(CONDITION_PROFILES["PMDD"]["common_symptoms"]) >= 5
    assert "vedic_equanimity" in CONDITION_PROFILES["PMDD"]

def test_calculate_cycle_phase_stages():
    # Menstrual phase
    m_phase = calculate_cycle_phase(2, 28)
    assert m_phase["phase"] == "Menstrual Phase"
    assert "Winter" in m_phase["sub_phase"]
    assert "caregiver_tip" in m_phase

    # Follicular phase
    f_phase = calculate_cycle_phase(8, 28)
    assert f_phase["phase"] == "Follicular Phase"
    assert "Spring" in f_phase["sub_phase"]

    # Ovulatory phase
    o_phase = calculate_cycle_phase(14, 28)
    assert o_phase["phase"] == "Ovulatory Phase"
    assert "Summer" in o_phase["sub_phase"]

    # Early Luteal
    el_phase = calculate_cycle_phase(19, 28)
    assert el_phase["phase"] == "Early Luteal Phase"

    # Late Luteal (PMDD sensitivity window)
    ll_phase = calculate_cycle_phase(26, 28)
    assert ll_phase["phase"] == "Late Luteal Phase"
    assert "PMDD" in ll_phase["hormones"]

def test_score_pmdd_dsm5():
    # High clinical indication meeting DSM-5 criteria (>= 5 symptoms, >= 1 core)
    positive_pmdd_data = {
        'mood_swings': 3,
        'irritability_anger': 3,
        'depressed_hopeless': 3,
        'anxiety_tension': 3,
        'decreased_interest': 3,
        'concentration_diff': 3
    }
    res_pos = score_pmdd_dsm5(positive_pmdd_data)
    assert "Provisional PMDD" in res_pos["tier"]
    assert res_pos["core_symptoms_count"] >= 1
    assert res_pos["total_symptoms_count"] >= 5

    # Sub-clinical / minimal symptoms
    minimal_data = {'mood_swings': 0, 'irritability_anger': 1}
    res_min = score_pmdd_dsm5(minimal_data)
    assert res_min["risk_level"] == "Minimal"

def test_score_pcos_assessment():
    # High risk / ultrasound confirmed
    high_risk_data = {
        'cycle_irregularity': 3,
        'androgen_signs': 3,
        'metabolic_signs': 2,
        'ultrasound_cysts': True
    }
    res_high = score_pcos_assessment(high_risk_data)
    assert "High Clinical Indication" in res_high["risk_level"]

    # Low risk
    low_risk_data = {
        'cycle_irregularity': 0,
        'androgen_signs': 0,
        'metabolic_signs': 0,
        'ultrasound_cysts': False
    }
    res_low = score_pcos_assessment(low_risk_data)
    assert "Low Risk" in res_low["risk_level"]

def test_export_period_csv_buffer():
    from datetime import date
    sample_cycles = [
        (date(2026, 10, 1), date(2026, 10, 5), "Mild cramping", 4, "Maya", "Partner", "PCOS, Dysmenorrhea", 5)
    ]
    csv_text = export_period_csv_buffer(sample_cycles, profile_name="Maya")
    assert "Profile Name" in csv_text
    assert "Pain Severity" in csv_text
    assert "Maya" in csv_text
    assert "PCOS, Dysmenorrhea" in csv_text

def test_api_screener_pmdd_endpoint(client):
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['username'] = 'admin'
        sess['role'] = 'admin'

    payload = {
        'mood_swings': 4,
        'irritability_anger': 3,
        'depressed_hopeless': 3,
        'anxiety_tension': 3,
        'decreased_interest': 3,
        'concentration_diff': 3
    }
    res = client.post('/api/period/screener/pmdd', json=payload)
    assert res.status_code == 200
    json_data = res.get_json()
    assert json_data['success'] is True
    assert "Provisional PMDD" in json_data['assessment']['tier']

def test_api_screener_pcos_endpoint(client):
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['username'] = 'admin'
        sess['role'] = 'admin'

    payload = {
        'cycle_irregularity': 3,
        'androgen_signs': 3,
        'metabolic_signs': 2,
        'ultrasound_cysts': '1'
    }
    res = client.post('/api/period/screener/pcos', json=payload)
    assert res.status_code == 200
    json_data = res.get_json()
    assert json_data['success'] is True
    assert "High Clinical Indication" in json_data['assessment']['risk_level']

def test_period_page_rendering_with_phase_and_screeners(client):
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['username'] = 'admin'
        sess['role'] = 'admin'
        sess['gender'] = 'female'

    res = client.get('/period')
    assert res.status_code == 200
    assert b"Period Journal & Menstrual Wellness" in res.data
    assert b"PMDD Screener" in res.data
    assert b"PCOS Screener" in res.data
    assert b"Clinical Diagnostic Tags" in res.data
    assert b"Pain & Cramp Severity" in res.data

def test_404_error_page(client):
    res = client.get('/nonexistent_path_for_testing_404')
    assert res.status_code == 404
    assert b"404" in res.data
    assert b"The path has gently drifted away" in res.data

def test_period_cycle_edit_and_delete_endpoints(client):
    import database_setup
    conn = database_setup.get_db_connection()
    cur = conn.cursor()
    # Insert a temporary cycle for user_id=1
    cur.execute("""
        INSERT INTO period_cycles (user_id, start_date, notes, condition_tags, pain_score)
        VALUES (1, '2026-10-01', 'Initial test note', 'PMS', 3)
    """)
    conn.commit()
    cycle_id = cur.lastrowid
    cur.close()
    conn.close()

    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['username'] = 'admin'
        sess['role'] = 'admin'

    # Edit cycle
    edit_payload = {
        'start_date': '2026-10-01',
        'end_date': '2026-10-06',
        'notes': 'Updated symptoms with chamomile tea',
        'conditions': ['PCOS', 'PMS'],
        'pain_score': 5,
        'flow_texture': 'Standard Flow'
    }
    res_edit = client.post(f'/api/period/cycle/edit/{cycle_id}', data=edit_payload, follow_redirects=True)
    assert res_edit.status_code == 200

    # Verify database update
    conn = database_setup.get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT end_date, notes, condition_tags, pain_score FROM period_cycles WHERE id = %s", (cycle_id,))
    updated = cur.fetchone()
    assert str(updated[0]) == '2026-10-06'
    assert 'chamomile' in updated[1]
    assert 'PCOS' in updated[2]
    assert updated[3] == 5

    # Delete cycle
    res_del = client.post(f'/api/period/cycle/delete/{cycle_id}', follow_redirects=True)
    assert res_del.status_code == 200
    conn.commit()
    cur.execute("SELECT id FROM period_cycles WHERE id = %s", (cycle_id,))
    assert cur.fetchone() is None
    cur.close()
    conn.close()

def test_chahat_account_and_period_entries(client):
    import database_setup
    # Verify authentication with chahat & chahat
    pwd_hash = database_setup.hash_password("chahat", "chahat")
    conn = database_setup.get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, username, password FROM users WHERE username = 'chahat'")
    chahat = cur.fetchone()
    assert chahat is not None
    assert chahat[2] == pwd_hash

    # Verify period demo entries exist for chahat
    cur.execute("SELECT COUNT(*) FROM period_cycles WHERE user_id = %s", (chahat[0],))
    cycle_count = cur.fetchone()[0]
    assert cycle_count >= 3

    cur.execute("SELECT COUNT(*) FROM journal WHERE user_id = %s AND shlok = 'Period Journal Entry'", (chahat[0],))
    wellness_count = cur.fetchone()[0]
    assert wellness_count >= 2
    cur.close()
    conn.close()


