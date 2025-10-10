from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class ImageGenerateRequest(_message.Message):
    __slots__ = ("campaign_id", "locale", "product_id", "headline", "description", "visual_elements", "correlation_id", "timestamp")
    CAMPAIGN_ID_FIELD_NUMBER: _ClassVar[int]
    LOCALE_FIELD_NUMBER: _ClassVar[int]
    PRODUCT_ID_FIELD_NUMBER: _ClassVar[int]
    HEADLINE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    VISUAL_ELEMENTS_FIELD_NUMBER: _ClassVar[int]
    CORRELATION_ID_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    campaign_id: str
    locale: str
    product_id: str
    headline: str
    description: str
    visual_elements: _containers.RepeatedScalarFieldContainer[str]
    correlation_id: str
    timestamp: str
    def __init__(self, campaign_id: _Optional[str] = ..., locale: _Optional[str] = ..., product_id: _Optional[str] = ..., headline: _Optional[str] = ..., description: _Optional[str] = ..., visual_elements: _Optional[_Iterable[str]] = ..., correlation_id: _Optional[str] = ..., timestamp: _Optional[str] = ...) -> None: ...

class ImageGenerated(_message.Message):
    __slots__ = ("campaign_id", "locale", "product_id", "image_url", "s3_uri", "prompt_used", "status", "error_message", "correlation_id", "generated_at")
    CAMPAIGN_ID_FIELD_NUMBER: _ClassVar[int]
    LOCALE_FIELD_NUMBER: _ClassVar[int]
    PRODUCT_ID_FIELD_NUMBER: _ClassVar[int]
    IMAGE_URL_FIELD_NUMBER: _ClassVar[int]
    S3_URI_FIELD_NUMBER: _ClassVar[int]
    PROMPT_USED_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    ERROR_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    CORRELATION_ID_FIELD_NUMBER: _ClassVar[int]
    GENERATED_AT_FIELD_NUMBER: _ClassVar[int]
    campaign_id: str
    locale: str
    product_id: str
    image_url: str
    s3_uri: str
    prompt_used: str
    status: str
    error_message: str
    correlation_id: str
    generated_at: str
    def __init__(self, campaign_id: _Optional[str] = ..., locale: _Optional[str] = ..., product_id: _Optional[str] = ..., image_url: _Optional[str] = ..., s3_uri: _Optional[str] = ..., prompt_used: _Optional[str] = ..., status: _Optional[str] = ..., error_message: _Optional[str] = ..., correlation_id: _Optional[str] = ..., generated_at: _Optional[str] = ...) -> None: ...
