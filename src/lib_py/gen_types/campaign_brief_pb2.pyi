from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CampaignBrief(_message.Message):
    __slots__ = ("campaign_id", "products", "target_locales", "audience", "localization", "brand", "placement", "output", "correlation_id", "timestamp")
    CAMPAIGN_ID_FIELD_NUMBER: _ClassVar[int]
    PRODUCTS_FIELD_NUMBER: _ClassVar[int]
    TARGET_LOCALES_FIELD_NUMBER: _ClassVar[int]
    AUDIENCE_FIELD_NUMBER: _ClassVar[int]
    LOCALIZATION_FIELD_NUMBER: _ClassVar[int]
    BRAND_FIELD_NUMBER: _ClassVar[int]
    PLACEMENT_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_FIELD_NUMBER: _ClassVar[int]
    CORRELATION_ID_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    campaign_id: str
    products: _containers.RepeatedCompositeFieldContainer[Product]
    target_locales: _containers.RepeatedScalarFieldContainer[str]
    audience: Audience
    localization: Localization
    brand: BrandCompliance
    placement: BrandPlacement
    output: OutputSpec
    correlation_id: str
    timestamp: str
    def __init__(self, campaign_id: _Optional[str] = ..., products: _Optional[_Iterable[_Union[Product, _Mapping]]] = ..., target_locales: _Optional[_Iterable[str]] = ..., audience: _Optional[_Union[Audience, _Mapping]] = ..., localization: _Optional[_Union[Localization, _Mapping]] = ..., brand: _Optional[_Union[BrandCompliance, _Mapping]] = ..., placement: _Optional[_Union[BrandPlacement, _Mapping]] = ..., output: _Optional[_Union[OutputSpec, _Mapping]] = ..., correlation_id: _Optional[str] = ..., timestamp: _Optional[str] = ...) -> None: ...

class Product(_message.Message):
    __slots__ = ("id", "name", "description")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    description: str
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ...) -> None: ...

class Audience(_message.Message):
    __slots__ = ("region", "audience", "age_min", "age_max", "interests_text")
    REGION_FIELD_NUMBER: _ClassVar[int]
    AUDIENCE_FIELD_NUMBER: _ClassVar[int]
    AGE_MIN_FIELD_NUMBER: _ClassVar[int]
    AGE_MAX_FIELD_NUMBER: _ClassVar[int]
    INTERESTS_TEXT_FIELD_NUMBER: _ClassVar[int]
    region: str
    audience: str
    age_min: int
    age_max: int
    interests_text: str
    def __init__(self, region: _Optional[str] = ..., audience: _Optional[str] = ..., age_min: _Optional[int] = ..., age_max: _Optional[int] = ..., interests_text: _Optional[str] = ...) -> None: ...

class Localization(_message.Message):
    __slots__ = ("message_en", "message_de", "message_fr", "message_it")
    MESSAGE_EN_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_DE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FR_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_IT_FIELD_NUMBER: _ClassVar[int]
    message_en: str
    message_de: str
    message_fr: str
    message_it: str
    def __init__(self, message_en: _Optional[str] = ..., message_de: _Optional[str] = ..., message_fr: _Optional[str] = ..., message_it: _Optional[str] = ...) -> None: ...

class BrandCompliance(_message.Message):
    __slots__ = ("primary_color", "logo_s3_uri", "banned_words_en", "banned_words_de", "banned_words_fr", "banned_words_it", "legal_guidelines")
    PRIMARY_COLOR_FIELD_NUMBER: _ClassVar[int]
    LOGO_S3_URI_FIELD_NUMBER: _ClassVar[int]
    BANNED_WORDS_EN_FIELD_NUMBER: _ClassVar[int]
    BANNED_WORDS_DE_FIELD_NUMBER: _ClassVar[int]
    BANNED_WORDS_FR_FIELD_NUMBER: _ClassVar[int]
    BANNED_WORDS_IT_FIELD_NUMBER: _ClassVar[int]
    LEGAL_GUIDELINES_FIELD_NUMBER: _ClassVar[int]
    primary_color: str
    logo_s3_uri: str
    banned_words_en: _containers.RepeatedScalarFieldContainer[str]
    banned_words_de: _containers.RepeatedScalarFieldContainer[str]
    banned_words_fr: _containers.RepeatedScalarFieldContainer[str]
    banned_words_it: _containers.RepeatedScalarFieldContainer[str]
    legal_guidelines: str
    def __init__(self, primary_color: _Optional[str] = ..., logo_s3_uri: _Optional[str] = ..., banned_words_en: _Optional[_Iterable[str]] = ..., banned_words_de: _Optional[_Iterable[str]] = ..., banned_words_fr: _Optional[_Iterable[str]] = ..., banned_words_it: _Optional[_Iterable[str]] = ..., legal_guidelines: _Optional[str] = ...) -> None: ...

class BrandPlacement(_message.Message):
    __slots__ = ("logo_position", "overlay_text_position")
    LOGO_POSITION_FIELD_NUMBER: _ClassVar[int]
    OVERLAY_TEXT_POSITION_FIELD_NUMBER: _ClassVar[int]
    logo_position: str
    overlay_text_position: str
    def __init__(self, logo_position: _Optional[str] = ..., overlay_text_position: _Optional[str] = ...) -> None: ...

class OutputSpec(_message.Message):
    __slots__ = ("aspect_ratios", "format", "s3_prefix")
    ASPECT_RATIOS_FIELD_NUMBER: _ClassVar[int]
    FORMAT_FIELD_NUMBER: _ClassVar[int]
    S3_PREFIX_FIELD_NUMBER: _ClassVar[int]
    aspect_ratios: _containers.RepeatedScalarFieldContainer[str]
    format: str
    s3_prefix: str
    def __init__(self, aspect_ratios: _Optional[_Iterable[str]] = ..., format: _Optional[str] = ..., s3_prefix: _Optional[str] = ...) -> None: ...
