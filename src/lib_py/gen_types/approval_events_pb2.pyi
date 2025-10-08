from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class CreativeApproved(_message.Message):
    __slots__ = ("campaign_id", "product_id", "variant_id", "locale", "revision", "approved_by", "correlation_id", "timestamp")
    CAMPAIGN_ID_FIELD_NUMBER: _ClassVar[int]
    PRODUCT_ID_FIELD_NUMBER: _ClassVar[int]
    VARIANT_ID_FIELD_NUMBER: _ClassVar[int]
    LOCALE_FIELD_NUMBER: _ClassVar[int]
    REVISION_FIELD_NUMBER: _ClassVar[int]
    APPROVED_BY_FIELD_NUMBER: _ClassVar[int]
    CORRELATION_ID_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    campaign_id: str
    product_id: str
    variant_id: str
    locale: str
    revision: int
    approved_by: str
    correlation_id: str
    timestamp: str
    def __init__(self, campaign_id: _Optional[str] = ..., product_id: _Optional[str] = ..., variant_id: _Optional[str] = ..., locale: _Optional[str] = ..., revision: _Optional[int] = ..., approved_by: _Optional[str] = ..., correlation_id: _Optional[str] = ..., timestamp: _Optional[str] = ...) -> None: ...

class RevisionRequested(_message.Message):
    __slots__ = ("campaign_id", "product_id", "locale", "from_revision", "feedback", "requested_by", "correlation_id", "timestamp")
    CAMPAIGN_ID_FIELD_NUMBER: _ClassVar[int]
    PRODUCT_ID_FIELD_NUMBER: _ClassVar[int]
    LOCALE_FIELD_NUMBER: _ClassVar[int]
    FROM_REVISION_FIELD_NUMBER: _ClassVar[int]
    FEEDBACK_FIELD_NUMBER: _ClassVar[int]
    REQUESTED_BY_FIELD_NUMBER: _ClassVar[int]
    CORRELATION_ID_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    campaign_id: str
    product_id: str
    locale: str
    from_revision: int
    feedback: str
    requested_by: str
    correlation_id: str
    timestamp: str
    def __init__(self, campaign_id: _Optional[str] = ..., product_id: _Optional[str] = ..., locale: _Optional[str] = ..., from_revision: _Optional[int] = ..., feedback: _Optional[str] = ..., requested_by: _Optional[str] = ..., correlation_id: _Optional[str] = ..., timestamp: _Optional[str] = ...) -> None: ...

class CreativeReadyForReview(_message.Message):
    __slots__ = ("campaign_id", "product_id", "locale", "revision", "best_variant_id", "alternate_variant_ids", "correlation_id", "timestamp")
    CAMPAIGN_ID_FIELD_NUMBER: _ClassVar[int]
    PRODUCT_ID_FIELD_NUMBER: _ClassVar[int]
    LOCALE_FIELD_NUMBER: _ClassVar[int]
    REVISION_FIELD_NUMBER: _ClassVar[int]
    BEST_VARIANT_ID_FIELD_NUMBER: _ClassVar[int]
    ALTERNATE_VARIANT_IDS_FIELD_NUMBER: _ClassVar[int]
    CORRELATION_ID_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    campaign_id: str
    product_id: str
    locale: str
    revision: int
    best_variant_id: str
    alternate_variant_ids: _containers.RepeatedScalarFieldContainer[str]
    correlation_id: str
    timestamp: str
    def __init__(self, campaign_id: _Optional[str] = ..., product_id: _Optional[str] = ..., locale: _Optional[str] = ..., revision: _Optional[int] = ..., best_variant_id: _Optional[str] = ..., alternate_variant_ids: _Optional[_Iterable[str]] = ..., correlation_id: _Optional[str] = ..., timestamp: _Optional[str] = ...) -> None: ...
