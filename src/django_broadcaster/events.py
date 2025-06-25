from typing import Any, Dict, Optional


class CloudEvent:
    """
    CloudEvent interface compatible with CloudEvents specification
    """

    def __init__(
        self,
        event_type: str,
        source: str,
        data: Optional[Any] = None,
        subject: str = "",
        data_content_type: str = "application/json",
        data_schema: str = "",
        spec_version: str = "1.0",
    ):
        self.spec_version = spec_version
        self.event_type = event_type
        self.source = source
        self.subject = subject
        self.data_content_type = data_content_type
        self.data_schema = data_schema
        self.data = data

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        event_dict = {
            "specversion": self.spec_version,
            "type": self.event_type,
            "source": self.source,
        }

        if self.subject:
            event_dict["subject"] = self.subject
        if self.data_content_type:
            event_dict["datacontenttype"] = self.data_content_type
        if self.data_schema:
            event_dict["dataschema"] = self.data_schema
        if self.data is not None:
            event_dict["data"] = self.data

        return event_dict
