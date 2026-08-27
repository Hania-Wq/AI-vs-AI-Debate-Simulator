import re
from typing import List, Tuple

try:
    from .llm import call_llm
    from .models import DebateResponse, Turn
    from .prompts import build_against_prompt, build_for_prompt, build_judge_prompt
except ImportError:
    from llm import call_llm
    from models import DebateResponse, Turn
    from prompts import build_against_prompt, build_for_prompt, build_judge_prompt


def _call_llm_with_retry(prompt: str, retries: int = 1) -> str:
    """Call LLM with up to `retries` additional retry on failure."""
    last_err: Exception | None = None
    for _ in range(retries + 1):
        try:
            return call_llm(prompt)
        except Exception as e:
            last_err = e
    if last_err:
        raise last_err
    raise RuntimeError("Unknown error during LLM invocation.")


def parse_judge_output(output: str) -> Tuple[str, str]:
    """Parse judge response into (winner, reasoning).
    
    Defaults winner to 'UNDECIDED' if parsing fails or winner is unrecognized.
    """
    if not output:
        return "UNDECIDED", "No evaluation received from judge."

    winner = "UNDECIDED"
    reasoning = output.strip()

    # Search for WINNER: <FOR or AGAINST>
    winner_match = re.search(r"WINNER:\s*(FOR|AGAINST)\b", output, re.IGNORECASE)
    if winner_match:
        winner = winner_match.group(1).upper()

    # Search for REASONING: <text>
    reasoning_match = re.search(r"REASONING:\s*(.*)", output, re.IGNORECASE | re.DOTALL)
    if reasoning_match:
        extracted = reasoning_match.group(1).strip()
        if extracted:
            reasoning = extracted

    return winner, reasoning


def run_debate(topic: str, num_rounds: int = 3) -> DebateResponse:
    """Run a multi-round debate between FOR and AGAINST agents and judge the winner.

    Args:
        topic: The topic/resolution for the debate.
        num_rounds: Number of rounds (each round has FOR followed by AGAINST).

    Returns:
        DebateResponse containing topic, list of turns, winner, and judge reasoning.
    """
    transcript: List[Turn] = []

    for round_num in range(1, num_rounds + 1):
        # 1. FOR speaker
        for_prompt = build_for_prompt(topic, transcript)
        try:
            for_text = _call_llm_with_retry(for_prompt, retries=1)
            transcript.append(Turn(round=round_num, speaker="FOR", text=for_text))
        except Exception as e:
            transcript.append(
                Turn(
                    round=round_num,
                    speaker="SYSTEM",
                    text=f"Error generating FOR argument in round {round_num}: {str(e)}",
                )
            )

        # 2. AGAINST speaker (sees FOR's latest argument in transcript)
        against_prompt = build_against_prompt(topic, transcript)
        try:
            against_text = _call_llm_with_retry(against_prompt, retries=1)
            transcript.append(Turn(round=round_num, speaker="AGAINST", text=against_text))
        except Exception as e:
            transcript.append(
                Turn(
                    round=round_num,
                    speaker="SYSTEM",
                    text=f"Error generating AGAINST argument in round {round_num}: {str(e)}",
                )
            )

    # 3. Judge evaluation
    judge_prompt = build_judge_prompt(topic, transcript)
    try:
        judge_output = _call_llm_with_retry(judge_prompt, retries=1)
        winner, reasoning = parse_judge_output(judge_output)
    except Exception as e:
        winner = "UNDECIDED"
        reasoning = f"Judge failed to evaluate debate: {str(e)}"
        transcript.append(
            Turn(
                round=num_rounds,
                speaker="SYSTEM",
                text=f"Error during judge evaluation: {str(e)}",
            )
        )

    return DebateResponse(
        topic=topic,
        turns=transcript,
        winner=winner,
        reasoning=reasoning,
    )
