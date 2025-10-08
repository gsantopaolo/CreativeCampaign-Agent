from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ContextEnrichRequest(_message.Message):
    __slots__ = ("campaign_id", "locale", "region", "audience", "age_min", "age_max", "interests_text", "product_names", "correlation_id", "timestamp")
    CAMPAIGN_ID_FIELD_NUMBER: _ClassVar[int]
    LOCALE_FIELD_NUMBER: _ClassVar[int]
    REGION_FIELD_NUMBER: _ClassVar[int]
    AUDIENCE_FIELD_NUMBER: _ClassVar[int]
    AGE_MIN_FIELD_NUMBER: _ClassVar[int]
    AGE_MAX_FIELD_NUMBER: _ClassVar[int]
    INTERESTS_TEXT_FIELD_NUMBER: _ClassVar[int]
    PRODUCT_NAMES_FIELD_NUMBER: _ClassVar[int]
    CORRELATION_ID_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    campaign_id: str
    locale: str
    region: str
    audience: str
    age_min: int
    age_max: int
    interests_text: str
    product_names: _containers.RepeatedScalarFieldContainer[str]
    correlation_id: str
    timestamp: str
    def __init__(self, campaign_id: _Optional[str] = ..., locale: _Optional[str] = ..., region: _Optional[str] = ..., audience: _Optional[str] = ..., age_min: _Optional[int] = ..., age_max: _Optional[int] = ..., interests_text: _Optional[str] = ..., product_names: _Optional[_Iterable[str]] = ..., correlation_id: _Optional[str] = ..., timestamp: _Optional[str] = ...) -> None: ...

class ContextEnrichReady(_message.Message):
    __slots__ = ("campaign_id", "locale", "context_pack", "correlation_id", "timestamp")
    CAMPAIGN_ID_FIELD_NUMBER: _ClassVar[int]
    LOCALE_FIELD_NUMBER: _ClassVar[int]
    CONTEXT_PACK_FIELD_NUMBER: _ClassVar[int]
    CORRELATION_ID_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    campaign_id: str
    locale: str
    context_pack: ContextPack
    correlation_id: str
    timestamp: str
    def __init__(self, campaign_id: _Optional[str] = ..., locale: _Optional[str] = ..., context_pack: _Optional[_Union[ContextPack, _Mapping]] = ..., correlation_id: _Optional[str] = ..., timestamp: _Optional[str] = ...) -> None: ...

class ContextPack(_message.Message):
    __slots__ = ("locale", "culture_notes", "tone", "dos", "donts", "banned_words", "legal_guidelines")
    LOCALE_FIELD_NUMBER: _ClassVar[int]
    CULTURE_NOTES_FIELD_NUMBER: _ClassVar[int]
    TONE_FIELD_NUMBER: _ClassVar[int]
    DOS_FIELD_NUMBER: _ClassVar[int]
    DONTS_FIELD_NUMBER: _ClassVar[int]
    BANNED_WORDS_FIELD_NUMBER: _ClassVar[int]
    LEGAL_GUIDELINES_FIELD_NUMBER: _ClassVar[int]
    locale: str
    culture_notes: str
    tone: str
    dos: _containers.RepeatedScalarFieldContainer[str]
    donts: _containers.RepeatedScalarFieldContainer[str]
    banned_words: _containers.RepeatedScalarFieldContainer[str]
    legal_guidelines: str
    def __init__(self, locale: _Optional[str] = ..., culture_notes: _Optional[str] = ..., tone: _Optional[str] = ..., dos: _Optional[_Iterable[str]] = ..., donts: _Optional[_Iterable[str]] = ..., banned_words: _Optional[_Iterable[str]] = ..., legal_guidelines: _Optional[str] = ...) -> None: ...
