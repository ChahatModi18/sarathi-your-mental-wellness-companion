# Design Specifications Document (DESIGN.md) — BhagvadMood Journal

> **Document Version:** 2.1.0  
> **Target Platforms:** Tkinter (Desktop 1200x800) & Responsive Web (HTML5/CSS3/JavaScript)  
> **Visual Identity:** Holistic Mindful Tech with Vedic Equanimity Accents & Natural Daylight Aesthetics

---

## 1. Design Philosophy & Aesthetic Principles

BhagvadMood Journal marries modern mindful computing with grounding Vedic motifs. The interface minimizes cognitive friction, sensory overload, and visual clutter to foster a soothing, judgment-free environment for users in emotional vulnerability.

### Core Tenets:
1. **Calm Affirmation (Natural Daylight & Visual Grounding):** Avoiding abrupt saturated flashes; offering a bright, tranquil Daylight Sage theme alongside warm amber and deep cosmic midnight themes.
2. **Cognitive Clarity:** Strict information hierarchy separating introspective journaling, quantitative metrics, and clinical interventions.
3. **Adaptive Emotion Biofeedback:** Dynamic background illumination reflecting the user's emotional state in real time without causing anxiety or alarm.
4. **Universal Accessibility:** WCAG AA contrast standards across all light and dark palettes ensuring legible text in all lighting conditions.

---

## 2. Tri-Theme Color System

The platform features an integrated Tri-Theme visual engine switchable via the universal header selector:

### 2.1 Theme Palette Matrix

| Token Name | Daylight (Sage Natural) | Warm Amber | Midnight Cosmic | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| `--bg-color` | `#f7f9f6` | `#faf6f0` | `#0b081a` | Base canvas background |
| `--bg-page` | `#f2f5f1` | `#f5efe6` | `#0f0b24` | Page viewport background |
| `--card-bg` | `rgba(255, 255, 255, 0.94)` | `rgba(255, 255, 255, 0.92)` | `rgba(23, 18, 56, 0.72)` | Card and panel fill |
| `--card-border` | `rgba(40, 75, 63, 0.14)` | `rgba(180, 83, 9, 0.16)` | `rgba(255, 255, 255, 0.10)` | Card border highlight |
| `--text-primary` | `#1e3329` | `#292524` | `#f1f0fb` | High-contrast main headings |
| `--text-secondary` | `#334a3e` | `#57534e` | `#c9c5f0` | Subtitles and labels |
| `--text-muted` | `#546c60` | `#78716c` | `#9f99d6` | Metadata and hints |
| `--accent-primary` | `#284b3f` | `#b45309` | `#8c52ff` | Primary CTA buttons & active state |
| `--accent-hover` | `#1e382f` | `#92400e` | `#7a3ee6` | Button hover and active state |
| `--accent-sage-light` | `#e5ede7` | `#fef3c7` | `rgba(140, 82, 255, 0.15)` | Feature pill icons & badges |

---

## 3. Dynamic 30-Mood Emotion Engine (Desktop GUI Parity)

Identical to the Desktop Tkinter GUI (`Main.py`), the web client dynamically alters the ambient background glow whenever a user enters or analyzes a journal reflection.

### 3.1 Emotion Color Taxonomy

| Emotion / Mood | Hex Code | Psychological Association |
| :--- | :--- | :--- |
| `ecstatic` | `#fef08a` | Radiance, exuberant joy, golden optimism |
| `very_happy` | `#fde047` | Luminous warmth, vibrant happiness |
| `happy` | `#86efac` | Fresh growth, gentle flourishing joy |
| `content` | `#bbf7d0` | Restful balance, satisfaction |
| `peaceful` | `#93c5fd` | Sky-blue stillness, tranquility |
| `serene` | `#a7f3d0` | Deep calm, inner harmony |
| `inspired` | `#f472b6` | Creative spark, elevated wonder |
| `hopeful` | `#6ee7b7` | Gentle renewal, future faith |
| `grateful` | `#fed7aa` | Heart-centered warmth, appreciation |
| `resilient` | `#cbd5e1` | Grounded steadfastness, endurance |
| `optimistic` | `#a3e635` | Sunny forward momentum |
| `positive` | `#86efac` | General uplifting affect |
| `neutral` | `#e2e8f0` | Centered baseline equanimity |
| `anxious` | `#fed7aa` | High cognitive arousal, nervous tension |
| `restless` | `#fed7aa` | Unsettled agitation, seeking grounding |
| `overwhelmed` | `#fca5a5` | Heavy sensory overload, emotional burden |
| `burned_out` | `#e2e8f0` | Depleted cognitive energy, exhaustion |
| `lonely` | `#c7d2fe` | Isolated yearning, soft solitude |
| `insecure` | `#fbcfe8` | Self-doubt, vulnerable affect |
| `confused` | `#e9d5ff` | Mental fog, uncertainty |
| `envious` | `#fef08a` | Comparative discontent |
| `guilty` | `#cbd5e1` | Internal friction, regret |
| `sad` | `#bae6fd` | Soft melancholy, quiet sorrow |
| `very_sad` | `#93c5fd` | Deep sorrow, emotional grief |
| `discouraged` | `#cbd5e1` | Dampened resolve, loss of heart |
| `pessimistic` | `#cbd5e1` | Heavy outlook, negative expectation |
| `angry` | `#fca5a5` | Fiery irritation, reactive boundary |
| `grief_stricken` | `#94a3b8` | Profound bereavement, mourning |
| `devastated` | `#0f172a` | Deep emotional shock, acute pain |
| `crisis` | `#ef4444` | High-priority safety alert |

### 3.2 Web Ambient Glow Implementation
The ambient emotion background is rendered via a dedicated `#mood-ambient-glow` DOM element positioned behind page content:
```css
#mood-ambient-glow {
    position: fixed;
    top: 0; left: 0; width: 100vw; height: 100vh;
    pointer-events: none;
    z-index: 0;
    opacity: 0.28;
    transition: background 1.2s cubic-bezier(0.4, 0, 0.2, 1), opacity 0.8s ease;
}
```
When `applyMoodTheme(mood)` is invoked via `main.js`, it updates:
```javascript
glow.style.background = `radial-gradient(circle at 50% 30%, ${color} 0%, transparent 70%)`;
```

---

## 4. Typography Hierarchy

- **Primary Serif (Wisdom & Headlines):** `Newsreader` / `Playfair Display` / `Georgia`  
  - H1: 34px / 2.2rem Semi-Bold (`var(--text-primary)`) — Page banners, welcoming headers
  - H2: 24px / 1.5rem Semi-Bold (`var(--text-primary)`) — Section titles, screening cards
  - H3: 18px / 1.15rem Medium (`var(--text-secondary)`) — Widget titles, metrics counters
- **Body & Reflective Text:** `Plus Jakarta Sans` / `Inter` / `system-ui`  
  - Body Regular: 15px / 0.95rem Regular (`var(--text-secondary)`) — Journal textareas, forum comments
  - Meta / Caption: 12px / 0.8rem Semi-Bold (`var(--text-muted)`) — Timestamps, badges, helpline footnotes
- **Vedic Wisdom Quotes & Sanskrit Shlokas:**  
  - Sanskrit Script: 18px Bold (`var(--accent-primary)`)
  - English Commentary: 14px Italic (`var(--text-secondary)`)

---

## 5. Component Design & Layout Systems

### 5.1 Desktop (Tkinter Frame Architecture)
The desktop application encapsulates 27 distinct frames within a centralized grid-swapping container (`SarathiApp` inheriting from `tk.Tk`):

```
+--------------------------------------------------------------------------+
|  Top Brand & Nav Header (Logo, Mindful Points, Streak Badge, Logout)    |
+-------------------+------------------------------------------------------+
|                   |                                                      |
|   Sidebar Nav     |             Active Frame Container                   |
|   - Chat & Journal|   (Dynamic switching via app.show_frame)             |
|   - Screenings    |                                                      |
|   - Counselor     |   - Modern ScrolledText for reflections              |
|   - Peer Forum    |   - Matplotlib FigureCanvasTkAgg for charts          |
|   - Resources     |   - Treeview with custom ttk styles for tables       |
|   - Cycle Tracker |   - Animated Canvas for Spin the Wheel               |
|   - To-Do Notes   |                                                      |
|                   |                                                      |
+-------------------+------------------------------------------------------+
|  Crisis Emergency Footer Strip (Tele-MANAS: 14416 | KIRAN: 1800-599-0019)|
+--------------------------------------------------------------------------+
```

### 5.2 Responsive Web Layout
- **Navigation:** Persistent glassmorphism sidebar (collapsible on mobile screens $\le 900\text{px}$).
- **Voicebot Drawer:** Floating toggle `#sarathiVoiceTrigger` mounting a slide-in mindful drawer `#sarathiDrawer` (strictly excluded on `/login` and `/register`).
- **Period Journal View:** Dual-column responsive layout featuring historical cycle calendar on the left and symptom logging/predictive analysis on the right.
- **Enterprise Admin Console:** Tabbed container with persistent state (`sessionStorage`) and real-time live search filter bars.
