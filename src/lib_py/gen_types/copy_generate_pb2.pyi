import context_enrich_pb2 as _context_enrich_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CopyGenerateRequest(_message.Message):
    __slots__ = ("campaign_id", "product_id", "variant_id", "locale", "s3_uri_branded", "context_pack", "base_message", "correlation_id", "timestamp")
    CAMPAIGN_ID_FIELD_NUMBER: _ClassVar[int]
    PRODUCT_ID_FIELD_NUMBER: _ClassVar[int]
    VARIANT_ID_FIELD_NUMBER: _ClassVar[int]
    LOCALE_FIELD_NUMBER: _ClassVar[int]
    S3_URI_BRANDED_FIELD_NUMBER: _ClassVar[int]
    CONTEXT_PACK_FIELD_NUMBER: _ClassVar[int]
    BASE_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    CORRELATION_ID_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    campaign_id: str
    product_id: str
    variant_id: str
    locale: str
    s3_uri_branded: str
    context_pack: _context_enrich_pb2.ContextPack
    base_message: str
    correlation_id: str
    timestamp: str
    def __init__(self, campaign_id: _Optional[str] = ..., product_id: _Optional[str] = ..., variant_id: _Optional[str] = ..., locale: _Optional[str] = ..., s3_uri_branded: _Optional[str] = ..., context_pack: _Optional[_Union[_context_enrich_pb2.ContextPack, _Mapping]] = ..., base_message: _Optional[str] = ..., correlation_id: _Optional[str] = ..., timestamp: _Optional[str] = ...) -> None: ...

class CopyGenerateDone(_message.Message):
    __slots__ = ("campaign_id", "product_id", "variant_id", "locale", "localized_copy", "cultural_fit_score", "compliant", "compliance_warnings", "correlation_id", "timestamp")
    CAMPAIGN_ID_FIELD_NUMBER: _ClassVar[int]
    PRODUCT_ID_FIELD_NUMBER: _ClassVar[int]
    VARIANT_ID_FIELD_NUMBER: _ClassVar[int]
    LOCALE_FIELD_NUMBER: _ClassVar[int]
    LOCALIZED_COPY_FIELD_NUMBER: _ClassVar[int]
    CULTURAL_FIT_SCORE_FIELD_NUMBER: _ClassVar[int]
    COMPLIANT_FIELD_NUMBER: _ClassVar[int]
    COMPLIANCE_WARNINGS_FIELD_NUMBER: _ClassVar[int]
    CORRELATION_ID_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    campaign_id: str
    product_id: str
    variant_id: str
    locale: str
    localized_copy: str
    cultural_fit_score: float
    compliant: bool
    compliance_warnings: _containers.RepeatedScalarFieldContainer[str]
    correlation_id: str
    timestamp: str
    def __init__(self, campaign_id: _Optional[str] = ..., product_id: _Optional[str] = ..., variant_id: _Optional[str] = ..., locale: _Optional[str] = ..., localized_copy: _Optional[str] = ..., cultural_fit_score: _Optional[float] = ..., compliant: bool = ..., compliance_warnings: _Optional[_Iterable[str]] = ..., correlation_id: _Optional[str] = ..., timestamp: _Optional[str] = ...) -> None: ...
