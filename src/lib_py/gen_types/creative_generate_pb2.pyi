import context_enrich_pb2 as _context_enrich_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CreativeGenerateRequest(_message.Message):
    __slots__ = ("campaign_id", "product_id", "product_name", "product_description", "locale", "context_pack", "num_candidates", "seed", "revision", "feedback", "correlation_id", "timestamp")
    CAMPAIGN_ID_FIELD_NUMBER: _ClassVar[int]
    PRODUCT_ID_FIELD_NUMBER: _ClassVar[int]
    PRODUCT_NAME_FIELD_NUMBER: _ClassVar[int]
    PRODUCT_DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    LOCALE_FIELD_NUMBER: _ClassVar[int]
    CONTEXT_PACK_FIELD_NUMBER: _ClassVar[int]
    NUM_CANDIDATES_FIELD_NUMBER: _ClassVar[int]
    SEED_FIELD_NUMBER: _ClassVar[int]
    REVISION_FIELD_NUMBER: _ClassVar[int]
    FEEDBACK_FIELD_NUMBER: _ClassVar[int]
    CORRELATION_ID_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    campaign_id: str
    product_id: str
    product_name: str
    product_description: str
    locale: str
    context_pack: _context_enrich_pb2.ContextPack
    num_candidates: int
    seed: int
    revision: int
    feedback: str
    correlation_id: str
    timestamp: str
    def __init__(self, campaign_id: _Optional[str] = ..., product_id: _Optional[str] = ..., product_name: _Optional[str] = ..., product_description: _Optional[str] = ..., locale: _Optional[str] = ..., context_pack: _Optional[_Union[_context_enrich_pb2.ContextPack, _Mapping]] = ..., num_candidates: _Optional[int] = ..., seed: _Optional[int] = ..., revision: _Optional[int] = ..., feedback: _Optional[str] = ..., correlation_id: _Optional[str] = ..., timestamp: _Optional[str] = ...) -> None: ...

class CreativeGenerateDone(_message.Message):
    __slots__ = ("campaign_id", "product_id", "locale", "revision", "candidates", "correlation_id", "timestamp")
    CAMPAIGN_ID_FIELD_NUMBER: _ClassVar[int]
    PRODUCT_ID_FIELD_NUMBER: _ClassVar[int]
    LOCALE_FIELD_NUMBER: _ClassVar[int]
    REVISION_FIELD_NUMBER: _ClassVar[int]
    CANDIDATES_FIELD_NUMBER: _ClassVar[int]
    CORRELATION_ID_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    campaign_id: str
    product_id: str
    locale: str
    revision: int
    candidates: _containers.RepeatedCompositeFieldContainer[GeneratedCandidate]
    correlation_id: str
    timestamp: str
    def __init__(self, campaign_id: _Optional[str] = ..., product_id: _Optional[str] = ..., locale: _Optional[str] = ..., revision: _Optional[int] = ..., candidates: _Optional[_Iterable[_Union[GeneratedCandidate, _Mapping]]] = ..., correlation_id: _Optional[str] = ..., timestamp: _Optional[str] = ...) -> None: ...

class GeneratedCandidate(_message.Message):
    __slots__ = ("variant_id", "s3_uri_raw", "seed", "prompt_used", "quality_score", "compliant", "compliance_warnings")
    VARIANT_ID_FIELD_NUMBER: _ClassVar[int]
    S3_URI_RAW_FIELD_NUMBER: _ClassVar[int]
    SEED_FIELD_NUMBER: _ClassVar[int]
    PROMPT_USED_FIELD_NUMBER: _ClassVar[int]
    QUALITY_SCORE_FIELD_NUMBER: _ClassVar[int]
    COMPLIANT_FIELD_NUMBER: _ClassVar[int]
    COMPLIANCE_WARNINGS_FIELD_NUMBER: _ClassVar[int]
    variant_id: str
    s3_uri_raw: str
    seed: int
    prompt_used: str
    quality_score: float
    compliant: bool
    compliance_warnings: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, variant_id: _Optional[str] = ..., s3_uri_raw: _Optional[str] = ..., seed: _Optional[int] = ..., prompt_used: _Optional[str] = ..., quality_score: _Optional[float] = ..., compliant: bool = ..., compliance_warnings: _Optional[_Iterable[str]] = ...) -> None: ...
