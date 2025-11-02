"""State definitions for the bot conversation handler."""

from enum import IntEnum


class ConversationState(IntEnum):
    """States for the bot conversation flow."""
    START = 0
    DXF_TEMPLATE_CONFIRMATION = 1
    FILE_UPLOAD = 2
    ENCODING_DETECTION = 3
    DELIMITER_DETECTION = 4
    COLUMN_MAPPING = 5
    SCALE_SELECTION = 6
    TIN_OPTIONS = 7
    DENSIFICATION_OPTIONS = 8
    EXTRAS_OPTIONS = 9
    CONFIRMATION = 10
    PROCESSING = 11
