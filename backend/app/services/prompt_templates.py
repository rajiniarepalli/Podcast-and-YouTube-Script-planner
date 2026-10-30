from app.schemas import ScriptGenerationRequest, ScriptRefinementRequest

def build_youtube_prompt(req: ScriptGenerationRequest) -> str:
    tone_str = req.tone.value if hasattr(req.tone, 'value') else str(req.tone)
    return f"""
You are an award-winning YouTube content strategist and scriptwriter.
Create a comprehensive, production-ready YouTube video script based on the following specifications:

- Topic: {req.topic}
- Target Audience: {req.target_audience or 'General Audience'}
- Language: {req.language or 'English'}
- Tone: {tone_str}
- Desired Duration: {req.duration or '5-7 minutes'}
- Keywords to naturally include: {req.keywords or "None specified"}
- Special Instructions: {req.additional_instructions or "None"}

Please format your response clearly using Markdown with the following distinct sections:

# [Video Title Suggestions]
(Provide 3 punchy, high-CTR YouTube title options)

# [Thumbnail Concept]
(Provide 2 visual thumbnail ideas with brief text overlay suggestions)

# [Hook & Intro] (0:00 - 0:45)
- Attention-grabbing opening hook.
- Problem statement / payoff teaser.
- Quick introduction and video roadmap.

# [Main Body Segments]
(Break down the core content into 3-4 structured segments with speaking lines, on-screen text [OST] cues, and B-roll/visual directions in brackets.)

# [Audience Engagement & Call to Action (CTA)]
- A natural question to spark comments in the comment section.
- Clear, non-spammy Like/Subscribe CTA.

# [Outro & Next Steps]
- Key takeaway summary and wrap-up.

# [Metadata: Description & Hashtags]
- SEO-friendly 2-paragraph video description.
- 5-8 relevant hashtags.

CRITICAL INSTRUCTIONS:
- Ground all facts. If an unverified claim, metric, or reference is introduced, explicitly flag it with [VERIFY: ...].
- Write naturally for the speaker.
"""

def build_podcast_prompt(req: ScriptGenerationRequest) -> str:
    tone_str = req.tone.value if hasattr(req.tone, 'value') else str(req.tone)
    return f"""
You are a veteran podcast producer and scriptwriter.
Create a natural, conversational, and highly engaging podcast episode script based on these specifications:

- Episode Topic: {req.topic}
- Target Listeners: {req.target_audience or 'General Audience'}
- Language: {req.language or 'English'}
- Tone: {tone_str}
- Target Duration: {req.duration or '15 minutes'}
- Key Topics/Keywords: {req.keywords or "None specified"}
- Special Instructions: {req.additional_instructions or "None"}

Please format your response clearly using Markdown with the following sections:

# [Episode Title Options]
(Provide 2-3 engaging episode titles)

# [Episode Summary]
(A concise, intriguing 2-sentence summary)

# [Intro & Host Welcome]
- Audio cue suggestions [e.g., Intro Music Fade Out].
- Warm welcome, episode theme announcement, and listener hook.

# [Segment 1: Setting the Stage]
- Natural host narration setting context.

# [Segment 2: Deep Dive Discussion]
- In-depth exploration with vocal pacing cues.
- 3 thought-provoking questions.
- Smooth verbal transition into the next segment.

# [Segment 3: Practical Takeaways & Real-World Application]
- Actionable steps and insights.

# [Listener Engagement & Outro]
- Review/share call to action.
- Community question of the week.
- Warm closing remarks [Outro Music Fade In].

# [Show Notes & Description]
- Ready-to-publish show notes with key bullet points.

CRITICAL INSTRUCTIONS:
- The script MUST sound natural when spoken aloud. Use conversational pacing.
- Flag any claims needing factual verification with [VERIFY: ...].
"""

def build_refinement_prompt(req: ScriptRefinementRequest) -> str:
    tone_str = req.target_tone if req.target_tone else 'Conversational'
    action_guidelines = {
        "make_shorter": "Condense this script by approximately 30-40%, removing filler words.",
        "make_longer": "Expand this script by adding richer explanations and practical analogies.",
        "change_tone": f"Rewrite this script shifting the tone to {tone_str}.",
        "improve_hook": "Revise the introduction and hook to be dramatically more compelling and high-stakes.",
        "add_examples": "Integrate 2-3 concrete, relatable examples into the main sections.",
        "simplify": "Simplify complex technical jargon into clear, accessible language.",
        "custom": f"Apply this specific custom refinement: {req.custom_instruction}"
    }

    guideline = action_guidelines.get(req.action, "Improve clarity and flow.")

    return f"""
You are an expert script editor.
Your task is to refine the following script according to these instructions:

DIRECTIVE: {guideline}

ORIGINAL SCRIPT:
------------------
{req.script}
------------------

Output the complete, revised script in clean Markdown format.
"""
