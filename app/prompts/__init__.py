from pathlib import Path


def load_prompt(provider_name: str) -> str:
    """
    Load prompt from file in prompts directory.

    Args:
        provider_name: Name of the provider (e.g., 'openai_realtime')

    Returns:
        Prompt text as string
    """
    prompts_dir = Path(__file__).parent
    prompt_file = prompts_dir / f"{provider_name}.txt"

    if not prompt_file.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_file}")

    return prompt_file.read_text().strip()
