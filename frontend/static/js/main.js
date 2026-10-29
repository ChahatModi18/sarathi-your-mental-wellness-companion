/**
 * ==============================================================================
 * BhagvadMood / Sarathi Web Platform - Advanced Interactive Frontend Engine
 * ==============================================================================
 */

// Mobile Navigation Drawer Toggle
document.addEventListener('DOMContentLoaded', () => {
    const mobileBtn = document.getElementById('mobile-menu-btn');
    const sidebar = document.getElementById('app-sidebar');

    if (mobileBtn && sidebar) {
        mobileBtn.addEventListener('click', () => {
            sidebar.classList.toggle('open');
            const icon = mobileBtn.querySelector('i');
            if (sidebar.classList.contains('open')) {
                icon.className = 'fa-solid fa-xmark';
            } else {
                icon.className = 'fa-solid fa-bars';
            }
        });

        // Close sidebar on outside click on mobile
        document.addEventListener('click', (e) => {
            if (window.innerWidth <= 992 && sidebar.classList.contains('open')) {
                if (!sidebar.contains(e.target) && !mobileBtn.contains(e.target)) {
                    sidebar.classList.remove('open');
                    const icon = mobileBtn.querySelector('i');
                    if (icon) icon.className = 'fa-solid fa-bars';
                }
            }
        });
    }

    // Auto-dismiss alert banners
    const flashMessages = document.querySelectorAll('.alert');
    flashMessages.forEach((msg) => {
        setTimeout(() => {
            msg.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
            msg.style.opacity = '0';
            msg.style.transform = 'translateY(-10px)';
            setTimeout(() => msg.remove(), 600);
        }, 5000);
    });
});

/**
 * Web Speech Synthesis: Reads Shlokas and Cognitive Reframing aloud with a calm pace
 */
function speakWisdom(text, buttonElement) {
    if (!('speechSynthesis' in window)) {
        alert("Speech synthesis is not supported on this browser.");
        return;
    }

    if (window.speechSynthesis.speaking) {
        window.speechSynthesis.cancel();
        if (buttonElement) buttonElement.classList.remove('speaking');
        return;
    }

    const cleanText = text.replace(/[*#—]/g, '').trim();
    const utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.rate = 0.88; // Gentle, meditative pacing
    utterance.pitch = 1.0;

    // Pick best English voice if available
    const voices = window.speechSynthesis.getVoices();
    const preferredVoice = voices.find(v => v.lang.startsWith('en') && (v.name.includes('Natural') || v.name.includes('Google') || v.name.includes('Samantha')));
    if (preferredVoice) utterance.voice = preferredVoice;

    if (buttonElement) {
        buttonElement.classList.add('speaking');
        utterance.onend = () => buttonElement.classList.remove('speaking');
        utterance.onerror = () => buttonElement.classList.remove('speaking');
    }

    window.speechSynthesis.speak(utterance);
}

/**
 * Confetti celebration generator for Mindful Points achievements
 */
function triggerConfetti() {
    const colors = ['#8c52ff', '#00e676', '#ffea00', '#00b0ff', '#ff4081', '#ffffff'];
    for (let i = 0; i < 40; i++) {
        const particle = document.createElement('div');
        particle.className = 'confetti-particle';
        particle.style.left = Math.random() * window.innerWidth + 'px';
        particle.style.top = (window.scrollY + 10) + 'px';
        particle.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
        particle.style.borderRadius = Math.random() > 0.5 ? '50%' : '2px';
        particle.style.width = (Math.random() * 8 + 6) + 'px';
        particle.style.height = (Math.random() * 8 + 6) + 'px';
        document.body.appendChild(particle);

        setTimeout(() => particle.remove(), 2500);
    }
}

/**
 * Interactive 4-4-4-4 Square Breathing Coach Engine
 */
let breathingInterval = null;
let breathingPhase = 0; // 0: Inhale, 1: Hold, 2: Exhale, 3: Hold

function toggleBreathingCoach(show = true) {
    const modal = document.getElementById('breathing-coach-modal');
    if (!modal) return;

    if (show) {
        modal.classList.add('active');
        startBreathingCycle();
    } else {
        modal.classList.remove('active');
        if (breathingInterval) {
            clearInterval(breathingInterval);
            breathingInterval = null;
        }
    }
}

function startBreathingCycle() {
    const circle = document.getElementById('mandala-circle');
    const label = document.getElementById('mandala-label');
    const counter = document.getElementById('mandala-counter');
    if (!circle || !label || !counter) return;

    const phases = [
        { text: "Inhale Slowly...", cls: "inhale", duration: 4 },
        { text: "Hold Steadily...", cls: "hold", duration: 4 },
        { text: "Exhale Gently...", cls: "exhale", duration: 4 },
        { text: "Rest Equipoised...", cls: "hold", duration: 4 }
    ];

    breathingPhase = 0;
    let secondsLeft = phases[breathingPhase].duration;

    const updateDisplay = () => {
        const current = phases[breathingPhase];
        label.innerText = current.text;
        counter.innerText = secondsLeft;
        circle.className = 'breathing-circle ' + current.cls;

        if (secondsLeft <= 1) {
            breathingPhase = (breathingPhase + 1) % phases.length;
            secondsLeft = phases[breathingPhase].duration;
        } else {
            secondsLeft--;
        }
    };

    updateDisplay();
    if (breathingInterval) clearInterval(breathingInterval);
    breathingInterval = setInterval(updateDisplay, 1000);
}

/**
 * Mini-Goal Completion Dispatcher
 */
function completeMiniGoal(reward, goalDescription, buttonElement) {
    if (!buttonElement) return;
    buttonElement.disabled = true;
    buttonElement.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Claiming...';

    fetch('/api/complete-minigoal', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ reward: reward, goal: goalDescription })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            triggerConfetti();
            buttonElement.parentElement.innerHTML = `
                <div style="color:#b9ffd9; font-size:0.95rem; font-weight:600;">
                    <i class="fa-solid fa-circle-check"></i> ${data.message}
                </div>
            `;
            // Update sidebar stats
            const pointsStrong = document.querySelector('.stat-icon-points + span strong');
            if (pointsStrong) pointsStrong.innerText = data.total_points + ' MP';
        } else {
            alert(data.error || "Could not claim mini-goal points.");
            buttonElement.disabled = false;
        }
    })
    .catch(err => {
        console.error(err);
        buttonElement.disabled = false;
    });
}

/**
 * ==============================================================================
 * Daylight Theme & Theme Switcher Controller
 * DOM Daylight Project Standard
 * ==============================================================================
 */
window.currentActiveMood = null;

function getStoredTheme() {
    return localStorage.getItem('sarathi_theme') || 'daylight';
}

function updateThemeToggleUI(theme) {
    const icon = document.getElementById('themeToggleIcon');
    const txt = document.getElementById('themeToggleText');
    if (icon && txt) {
        if (theme === 'daylight') {
            icon.className = 'fa-solid fa-sun';
            txt.innerText = 'Daylight Mode';
        } else {
            icon.className = 'fa-solid fa-moon';
            txt.innerText = 'Midnight Mode';
        }
    }
}

function setSarathiTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('sarathi_theme', theme);
    updateThemeToggleUI(theme);
    if (window.currentActiveMood) {
        applyMoodAmbientTheme(window.currentActiveMood);
    } else {
        document.body.style.backgroundImage = '';
    }
}

function toggleSarathiTheme() {
    const current = document.documentElement.getAttribute('data-theme') || 'daylight';
    const next = (current === 'daylight') ? 'night' : 'daylight';
    setSarathiTheme(next);
}

// Immediately initialize theme on script load
(function() {
    const initialTheme = getStoredTheme();
    document.documentElement.setAttribute('data-theme', initialTheme);
})();

/**
 * ==============================================================================
 * Desktop Feature Parity: 30 Discrete Mood Ambient Shifters
 * Matches Tkinter Main.py MOOD_COLORS with Dual Daylight / Midnight Ambient Engines
 * ==============================================================================
 */
const DESKTOP_MOOD_COLORS = {
    "positive": { primary: "#FFD300", calm: "#AEE1F9", name: "Soft Sky Blue" },
    "very_happy": { primary: "#FF914D", calm: "#6BCBCE", name: "Cool Teal" },
    "negative": { primary: "#B23A48", calm: "#9BF6FF", name: "Seafoam Green" },
    "pessimistic": { primary: "#5A189A", calm: "#FEC89A", name: "Pastel Peach" },
    "optimistic": { primary: "#8FD694", calm: "#CDB4DB", name: "Lavender Mist" },
    "neutral": { primary: "#6C757D", calm: "#FFD56B", name: "Golden Glow" },
    "overwhelmed": { primary: "#D1495B", calm: "#C3B1E1", name: "Cool Lilac" },
    "anxious": { primary: "#7209B7", calm: "#FEC89A", name: "Soft Peach" },
    "peaceful": { primary: "#87CEEB", calm: "#FFD1BA", name: "Sunset Peach" },
    "restless": { primary: "#FF6F61", calm: "#A8E6CF", name: "Mint Green" },
    "very_sad": { primary: "#1D3557", calm: "#FF9B85", name: "Warm Coral" },
    "sad": { primary: "#457B9D", calm: "#FFB4A2", name: "Soft Coral Pink" },
    "discouraged": { primary: "#8D6E63", calm: "#B8F2E6", name: "Aqua Green" },
    "devastated": { primary: "#2B2D42", calm: "#F4A261", name: "Warm Amber" },
    "ecstatic": { primary: "#9D4EDD", calm: "#B5EAEA", name: "Powder Blue" },
    "content": { primary: "#A7C957", calm: "#F7A9A8", name: "Rose Quartz" },
    "angry": { primary: "#E63946", calm: "#90E0EF", name: "Cool Aqua" },
    "happy": { primary: "#FFCB77", calm: "#A0CED9", name: "Soft Blue" },
    "grateful": { primary: "#FF6F91", calm: "#A8E6CF", name: "Gentle Mint" },
    "hopeful": { primary: "#06D6A0", calm: "#CDB4DB", name: "Lavender Mist" },
    "lonely": { primary: "#3A86FF", calm: "#E2EAFC", name: "Pale Cloud" },
    "burned_out": { primary: "#6C757D", calm: "#E9D8A6", name: "Warm Sand" },
    "guilty": { primary: "#9D8189", calm: "#F4ACB7", name: "Blush Rose" },
    "insecure": { primary: "#5C677D", calm: "#D8E2DC", name: "Pearly Mist" },
    "confused": { primary: "#7B2CBF", calm: "#E0AAFF", name: "Mauve Mist" },
    "envious": { primary: "#2D6A4F", calm: "#D8F3DC", name: "Pale Mint" },
    "grief_stricken": { primary: "#1F2421", calm: "#DCE1DE", name: "Silver Sage" },
    "serene": { primary: "#48CAE4", calm: "#CAF0F8", name: "Crystal Blue" },
    "inspired": { primary: "#FFB703", calm: "#FFE6A7", name: "Golden Honey" },
    "resilient": { primary: "#588157", calm: "#DAD7CD", name: "Sage Earth" }
};

function applyMoodAmbientTheme(mood) {
    if (!mood) return;
    const moodKey = mood.toLowerCase().trim().replace(/\s+/g, '_');
    window.currentActiveMood = moodKey;

    const palette = DESKTOP_MOOD_COLORS[moodKey] || DESKTOP_MOOD_COLORS["neutral"];
    const currentTheme = document.documentElement.getAttribute('data-theme') || 'daylight';
    const isDaylight = (currentTheme === 'daylight' || currentTheme === 'amber');

    document.body.style.transition = 'background 1.2s cubic-bezier(0.4, 0, 0.2, 1), background-color 1.2s ease';

    if (isDaylight) {
        // Desktop parity: use calm soothing color as radiant base
        document.body.style.backgroundColor = palette.calm;
        document.body.style.backgroundImage = `radial-gradient(circle at 18% 18%, ${palette.calm} 0%, rgba(246, 244, 237, 0.78) 55%, #faf8f3 100%)`;
        document.documentElement.style.setProperty('--card-border', `${palette.primary}33`);
        document.documentElement.style.setProperty('--shadow-glow', `0 10px 30px ${palette.primary}18`);
    } else {
        // Midnight Mode: deep cosmic background with vibrant mood primary hue wash
        document.body.style.backgroundColor = '#0b081a';
        document.body.style.backgroundImage = `radial-gradient(circle at 20% 20%, ${palette.primary}2c 0%, rgba(15, 11, 36, 0.95) 60%, #0b081a 100%)`;
        document.documentElement.style.setProperty('--card-border', `${palette.primary}44`);
        document.documentElement.style.setProperty('--shadow-glow', `0 0 35px ${palette.primary}33`);
    }

    // Set dynamic mood accents
    document.documentElement.style.setProperty('--mood-current-primary', palette.primary);
    document.documentElement.style.setProperty('--mood-current-calm', palette.calm);

    // Show floating ambient indicator badge matching GUI desktop
    showMoodAmbientBadge(moodKey, palette);
}

function resetMoodAmbientTheme() {
    window.currentActiveMood = null;
    const currentTheme = document.documentElement.getAttribute('data-theme') || 'daylight';
    document.body.style.backgroundImage = '';
    document.body.style.backgroundColor = '';
    document.documentElement.style.removeProperty('--card-border');
    document.documentElement.style.removeProperty('--shadow-glow');
    document.documentElement.style.removeProperty('--mood-current-primary');
    document.documentElement.style.removeProperty('--mood-current-calm');

    const badge = document.getElementById('floatingMoodBadge');
    if (badge) badge.remove();
}

function showMoodAmbientBadge(moodKey, palette) {
    let badge = document.getElementById('floatingMoodBadge');
    if (!badge) {
        badge = document.createElement('div');
        badge.id = 'floatingMoodBadge';
        badge.style.position = 'fixed';
        badge.style.bottom = '24px';
        badge.style.right = '24px';
        badge.style.zIndex = '999';
        badge.style.background = 'var(--card-bg)';
        badge.style.border = '1px solid var(--card-border)';
        badge.style.boxShadow = '0 10px 30px rgba(0,0,0,0.12)';
        badge.style.borderRadius = '30px';
        badge.style.padding = '0.5rem 1.1rem';
        badge.style.display = 'flex';
        badge.style.alignItems = 'center';
        badge.style.gap = '0.75rem';
        badge.style.fontSize = '0.86rem';
        badge.style.fontWeight = '600';
        badge.style.color = 'var(--text-primary)';
        badge.style.backdropFilter = 'blur(12px)';
        badge.style.transition = 'all 0.3s ease';
        document.body.appendChild(badge);
    }

    const moodTitle = moodKey.replace(/_/g, ' ').toUpperCase();
    badge.innerHTML = `
        <span style="width:12px; height:12px; border-radius:50%; background:${palette.primary}; box-shadow:0 0 8px ${palette.primary}; flex-shrink:0;"></span>
        <span>Ambience: <strong style="color:var(--text-primary);">${moodTitle}</strong> <span style="opacity:0.75; font-size:0.78rem;">(${palette.name})</span></span>
        <button type="button" onclick="resetMoodAmbientTheme()" style="background:none; border:none; color:var(--text-muted); cursor:pointer; font-size:1.05rem; padding:0 2px; margin-left:4px;" title="Reset to standard background">
            <i class="fa-solid fa-xmark"></i>
        </button>
    `;
}


/**
 * ==============================================================================
 * Web Speech Recognition (Speech-to-Text Voice Input)
 * ==============================================================================
 */
function startVoiceDictation(targetInputId, micButtonId) {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
        alert("Voice recognition is not supported in this browser. Please use Chrome, Edge, or Safari.");
        return;
    }

    const targetInput = document.getElementById(targetInputId);
    const micBtn = document.getElementById(micButtonId);
    if (!targetInput) return;

    const recognition = new SpeechRecognition();
    recognition.lang = 'en-US';
    recognition.interimResults = false;
    recognition.continuous = false;

    if (micBtn) micBtn.classList.add('listening');

    recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        if (targetInput.value) {
            targetInput.value += " " + transcript;
        } else {
            targetInput.value = transcript;
        }
        if (micBtn) micBtn.classList.remove('listening');
    };

    recognition.onerror = () => {
        if (micBtn) micBtn.classList.remove('listening');
    };

    recognition.onend = () => {
        if (micBtn) micBtn.classList.remove('listening');
    };

    recognition.start();
}

/**
 * ==============================================================================
 * Agentic Conversational Voice Bot (Sarathi Voice Assistant)
 * ==============================================================================
 */
function initSarathiVoiceBot() {
    // Only show voicebot on authenticated application pages, not on login/register pages
    if (window.location.pathname === '/login' || window.location.pathname === '/register') return;
    if (document.getElementById('sarathi-voicebot-root')) return;

    const root = document.createElement('div');
    root.id = 'sarathi-voicebot-root';
    root.innerHTML = `
        <div class="voicebot-floating-trigger" id="sarathiTrigger" onclick="toggleVoiceBotDrawer()">
            <span class="voicebot-pulse-dot"></span>
            <i class="fa-solid fa-headset" style="font-size:1.1rem;"></i>
            <span>Talk to Sarathi AI</span>
        </div>

        <div class="voicebot-drawer" id="sarathiDrawer">
            <div class="voicebot-header">
                <div style="display:flex; align-items:center; gap:0.6rem;">
                    <i class="fa-solid fa-dharmachakra" style="color:#ffd700; font-size:1.3rem;"></i>
                    <div>
                        <strong style="color:white; font-size:0.95rem; display:block;">Sarathi Mindful Voice Bot</strong>
                        <span style="font-size:0.75rem; color:#00e676;"><i class="fa-solid fa-circle" style="font-size:0.5rem;"></i> Active &bull; Vedic Reframing AI</span>
                    </div>
                </div>
                <button onclick="toggleVoiceBotDrawer()" style="background:none; border:none; color:var(--text-secondary); cursor:pointer; font-size:1.1rem;">
                    <i class="fa-solid fa-xmark"></i>
                </button>
            </div>

            <div class="voicebot-messages" id="voicebotMessages">
                <div class="voicebot-msg bot">
                    Namaste! I am Sarathi, your empathetic AI companion. Speak or type whatever is on your heart—I am here to listen, validate, and gently reframe.
                </div>
            </div>

            <div class="voicebot-chips">
                <span class="voicebot-chip" onclick="sendQuickPrompt('I feel anxious about an exam deadline')">📚 Exam Anxiety</span>
                <span class="voicebot-chip" onclick="sendQuickPrompt('I feel exhausted from work burnout')">💼 Work Burnout</span>
                <span class="voicebot-chip" onclick="sendQuickPrompt('I feel down and lonely today')">🫂 Feeling Down</span>
                <span class="voicebot-chip" onclick="toggleBreathingCoach(true)">🌬️ Breathing Pause</span>
            </div>

            <div class="voicebot-input-bar">
                <button type="button" class="voicebot-mic-btn" id="voicebotMicBtn" onclick="startVoiceDictation('voicebotInput', 'voicebotMicBtn')" title="Click to speak (Voice Input)">
                    <i class="fa-solid fa-microphone"></i>
                </button>
                <input type="text" id="voicebotInput" placeholder="Speak or type your reflection..." style="flex:1; background:rgba(255,255,255,0.06); border:1px solid rgba(255,255,255,0.12); border-radius:20px; padding:0.6rem 1rem; color:white; font-size:0.9rem;" onkeydown="if(event.key==='Enter') sendVoiceBotMessage()">
                <button type="button" class="btn" style="padding:0.6rem 0.9rem; border-radius:50%; width:40px; height:40px; display:flex; align-items:center; justify-content:center;" onclick="sendVoiceBotMessage()">
                    <i class="fa-solid fa-paper-plane" style="font-size:0.85rem;"></i>
                </button>
            </div>
        </div>
    `;
    document.body.appendChild(root);
}

function toggleVoiceBotDrawer() {
    const drawer = document.getElementById('sarathiDrawer');
    if (drawer) drawer.classList.toggle('active');
}

function sendQuickPrompt(promptText) {
    const input = document.getElementById('voicebotInput');
    if (input) {
        input.value = promptText;
        sendVoiceBotMessage();
    }
}

function sendVoiceBotMessage() {
    const input = document.getElementById('voicebotInput');
    const msgBox = document.getElementById('voicebotMessages');
    if (!input || !msgBox) return;

    const userText = input.value.trim();
    if (!userText) return;

    const userMsg = document.createElement('div');
    userMsg.className = 'voicebot-msg user';
    userMsg.innerText = userText;
    msgBox.appendChild(userMsg);
    input.value = '';
    msgBox.scrollTop = msgBox.scrollHeight;

    const typingIndicator = document.createElement('div');
    typingIndicator.className = 'voicebot-msg bot';
    typingIndicator.id = 'botTyping';
    typingIndicator.innerHTML = '<i class="fa-solid fa-ellipsis fa-fade"></i> Reflecting with wisdom...';
    msgBox.appendChild(typingIndicator);
    msgBox.scrollTop = msgBox.scrollHeight;

    fetch('/api/sentiment', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: userText })
    })
    .then(res => res.json())
    .then(data => {
        typingIndicator.remove();
        applyMoodAmbientTheme(data.mood);

        const botReply = document.createElement('div');
        botReply.className = 'voicebot-msg bot';
        
        let responseHTML = '';
        if (data.is_crisis) {
            responseHTML = `
                <div style="color:#ff8a80; font-weight:700; margin-bottom:0.4rem;">
                    <i class="fa-solid fa-triangle-exclamation"></i> Immediate Compassionate Support
                </div>
                <p style="margin:0 0 0.6rem 0;">You are never alone. Please reach out to Tele-MANAS at <strong>14416</strong> or call <strong>112</strong> immediately.</p>
            `;
        } else {
            const cleanReframing = (data.reframing || 'Take a slow, deep breath in this moment.').replace(/'/g, "&#39;");
            const cleanMeaning = (data.shlok_meaning || '').replace(/'/g, "&#39;");
            const cleanAffirmation = (data.affirmation || '').replace(/'/g, "&#39;");

            responseHTML = `
                <div style="font-size:0.8rem; color:#ffd700; font-weight:700; text-transform:uppercase; margin-bottom:0.3rem;">
                    ${data.context || 'Reflection'} &bull; ${data.mood}
                </div>
                <p style="margin:0 0 0.6rem 0;">${data.reframing || 'Take a slow, deep breath in this moment.'}</p>
                <div style="background:rgba(255,255,255,0.04); border-left:3px solid #8c52ff; padding:0.5rem 0.8rem; border-radius:0 8px 8px 0; margin-bottom:0.5rem;">
                    <div style="font-size:0.95rem; color:#f7d794; font-weight:700;">${data.shlok}</div>
                    <div style="font-size:0.85rem; color:#ccc; margin-top:0.2rem;">${data.shlok_meaning}</div>
                </div>
                ${data.affirmation ? `<div style="font-size:0.85rem; color:#a5d6a7; font-style:italic;">💡 "${data.affirmation}"</div>` : ''}
                <div style="margin-top:0.6rem; display:flex; justify-content:flex-end;">
                    <button class="audio-btn" onclick="speakWisdom('${cleanMeaning}. Affirmation: ${cleanAffirmation}', this)" title="Listen to Voice Response">
                        <i class="fa-solid fa-volume-high"></i>
                    </button>
                </div>
            `;
        }

        botReply.innerHTML = responseHTML;
        msgBox.appendChild(botReply);
        msgBox.scrollTop = msgBox.scrollHeight;

        if (!data.is_crisis && data.shlok_meaning) {
            const speechText = (data.affirmation ? data.affirmation + ". " : "") + data.shlok_meaning;
            speakWisdom(speechText, null);
        }
    })
    .catch(err => {
        typingIndicator.remove();
        const errReply = document.createElement('div');
        errReply.className = 'voicebot-msg bot';
        errReply.innerText = "Take a gentle breath. I am with you; please share your thought again.";
        msgBox.appendChild(errReply);
    });
}

document.addEventListener('DOMContentLoaded', () => {
    initSarathiVoiceBot();
    updateThemeToggleUI(getStoredTheme());
});

/**
 * ==============================================================================
 * Daylight Live Local Clock Widget Engine (From User-Uploaded Interface)
 * ==============================================================================
 */
function updateDaylightClock() {
    const timeElem = document.getElementById('daylightClockTime');
    const dateElem = document.getElementById('daylightClockDate');
    const statusTextElem = document.getElementById('daylightClockStatusText');
    const dotElem = document.getElementById('daylightClockDot');

    if (!timeElem && !dateElem) return;

    const now = new Date();
    
    // Format Time: e.g. "10:18:56 pm"
    let hours = now.getHours();
    const minutes = String(now.getMinutes()).padStart(2, '0');
    const seconds = String(now.getSeconds()).padStart(2, '0');
    const ampm = hours >= 12 ? 'pm' : 'am';
    hours = hours % 12;
    hours = hours ? hours : 12; // '0' becomes '12'
    const timeStr = `${hours}:${minutes}:${seconds} ${ampm}`;

    // Format Date: e.g. "Tuesday, 27 October 2026"
    const options = { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' };
    const dateStr = now.toLocaleDateString('en-GB', options);

    if (timeElem) timeElem.innerText = timeStr;
    if (dateElem) dateElem.innerText = dateStr;

    // Time-based Mindfulness Message & Amber/Green status dot
    const rawHour = now.getHours();
    let statusMsg = "Let the day soften into evening.";
    let dotColor = "#f59e0b"; // warm amber

    if (rawHour >= 5 && rawHour < 12) {
        statusMsg = "Welcome the morning stillness with gratitude.";
        dotColor = "#10b981"; // emerald
    } else if (rawHour >= 12 && rawHour < 17) {
        statusMsg = "Walk through the afternoon with steady focus.";
        dotColor = "#3b82f6"; // blue
    } else if (rawHour >= 17 && rawHour < 22) {
        statusMsg = "Let the day soften into evening.";
        dotColor = "#f59e0b"; // amber from daylight image
    } else {
        statusMsg = "Rest peacefully; release all effort into the night.";
        dotColor = "#8b5cf6"; // soft purple
    }

    if (statusTextElem) statusTextElem.innerText = statusMsg;
    if (dotElem) dotElem.style.background = dotColor;
}

setInterval(updateDaylightClock, 1000);

/**
 * ==============================================================================
 * Community Thought Banner Carousel (Exact match for Chahat Modi banner in image)
 * ==============================================================================
 */
const COMMUNITY_THOUGHTS = [
    { quote: "“Be happy, keep smiling.”", author: "— Chahat Modi" },
    { quote: "“You have a right to your actions, never to their fruits. Keep your heart tranquil.”", author: "— Bhagavad Gita 2.47" },
    { quote: "“Peace comes from within. Do not seek it without.”", author: "— Gautama Buddha" },
    { quote: "“When the mind is equipoised, all sorrows dissolve naturally.”", author: "— Bhagavad Gita 2.65" }
];
let currentThoughtIndex = 0;

function renderCommunityThought() {
    const quoteElem = document.getElementById('thoughtQuote');
    const authorElem = document.getElementById('thoughtAuthor');
    const counterElem = document.getElementById('thoughtCounter');

    if (!quoteElem) return;

    const thought = COMMUNITY_THOUGHTS[currentThoughtIndex];
    quoteElem.style.opacity = '0';
    quoteElem.style.transform = 'translateY(4px)';

    setTimeout(() => {
        quoteElem.innerText = thought.quote;
        if (authorElem) authorElem.innerText = thought.author;
        if (counterElem) counterElem.innerText = `${currentThoughtIndex + 1} of ${COMMUNITY_THOUGHTS.length}`;
        quoteElem.style.transition = 'opacity 0.25s ease, transform 0.25s ease';
        quoteElem.style.opacity = '1';
        quoteElem.style.transform = 'translateY(0)';
    }, 150);
}

function nextCommunityThought() {
    currentThoughtIndex = (currentThoughtIndex + 1) % COMMUNITY_THOUGHTS.length;
    renderCommunityThought();
}

function prevCommunityThought() {
    currentThoughtIndex = (currentThoughtIndex - 1 + COMMUNITY_THOUGHTS.length) % COMMUNITY_THOUGHTS.length;
    renderCommunityThought();
}

/**
 * ==============================================================================
 * Enhanced Multi-Theme Dropdown Toggle
 * ==============================================================================
 */
function toggleThemeDropdown(event) {
    if (event) event.stopPropagation();
    const menu = document.getElementById('themeDropdownMenu');
    if (menu) menu.classList.toggle('show');
}

// Close theme dropdown on outside click
document.addEventListener('click', (e) => {
    const menu = document.getElementById('themeDropdownMenu');
    const btn = document.getElementById('themeToggleBtn');
    if (menu && menu.classList.contains('show')) {
        if (!menu.contains(e.target) && (!btn || !btn.contains(e.target))) {
            menu.classList.remove('show');
        }
    }
});

// Update Theme Selector UI
function updateThemeToggleUI(theme) {
    const icon = document.getElementById('themeToggleIcon');
    const txt = document.getElementById('themeToggleText');
    const items = document.querySelectorAll('.theme-option-item');

    items.forEach(item => {
        if (item.getAttribute('data-theme-val') === theme) {
            item.classList.add('active');
        } else {
            item.classList.remove('active');
        }
    });

    if (icon && txt) {
        if (theme === 'daylight') {
            icon.className = 'fa-solid fa-sun';
            txt.innerText = 'Daylight (Sage)';
        } else if (theme === 'amber') {
            icon.className = 'fa-solid fa-mountain-sun';
            txt.innerText = 'Warm Amber';
        } else {
            icon.className = 'fa-solid fa-moon';
            txt.innerText = 'Dark mode';
        }
    }
}

/**
 * ==============================================================================
 * Period Journal Dynamic Shloka Wisdom & Mood Chips
 * ==============================================================================
 */
const PERIOD_SHLOKAS = {
    "peaceful": { verse: "BG 2.70: 'Like the ocean that remains calm as rivers enter it, the wise remain peaceful amidst all changes.'", meaning: "Your body is naturally harmonizing. Honor its resting tide." },
    "content": { verse: "BG 2.65: 'With clarity and contentment of mind, all physical discomfort softens.'", meaning: "Accept today's pace without needing to rush." },
    "calm": { verse: "BG 6.19: 'As a lamp in a windless place flickers not, so does the steady heart remain serene.'", meaning: "Breathe into steady stillness." },
    "anxious": { verse: "BG 2.47: 'Your duty is to the action of self-care, not anxious preoccupation with tomorrow.'", meaning: "Sip warm tea and allow tension to flow out." },
    "restless": { verse: "BG 6.26: 'From wherever the unsteady mind wanders, gently lead it back to inner tranquility.'", meaning: "Restlessness during menstrual cycles is natural biology; ground your feet." },
    "overwhelmed": { verse: "BG 18.66: 'Surrender all exhausting burdens; do not grieve, for grace carries you.'", meaning: "Give yourself permission to pause tasks today." },
    "sad": { verse: "BG 2.14: 'Sensations of pleasure and pain come and go like seasons. Endure them with gentle wisdom.'", meaning: "Emotional release during cycles cleanses the spirit." },
    "burned_out": { verse: "BG 6.16: 'Yoga is not for one who exerts excessively, nor one who deprives oneself of rest.'", meaning: "Restorative sleep is sacred medicine." },
    "happy": { verse: "BG 5.24: 'One whose happiness is within, whose delight is within, attains spiritual bliss.'", meaning: "Celebrate vitality and ease." },
    "grateful": { verse: "BG 9.26: 'Whatever is offered with love and devotion—even a single leaf—is received with joy.'", meaning: "Give thanks to your resilient body." },
    "serene": { verse: "BG 2.71: 'Attaining desireless peace, free from false ownership, one reaches tranquil quietude.'", meaning: "Enjoy the stillness of this moment." },
    "lonely": { verse: "BG 6.30: 'For one who sees the Divine everywhere and in all beings, they are never alone.'", meaning: "The universe breathes with you in every heartbeat." },
    "angry": { verse: "BG 2.63: 'From anger comes delusion; from calm discrimination comes mastery.'", meaning: "Exhale sharply, relax your jaw, and let heat dissolve." },
    "resilient": { verse: "BG 2.20: 'The soul is never born nor dies; it is eternal and unshaken.'", meaning: "You have weathered every cycle before and flourish again." },
    "hopeful": { verse: "BG 4.38: 'There is nothing so sublime and purifying as sacred self-knowledge in this world.'", meaning: "Tomorrow brings a renewed energetic phase." }
};

function toggleMoodTag(labelElement, mood) {
    const chk = labelElement.querySelector('input');
    if (!chk) return;
    
    chk.checked = !chk.checked;
    if (chk.checked) {
        labelElement.classList.add('active');
    } else {
        labelElement.classList.remove('active');
    }

    // Dynamic Shloka update
    const shlokData = PERIOD_SHLOKAS[mood];
    if (shlokData) {
        const textElem = document.getElementById('periodShlokText');
        const meaningElem = document.getElementById('periodShlokMeaning');
        if (textElem && meaningElem) {
            textElem.innerText = shlokData.verse;
            meaningElem.innerText = shlokData.meaning;
        }
    }
}

/**
 * ==============================================================================
 * Peer Support Forum Live Instant Filtering
 * ==============================================================================
 */
function filterPostsLive() {
    const input = document.getElementById('forumSearchInput');
    if (!input) return;
    const query = input.value.toLowerCase().trim();
    const cards = document.querySelectorAll('.thread-card');

    cards.forEach(card => {
        const title = card.querySelector('h3') ? card.querySelector('h3').innerText.toLowerCase() : '';
        const body = card.querySelector('p') ? card.querySelector('p').innerText.toLowerCase() : '';
        const cat = card.querySelector('.tag-category') ? card.querySelector('.tag-category').innerText.toLowerCase() : '';

        if (!query || title.includes(query) || body.includes(query) || cat.includes(query)) {
            card.style.display = 'block';
        } else {
            card.style.display = 'none';
        }
    });
}

function toggleForm() {
    const card = document.getElementById('post-form-card');
    if (card) {
        card.style.display = (card.style.display === 'none' || !card.style.display) ? 'block' : 'none';
    }
}

/**
 * ==============================================================================
 * Simple Admin Dashboard Search Filter
 * ==============================================================================
 */
function filterAdminTable(tableId, query) {
    const table = document.getElementById(tableId);
    if (!table) return;
    const q = query.toLowerCase().trim();
    const rows = table.querySelectorAll('tbody tr');

    rows.forEach(row => {
        const text = row.innerText.toLowerCase();
        row.style.display = (!q || text.includes(q)) ? '' : 'none';
    });
}
