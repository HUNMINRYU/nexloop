"""
Google Veo 3.1 Prompt Templates & Protocols
"""

# System Instructions for Gemini to act as Prompt Engineer
VEO_SYSTEM_PROMPT = """
### 🤖 Role & Persona
You are a **Google Veo 3.1 Expert Video Prompt Engineer**.
Your goal is to design the optimal structure for Veo 3.1 to generate safe, high-quality videos without refusal.

### ⚠️ Critical Safety & Stability Rules
1. **Generic Subjects:** NEVER use specific celebrity names, real people's names, or specific trademark names (Nike, iPhone, etc.) in visual descriptions. Generalize them (e.g., 'A generic smartphone', 'A man', 'A professional athlete').
2. **Safe Content:** NO violence, sexual content, or hate speech.
3. **Language Protocol:**
   - **Video Descriptions:** MUST be in **English**.
   - **Dialogue/Text:** Keep user's requested language.

### ✅ Safety Checklist (must pass before output)
- No real person names or identifiable public figures
- No explicit brands, logos, or trademarked products
- No sexual, NSFW, or exploitative content
- No graphic violence, gore, or hate content
- Avoid minors in unsafe contexts
### 📝 Output Format
You must output a structured prompt following the templates below.
Do not explain your reasoning, just provide the final prompt text ready for Veo.
"""

# Option 1: Dual Phase (Extension)
TEMPLATE_DUAL_PHASE = """
# Phase 1: The Core Action (0s-8s)
1. **Scene:** {scene}
2. **Subject:** {subject}
3. **Talent/POV:** {pov}
4. **Shot/Motion:** 9:16 Vertical. {motion}
5. **Action Breakdown:**
   - 0-2s (Hook): {action_hook}
   - 2-5s (Process): {action_process}
   - 5-8s (Peak): {action_peak}
6. **Composition:** Center Focus (Safe Zone optimized)
7. **Lighting:** {lighting}
8. **Style:** {style}, 4k, High Fidelity
9. **Sound:** {sound}
10. **Voice-over:** "{voice_over}"
11. **Negative Prompt:** text, watermark, bad quality, morphing.

# Phase 2: The Brand Stamp (Extension: 8s-12s)
*Init Image: Last frame of Phase 1*
1. **Action:** Freeze frame aesthetic. Subtle light leaks.
2. **Subject:** Product Hero Shot (Static).
3. **Camera:** Static / Slow Zoom In.
4. **Voice-over:** "{brand_voice_over}"
5. **Text Overlay:** "{brand_text}"
"""

# Option 2: Single Phase (Standard)
TEMPLATE_SINGLE_PHASE = """
# Single Phase: The Complete Shot (0s-8s)
1. **Scene:** {scene}
2. **Subject:** {subject}
3. **Talent/POV:** {pov}
4. **Shot/Motion:** 9:16 Vertical. {motion}
5. **Action Breakdown:**
   - 0-4s: {action_start}
   - 4-8s: {action_end}
6. **Composition:** Center Focus
7. **Lighting:** {lighting}
8. **Style:** {style}, Photorealistic
9. **Sound:** {sound}
10. **Voice-over:** "{voice_over}"
11. **Negative Prompt:** text, subtitles, watermark, specific logos, blurry, distorted, morphing.
"""


class VeoTemplateManager:
    """Veo 프롬프트 템플릿 관리자"""

    @staticmethod
    def get_system_prompt() -> str:
        return VEO_SYSTEM_PROMPT

    @staticmethod
    def get_template(mode: str = "single") -> str:
        if mode == "dual":
            return TEMPLATE_DUAL_PHASE
        return TEMPLATE_SINGLE_PHASE
