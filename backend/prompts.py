from typing import Any, List


def format_transcript(transcript: List[Any]) -> str:
    """Format a list of Turn objects or dicts into a readable transcript string."""
    if not transcript:
        return "No previous rounds."
    formatted = []
    for item in transcript:
        if hasattr(item, "speaker") and hasattr(item, "text"):
            round_num = getattr(item, "round", "?")
            formatted.append(f"Round {round_num} [{item.speaker}]: {item.text}")
        elif isinstance(item, dict):
            round_num = item.get("round", "?")
            speaker = item.get("speaker", "UNKNOWN")
            text = item.get("text", "")
            formatted.append(f"Round {round_num} [{speaker}]: {text}")
        else:
            formatted.append(str(item))
    return "\n\n".join(formatted)


def build_for_prompt(topic: str, transcript: List[Any]) -> str:
    """Build the prompt for the FOR speaker arguing in favor of the topic.
    
    Placeholder wording - ready to be updated with finalized product prompts.
    """
    history = format_transcript(transcript)
    return (
        f"You are a competitive debater arguing strictly IN FAVOR OF (FOR) the following topic.\n\n"
        f"Debate Topic: {topic}\n\n"
        f"Transcript so far:\n{history}\n\n"
        f"Instructions:\n"
        f"1. Provide a compelling, coherent, and evidence-backed argument supporting the topic.\n"
        f"2. Directly address and refute any opposing points made in the transcript.\n"
        f"3. Keep your tone professional, persuasive, and concise.\n\n"
        f"Your argument (FOR):"
    )


def build_against_prompt(topic: str, transcript: List[Any]) -> str:
    """Build the prompt for the AGAINST speaker arguing against the topic.
    
    Placeholder wording - ready to be updated with finalized product prompts.
    """
    history = format_transcript(transcript)
    return (
        f"You are a competitive debater arguing strictly OPPOSING (AGAINST) the following topic.\n\n"
        f"Debate Topic: {topic}\n\n"
        f"Transcript so far:\n{history}\n\n"
        f"Instructions:\n"
        f"1. Provide a compelling, coherent, and evidence-backed argument against the topic.\n"
        f"2. Directly counter the FOR speaker's points and point out logical flaws or weaknesses.\n"
        f"3. Keep your tone professional, persuasive, and concise.\n\n"
        f"Your argument (AGAINST):"
    )


def build_judge_prompt(topic: str, transcript: List[Any]) -> str:
    """Build the prompt for the impartial judge evaluating the debate.
    
    Placeholder wording - requires strict parseable output format.
    """
    history = format_transcript(transcript)
    return (
        f"You are an impartial and expert debate adjudicator evaluating the following debate.\n\n"
        f"Debate Topic: {topic}\n\n"
        f"Complete Transcript:\n{history}\n\n"
        f"Instructions:\n"
        f"1. Objectively evaluate both sides based on argumentation quality, rebuttal effectiveness, and clarity.\n"
        f"2. Declare a winner: strictly choose either 'FOR' or 'AGAINST'.\n"
        f"3. Provide your rationale explaining why the winner prevailed.\n"
        f"4. You MUST format your response EXACTLY as follows:\n\n"
        f"WINNER: <FOR or AGAINST>\n"
        f"REASONING: <Your detailed evaluation and rationale>"
    )
