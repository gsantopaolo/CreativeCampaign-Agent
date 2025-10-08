from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class BrandComposeRequest(_message.Message):
    __slots__ = ("campaign_id", "product_id", "variant_id", "locale", "s3_uri_raw", "logo_s3_uri", "primary_color", "logo_position", "correlation_id", "timestamp")
    CAMPAIGN_ID_FIELD_NUMBER: _ClassVar[int]
    PRODUCT_ID_FIELD_NUMBER: _ClassVar[int]
    VARIANT_ID_FIELD_NUMBER: _ClassVar[int]
    LOCALE_FIELD_NUMBER: _ClassVar[int]
    S3_URI_RAW_FIELD_NUMBER: _ClassVar[int]
    LOGO_S3_URI_FIELD_NUMBER: _ClassVar[int]
    PRIMARY_COLOR_FIELD_NUMBER: _ClassVar[int]
    LOGO_POSITION_FIELD_NUMBER: _ClassVar[int]
    CORRELATION_ID_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    campaign_id: str
    product_id: str
    variant_id: str
    locale: str
    s3_uri_raw: str
    logo_s3_uri: str
    primary_color: str
    logo_position: str
    correlation_id: str
    timestamp: str
    def __init__(self, campaign_id: _Optional[str] = ..., product_id: _Optional[str] = ..., variant_id: _Optional[str] = ..., locale: _Optional[str] = ..., s3_uri_raw: _Optional[str] = ..., logo_s3_uri: _Optional[str] = ..., primary_color: _Optional[str] = ..., logo_position: _Optional[str] = ..., correlation_id: _Optional[str] = ..., timestamp: _Optional[str] = ...) -> None: ...

class BrandComposeDone(_message.Message):
    __slots__ = ("campaign_id", "product_id", "variant_id", "locale", "s3_uri_branded", "correlation_id", "timestamp")
    CAMPAIGN_ID_FIELD_NUMBER: _ClassVar[int]
    PRODUCT_ID_FIELD_NUMBER: _ClassVar[int]
    VARIANT_ID_FIELD_NUMBER: _ClassVar[int]
    LOCALE_FIELD_NUMBER: _ClassVar[int]
    S3_URI_BRANDED_FIELD_NUMBER: _ClassVar[int]
    CORRELATION_ID_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    campaign_id: str
    product_id: str
    variant_id: str
    locale: str
    s3_uri_branded: str
    correlation_id: str
    timestamp: str
    def __init__(self, campaign_id: _Optional[str] = ..., product_id: _Optional[str] = ..., variant_id: _Optional[str] = ..., locale: _Optional[str] = ..., s3_uri_branded: _Optional[str] = ..., correlation_id: _Optional[str] = ..., timestamp: _Optional[str] = ...) -> None: ...
