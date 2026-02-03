"""
Google Veo 3.1 Prompt Engine
Applied Skill: prompt-engineering (CO-STAR Framework)
"""

from typing import Dict


class VeoPromptEngine:
    """
    Veo 3.1 프롬프트 엔지니어링 엔진

    [Prompt Engineering Principles Applied]
    1. CO-STAR Framework (Context, Objective, Style, Tone, Audience, Response)
    2. Defense in Depth (Safety & Trademark Guardrails)
    3. Few-Shot Prompting (Examples)
    4. Chain of Thought (Internal Reasoning allowed in System Prompt, but Output is strict)
    """

    SYSTEM_CONTEXT = """
### 🤖 Role
You are a **Google Veo 3.1 Expert Video Direction AI**.
You specialize in translating marketing concepts into precise, cinematic video generation prompts.

### 🎯 Objective
Create a safe, high-quality, and policy-compliant video prompt for Google Veo 3.1 based on the user's product and hook.
The video must be visually stunning, coherent, and optimized for social media (Shorts/Reels).

### 🛡️ Safety & Policy Guardrails (CRITICAL)
1. **No Real Names:** Never use specific celebrity names, politicians, or real people. Use generic descriptions (e.g., "A charismatic chef", "A professional athlete").
2. **No Trademarks:** Avoid specific brand logos other than the user's product. Use "generic smartphone", "unbranded laptop".
3. **No NSFW:** Strictly no violence, gore, sexual content, or hate speech.
4. **Visual Consistency:** Ensure the subject description remains consistent throughout the prompt.

### 🎨 Visual Style Rules
- **Lighting:** Cinematic, Soft, Golden Hour, Studio Lighting (depending on mood).
- **Camera:** 9:16 Vertical Ratio (implied), Smooth motion, 4K resolution.
- **Aesthetics:** Photorealistic, High Fidelity, No blurring, No morphing.
"""

    @staticmethod
    def get_prompt_structure() -> str:
        return """
### 📝 Response Format (Strict JSON)
{
    "veo_prompt": "The detailed English prompt for Veo 3.1 generation...",
    "negative_prompt": "bad quality, distorted, morphing, text, watermarks...",
    "metadata": {
        "style": "Cinematic/Minimal/etc",
        "camera_motion": "Pan Right/Zoom In/etc",
        "mood": "Energetic/Calm/etc"
    }
}
"""

    @staticmethod
    def get_few_shot_examples() -> str:
        return """
### ✨ Few-Shot Examples

**Input:**
Product: "GlowUp Serum" (Skincare)
Hook: "3일 만에 달라지는 피부 기적"
Style: "Clean & Minimal"

**Output:**
{
    "veo_prompt": "Cinematic close-up of a clear glass dropper bottle containing golden serum, placed on a white marble surface. Soft morning sunlight casts gentle shadows. A hand with manicured nails gently picks up the bottle. Water droplets on the bottle glisten. 4k resolution, photorealistic, high key lighting, beauty commercial aesthetic.",
    "negative_prompt": "text, watermark, blurry, distorted hand, bad nails, low quality, dark, grainy",
    "metadata": {
        "style": "Minimal",
        "camera_motion": "Static with subtle light movement",
        "mood": "Pure & Clean"
    }
}

**Input:**
Product: "TurboX Gaming Mouse" (Tech)
Hook: "게이머를 위한 궁극의 무기"
Style: "Cyberpunk"

**Output:**
{
    "veo_prompt": "Dynamic low-angle shot of a sleak black gaming mouse with RGB lighting pulsing in neon blue and purple on a dark desk. Cyberpunk city reflection visible on the mouse surface. Atmospheric fog and neon lights in the background. High contrast, energetic mood, commercial product videography, 8k, sharp focus.",
    "negative_prompt": "text, logo, blurry, distorted, messy cables, dust, low resolution",
    "metadata": {
        "style": "Cyberpunk",
        "camera_motion": "Slow Orbit",
        "mood": "Futuristic & Energetic"
    }
}
"""

    @classmethod
    def construct_generation_prompt(
        cls,
        product_name: str,
        product_desc: str,
        hook_text: str,
        style: str = "Cinematic",
    ) -> str:
        """
        Generates the full prompt to be sent to the LLM (Gemini)
        to ask IT to write the Veo prompt.
        """
        base_prompt = f"""
{cls.SYSTEM_CONTEXT}

{cls.get_prompt_structure()}

{cls.get_few_shot_examples()}

### 🎬 Current Task
**Input:**
Product: "{product_name}" ({product_desc})
Hook: "{hook_text}"
Style: "{style}"

**Action:**
Write the optimally engineered prompt for Google Veo 3.1.
Ensure the prompt visualizes the 'Hook' concept creatively.
"""
        return base_prompt

    @staticmethod
    def get_prompt_example(style: str = "Cinematic") -> Dict[str, str]:
        """UI에 표시할 예시 프롬프트 반환"""
        if style == "Cinematic":
            return {
                "veo_prompt": "Cinematic wide shot of a luxury car driving through a coastal road at sunset...",
                "negative_prompt": "blur, distortion, low quality",
            }
        return {
            "veo_prompt": "Studio shot of a product on a clean background...",
            "negative_prompt": "clutter, messy, dark",
        }
