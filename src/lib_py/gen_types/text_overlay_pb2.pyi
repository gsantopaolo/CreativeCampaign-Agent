from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class TextOverlaid(_message.Message):
    __slots__ = ("campaign_id", "locale", "final_image_s3_uri", "final_image_url")
    CAMPAIGN_ID_FIELD_NUMBER: _ClassVar[int]
    LOCALE_FIELD_NUMBER: _ClassVar[int]
    FINAL_IMAGE_S3_URI_FIELD_NUMBER: _ClassVar[int]
    FINAL_IMAGE_URL_FIELD_NUMBER: _ClassVar[int]
    campaign_id: str
    locale: str
    final_image_s3_uri: str
    final_image_url: str
    def __init__(self, campaign_id: _Optional[str] = ..., locale: _Optional[str] = ..., final_image_s3_uri: _Optional[str] = ..., final_image_url: _Optional[str] = ...) -> None: ...
