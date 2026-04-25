from typing import Any

from deps_asb import ASBSettings
from deps_kafka import KafkaSettings
from deps_message_flow import MessagingDriverEnum
from deps_rabbitmq import RabbitMQTLSSettings
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from deps_prototype.extras.settings import (
    AuthenticationSettings,
    DatabaseSettings,
    ServiceInfoSettings,
)


class ParsingProxySettings(BaseSettings):
    url: str = ""
    proxy_timeout: int = 300

    model_config = SettingsConfigDict(env_prefix="PARSING_")


class ExtractionProxySettings(BaseSettings):
    url: str = ""
    proxy_timeout: int = 60

    model_config = SettingsConfigDict(env_prefix="EXTRACTION_")


class DocumentTypeProxySettings(BaseSettings):
    url: str = ""
    proxy_timeout: int = 60

    model_config = SettingsConfigDict(env_prefix="DOCUMENT_TYPE_")


class UnifierProxySettings(BaseSettings):
    url: str = ""
    proxy_timeout: int = 60

    model_config = SettingsConfigDict(env_prefix="UNIFIER_")


class FileStorageProxySettings(BaseSettings):
    url: str = ""
    proxy_timeout: int = 60

    model_config = SettingsConfigDict(env_prefix="FILE_STORAGE_")


class DocumentProxySettings(BaseSettings):
    url: str = ""
    proxy_timeout: int = 60

    model_config = SettingsConfigDict(env_prefix="DOCUMENT_")


class Settings(BaseSettings):
    env: str = "development"
    version: str = "1.0"

    logger_level: str = Field("INFO", validation_alias="LOG_LEVEL")

    info: ServiceInfoSettings = ServiceInfoSettings()
    database: DatabaseSettings = DatabaseSettings()
    authentication: AuthenticationSettings = AuthenticationSettings()

    messaging_driver: MessagingDriverEnum = Field(MessagingDriverEnum.RABBITMQ, validation_alias="MESSAGING_DRIVER")
    messaging_driver_settings: Any = Field(None, validation_alias="MESSAGING_DRIVER_SETTINGS")
    message_broker_connection_string: str = ""

    document_type: DocumentTypeProxySettings = DocumentTypeProxySettings()
    parsing: ParsingProxySettings = ParsingProxySettings()
    extraction: ExtractionProxySettings = ExtractionProxySettings()
    unifier: UnifierProxySettings = UnifierProxySettings()
    file_storage: FileStorageProxySettings = FileStorageProxySettings()
    document: DocumentProxySettings = DocumentProxySettings()

    documentation_enabled: bool = True
    instrumentation_enabled: bool = False
    ssl_verify: bool = False

    model_config = SettingsConfigDict(use_enum_values=True)

    @field_validator("messaging_driver_settings", mode="before")
    @classmethod
    def validate_messaging_driver_settings(cls, v, info):  # noqa: N805
        messaging_driver = info.data.get("messaging_driver")
        if not messaging_driver:
            raise ValueError("Invalid messaging driver")

        driver = MessagingDriverEnum(messaging_driver)
        if driver == MessagingDriverEnum.ASB:
            return ASBSettings()
        elif driver == MessagingDriverEnum.KAFKA:
            return KafkaSettings()
        elif driver == MessagingDriverEnum.RABBITMQ:
            return RabbitMQTLSSettings().model_dump()  # TODO: use BaseSettings

        raise ValueError(f"Driver {driver} is not implemented")
