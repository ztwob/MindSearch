"""Utilities for accepting text/image multimodal requests."""

from typing import Dict, List, Union

from pydantic import BaseModel, Field


class MultimodalPart(BaseModel):
    """A normalized piece of multimodal input."""

    type: str = Field(description="Input type, for example text, image_url, or image_base64")
    content: str = Field(description="Text content, URL, or base64 payload")
    metadata: Dict[str, str] = Field(default_factory=dict)


def normalize_multimodal_inputs(inputs: Union[str, List[Dict]]) -> List[MultimodalPart]:
    """Normalize frontend/OpenAI-style multimodal inputs into typed parts."""
    if isinstance(inputs, str):
        return [MultimodalPart(type="text", content=inputs)]

    parts: List[MultimodalPart] = []
    for item in inputs:
        item_type = item.get("type", "text")
        if item_type == "text":
            content = item.get("text") or item.get("content") or ""
        elif item_type in {"image_url", "image"}:
            image_url = item.get("image_url", item.get("url", ""))
            content = image_url.get("url", "") if isinstance(image_url, dict) else image_url
            item_type = "image_url"
        elif item_type == "image_base64":
            content = item.get("image_base64") or item.get("content") or ""
        else:
            content = item.get("content") or item.get("text") or ""
        parts.append(
            MultimodalPart(
                type=item_type,
                content=content,
                metadata={k: str(v) for k, v in item.get("metadata", {}).items()},
            )
        )
    return parts
