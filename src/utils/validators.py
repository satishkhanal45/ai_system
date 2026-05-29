import json
import re
from .schemas import StructuredResponse
from .logger import get_logger

logger = get_logger("validators")


def extract_json(raw: str) -> str:
    """Step 1 — strip markdown code blocks if present"""
    raw = raw.strip()
    if raw.startswith("```"):
        lines = raw.splitlines()
        lines = [l for l in lines if not l.startswith("```")]
        raw = "\n".join(lines).strip()
    return raw


def recover_json(raw: str) -> str:
    """Step 2 — attempt to recover common JSON issues"""

    # fix single quotes to double quotes
    raw = raw.replace("'", '"')

    # remove trailing commas before } or ]
    raw = re.sub(r",\s*([}\]])", r"\1", raw)

    # extract JSON object if there is extra text around it
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if match:
        raw = match.group()

    return raw


def validate_llm_output(raw: str) -> StructuredResponse | None:
    """
    Full pipeline:
    Step 1 — clean markdown
    Step 2 — try parsing
    Step 3 — if fails, attempt recovery
    Step 4 — validate against schema
    """

    # step 1 — clean markdown
    cleaned = extract_json(raw)
    logger.info("Step 1 — markdown cleaned")

    # step 2 — try parsing directly
    try:
        data = json.loads(cleaned)
        logger.info("Step 2 — JSON parsed successfully (no recovery needed)")

    except json.JSONDecodeError as e:
        logger.warning(f"Step 2 — JSON parse failed: {e}")

        # step 3 — attempt recovery
        logger.info("Step 3 — attempting JSON recovery")
        recovered = recover_json(cleaned)

        try:
            data = json.loads(recovered)
            logger.info("Step 3 — recovery successful")
        except json.JSONDecodeError as e2:
            logger.error(f"Step 3 — recovery failed, cannot parse JSON: {e2}")
            return None

    # step 4 — validate against schema
    try:
        result = StructuredResponse(**data)
        logger.info("Step 4 — schema validation passed")
        return result
    except Exception as e:
        logger.error(f"Step 4 — schema validation failed: {e}")
        return None
