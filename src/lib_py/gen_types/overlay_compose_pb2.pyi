from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class OverlayComposeRequest(_message.Message):
    __slots__ = ("campaign_id", "product_id", "variant_id", "locale", "s3_uri_branded", "text", "text_position", "aspect_ratios", "format", "correlation_id", "timestamp")
    CAMPAIGN_ID_FIELD_NUMBER: _ClassVar[int]
    PRODUCT_ID_FIELD_NUMBER: _ClassVar[int]
    VARIANT_ID_FIELD_NUMBER: _ClassVar[int]
    LOCALE_FIELD_NUMBER: _ClassVar[int]
    S3_URI_BRANDED_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    TEXT_POSITION_FIELD_NUMBER: _ClassVar[int]
    ASPECT_RATIOS_FIELD_NUMBER: _ClassVar[int]
    FORMAT_FIELD_NUMBER: _ClassVar[int]
    CORRELATION_ID_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    campaign_id: str
    product_id: str
    variant_id: str
    locale: str
    s3_uri_branded: str
    text: str
    text_position: str
    aspect_ratios: _containers.RepeatedScalarFieldContainer[str]
    format: str
    correlation_id: str
    timestamp: str
    def __init__(self, campaign_id: _Optional[str] = ..., product_id: _Optional[str] = ..., variant_id: _Optional[str] = ..., locale: _Optional[str] = ..., s3_uri_branded: _Optional[str] = ..., text: _Optional[str] = ..., text_position: _Optional[str] = ..., aspect_ratios: _Optional[_Iterable[str]] = ..., format: _Optional[str] = ..., correlation_id: _Optional[str] = ..., timestamp: _Optional[str] = ...) -> None: ...

class OverlayComposeDone(_message.Message):
    __slots__ = ("campaign_id", "product_id", "variant_id", "locale", "outputs", "correlation_id", "timestamp")
    CAMPAIGN_ID_FIELD_NUMBER: _ClassVar[int]
    PRODUCT_ID_FIELD_NUMBER: _ClassVar[int]
    VARIANT_ID_FIELD_NUMBER: _ClassVar[int]
    LOCALE_FIELD_NUMBER: _ClassVar[int]
    OUTPUTS_FIELD_NUMBER: _ClassVar[int]
    CORRELATION_ID_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    campaign_id: str
    product_id: str
    variant_id: str
    locale: str
    outputs: _containers.RepeatedCompositeFieldContainer[AspectOutput]
    correlation_id: str
    timestamp: str
    def __init__(self, campaign_id: _Optional[str] = ..., product_id: _Optional[str] = ..., variant_id: _Optional[str] = ..., locale: _Optional[str] = ..., outputs: _Optional[_Iterable[_Union[AspectOutput, _Mapping]]] = ..., correlation_id: _Optional[str] = ..., timestamp: _Optional[str] = ...) -> None: ...

class AspectOutput(_message.Message):
    __slots__ = ("aspect_ratio", "s3_uri_final")
    ASPECT_RATIO_FIELD_NUMBER: _ClassVar[int]
    S3_URI_FINAL_FIELD_NUMBER: _ClassVar[int]
    aspect_ratio: str
    s3_uri_final: str
    def __init__(self, aspect_ratio: _Optional[str] = ..., s3_uri_final: _Optional[str] = ...) -> None: ...
