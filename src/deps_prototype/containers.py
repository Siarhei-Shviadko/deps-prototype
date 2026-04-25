from typing import Any, Dict, Type, Union

from dependency_injector import containers, providers, resources
from deps_asb import ASBClient, ASBConsumer, ASBProducer
from deps_kafka import KafkaClient, KafkaConsumer, KafkaProducer
from deps_message_flow import MessagingDriverEnum
from deps_message_flow.commands.producer import CommandProducer
from deps_message_flow.events.publisher import DomainEventPublisher
from deps_message_flow.messaging.consumer import IMessageConsumer
from deps_message_flow.messaging.producer import IMessageProducer
from deps_message_flow.sagas.orchestration import (
    SagaCommandProducer,
    SagaDataMapping,
    SagaInstanceFactory,
    SagaManagerFactory,
)
from deps_rabbitmq import RabbitMQClient, RabbitMQConsumer, RabbitMQProducer

from deps_prototype.application import (
    ExtractionService,
    IDocumentProxy,
    IDocumentTypeProxy,
    IExtractionProxy,
    IParsingProxy,
    MappingService,
    PrototypeService,
    QueryPrototypeService,
    ReferenceLayoutService,
    ReferenceLayoutServiceWithSagas,
    TabularMappingService,
    UnifiedMappingService,
)
from deps_prototype.constants import ASB_SUBSCRIPTION_NAME
from deps_prototype.domain.model import (
    IMappingRepository,
    IPrototypeRepository,
    IQueryPrototypeRepository,
    IReferenceLayoutRepository,
    ITabularMappingRepository,
)
from deps_prototype.extras.datasource import Database
from deps_prototype.extras.datasource.constants import DBDialect, DBDriver
from deps_prototype.infrastructure import (
    DocumentTypeProxy,
    ExtractionProxy,
    FileStorageProxy,
    ParsingProxy,
)
from deps_prototype.infrastructure.proxies.document import DocumentProxy
from deps_prototype.infrastructure.repositories import (
    MappingRepository,
    PrototypeRepository,
    QueryPrototypeRepository,
    ReferenceLayoutRepository,
    SagaInstanceRepository,
    TabularMappingRepository,
)
from deps_prototype.messaging.dispatcher import make_message_dispatcher
from deps_prototype.messaging.sagas import (
    PrototypeCreationSaga,
    ReferenceLayoutProcessingSaga,
)
from deps_prototype.messaging.sagas_data import (
    PrototypeCreationSteps,
    ReferenceLayoutProcessingSteps,
    make_saga_data_mapping,
)

MessagingClient = Union[ASBClient, KafkaClient, RabbitMQClient]


class DatabaseResource(resources.Resource):
    def init(
        self,
        username: str,
        password: str,
        host: str,
        port: int,
        database: str,
        dialect: DBDialect,
        driver: DBDriver,
        require_secure_transport: bool,
    ) -> Database:
        db = Database(
            username=username,
            password=password,
            host=host,
            port=port,
            database=database,
            dialect=dialect,
            driver=driver,
            require_secure_transport=require_secure_transport,
        )
        db.connect()
        return db

    def shutdown(self, resource: Database) -> None:
        resource.close()


class MessageBrokerResource(resources.Resource):
    def init(
        self,
        driver_type: str,
        expected_driver: str,
        client: Type[MessagingClient],
        message_connection_string: str,
        **kwargs: Dict[str, Any],
    ) -> MessagingClient | None:
        return client(message_connection_string, **kwargs) if driver_type == expected_driver else None

    def shutdown(self, resource: MessagingClient | None) -> None:
        if resource:
            resource.close()


class MessageBrokers(containers.DeclarativeContainer):
    config = providers.Configuration()
    messaging_driver_settings = providers.Dependency(instance_of=object)

    broker_client: providers.Provider[MessagingClient] = providers.Selector(
        config.messaging_driver,
        asb=providers.Resource(
            MessageBrokerResource,
            driver_type=MessagingDriverEnum.ASB.value,
            expected_driver=config.messaging_driver,
            client=ASBClient,
            message_connection_string=config.message_broker_connection_string,
            asb_settings=messaging_driver_settings,
        ),
        kafka=providers.Resource(
            MessageBrokerResource,
            driver_type=MessagingDriverEnum.KAFKA.value,
            expected_driver=config.messaging_driver,
            client=KafkaClient,
            message_connection_string=config.message_broker_connection_string,
            settings=messaging_driver_settings,
        ),
        rabbitmq=providers.Resource(
            MessageBrokerResource,
            driver_type=MessagingDriverEnum.RABBITMQ.value,
            expected_driver=config.messaging_driver,
            client=RabbitMQClient,
            message_connection_string=config.message_broker_connection_string,
            settings=messaging_driver_settings,
        ),
    )


class Messaging(containers.DeclarativeContainer):
    config = providers.Configuration()
    message_brokers = providers.DependenciesContainer()

    producer: providers.Provider[IMessageProducer] = providers.Selector(
        config.messaging_driver,
        asb=providers.Singleton(
            ASBProducer,
            client=message_brokers.broker_client,
            topic_name=config.messaging_driver_settings.topic_name,
        ),
        kafka=providers.Singleton(
            KafkaProducer,
            client=message_brokers.broker_client,
        ),
        rabbitmq=providers.Singleton(
            RabbitMQProducer,
            client=message_brokers.broker_client,
        ),
    )
    consumer: providers.Provider[IMessageConsumer] = providers.Selector(
        config.messaging_driver,
        asb=providers.Singleton(
            ASBConsumer,
            client=message_brokers.broker_client,
            topic_name=config.messaging_driver_settings.topic_name,
            custom_subscription_name=ASB_SUBSCRIPTION_NAME,
        ),
        kafka=providers.Singleton(
            KafkaConsumer,
            client=message_brokers.broker_client,
        ),
        rabbitmq=providers.Singleton(
            RabbitMQConsumer,
            client=message_brokers.broker_client,
        ),
    )


class Core(containers.DeclarativeContainer):
    config = providers.Configuration()
    build_info: providers.Provider[Dict] = providers.Dict(
        {
            "build_tag": config.info.tag,
            "build_date": config.info.date,
            "commit_hash": config.info.hash,
        },
    )


class Datasources(containers.DeclarativeContainer):
    config = providers.Configuration()

    postgres_datasource: providers.Provider[Database] = providers.Resource(
        DatabaseResource,
        config.user,
        config.password,
        config.host,
        config.port,
        config.db,
        config.dialect,
        config.driver,
        config.require_secure_transport,
    )


class Repositories(containers.DeclarativeContainer):
    datasources = providers.DependenciesContainer()

    prototype: providers.Singleton[IPrototypeRepository] = providers.Singleton(
        PrototypeRepository,
        datasources.postgres_datasource,
    )
    saga_instance: providers.Provider[SagaInstanceRepository] = providers.Singleton(
        SagaInstanceRepository,
        datasources.postgres_datasource,
    )
    mapping: providers.Singleton[IMappingRepository] = providers.Singleton(
        MappingRepository,
        datasources.postgres_datasource,
    )
    reference_layout: providers.Singleton[IReferenceLayoutRepository] = providers.Singleton(
        ReferenceLayoutRepository,
        datasources.postgres_datasource,
    )
    tabular_mapping: providers.Singleton[ITabularMappingRepository] = providers.Singleton(
        TabularMappingRepository,
        datasources.postgres_datasource,
    )
    query_prototype: providers.Singleton[IQueryPrototypeRepository] = providers.Singleton(
        QueryPrototypeRepository,
        datasources.postgres_datasource,
    )


class Services(containers.DeclarativeContainer):
    config = providers.Configuration()

    document_type_service: providers.Singleton[IDocumentTypeProxy] = providers.Singleton(
        DocumentTypeProxy,
        base_url=config.document_type.url,
        timeout=config.document_type.proxy_timeout,
        ssl_verify=config.ssl_verify,
    )
    extraction: providers.Provider[IExtractionProxy] = providers.Singleton(
        ExtractionProxy,
        base_url=config.extraction.url,
        timeout=config.extraction.proxy_timeout,
        ssl_verify=config.ssl_verify,
    )
    parsing: providers.Provider[IParsingProxy] = providers.Singleton(
        ParsingProxy,
        base_url=config.parsing.url,
        timeout=config.parsing.proxy_timeout,
        ssl_verify=config.ssl_verify,
    )
    document: providers.Provider[IDocumentProxy] = providers.Singleton(
        DocumentProxy,
        base_url=config.document.url,
        timeout=config.document.proxy_timeout,
        ssl_verify=config.ssl_verify,
    )

    file_storage: providers.Provider[FileStorageProxy] = providers.Singleton(
        FileStorageProxy,
        base_url=config.file_storage.url,
        ssl_verify=config.ssl_verify,
        timeout=config.file_storage.proxy_timeout,
    )


class SagaSteps(containers.DeclarativeContainer):
    services = providers.DependenciesContainer()
    repositories = providers.DependenciesContainer()
    domain_event_publisher: DomainEventPublisher = providers.Dependency()
    reference_layout: ReferenceLayoutService = providers.Dependency()

    prototype_creation: providers.Singleton[PrototypeCreationSteps] = providers.Singleton(
        PrototypeCreationSteps,
        document_type_service=services.document_type_service,
        extraction_service=services.extraction,
        prototype_repository=repositories.prototype,
        domain_event_publisher=domain_event_publisher,
    )
    reference_layout_processing: providers.Singleton[ReferenceLayoutProcessingSteps] = providers.Singleton(
        ReferenceLayoutProcessingSteps,
        reference_layout_service=reference_layout,
    )


class Application(containers.DeclarativeContainer):
    config = providers.Configuration()
    repositories = providers.DependenciesContainer()
    domain_event_publisher: DomainEventPublisher = providers.Dependency()
    saga_instance_factory: providers.Dependency[SagaInstanceFactory] = providers.Dependency()
    sagas = providers.List()
    services = providers.DependenciesContainer()

    prototype: providers.Singleton[PrototypeService] = providers.Singleton(
        PrototypeService,
        prototype_repository=repositories.prototype,
        mapping_repository=repositories.mapping,
        domain_event_publisher=domain_event_publisher,
        saga_instance_factory=saga_instance_factory,
        sagas=sagas,
        document_proxy=services.document,
    )

    mapping: providers.Singleton[MappingService] = providers.Singleton(
        MappingService,
        mapping_repository=repositories.mapping,
        prototype_repository=repositories.prototype,
        domain_event_publisher=domain_event_publisher,
    )

    tabular_mapping: providers.Singleton[TabularMappingService] = providers.Singleton(
        TabularMappingService,
        tabular_mapping_repository=repositories.tabular_mapping,
        prototype_repository=repositories.prototype,
    )

    unified_mapping: providers.Singleton[UnifiedMappingService] = providers.Singleton(
        UnifiedMappingService,
        mapping_repository=repositories.mapping,
        tabular_mapping_repository=repositories.tabular_mapping,
        prototype_repository=repositories.prototype,
    )

    extraction: providers.Singleton[ExtractionService] = providers.Singleton(
        ExtractionService,
        prototype_repository=repositories.prototype,
        mapping_repository=repositories.mapping,
        extraction_proxy=services.extraction,
        parsing_proxy=services.parsing,
        tabular_mapping_repository=repositories.tabular_mapping,
    )

    reference_layout_with_sagas: providers.Singleton[ReferenceLayoutServiceWithSagas] = providers.Singleton(
        ReferenceLayoutServiceWithSagas,
        prototype_repository=repositories.prototype,
        reference_layout_repository=repositories.reference_layout,
        file_storage_proxy=services.file_storage,
        saga_instance_factory=saga_instance_factory,
        sagas=sagas,
    )

    query_prototype: providers.Singleton[QueryPrototypeService] = providers.Singleton(
        QueryPrototypeService,
        query_prototype_repository=repositories.query_prototype,
    )


class Containers(containers.DeclarativeContainer):
    config = providers.Configuration()
    messaging_driver_settings = providers.Dependency(instance_of=object)

    datasources: providers.Container[Datasources] = providers.Container(
        Datasources,
        config=config.database,
    )

    repositories: providers.Container[Repositories] = providers.Container(
        Repositories,
        datasources=datasources,
    )

    core: providers.Container[Core] = providers.Container(Core, config=config)
    message_brokers: providers.Container[MessageBrokers] = providers.Container(
        MessageBrokers,
        config=config,
        messaging_driver_settings=messaging_driver_settings,
    )

    messaging: providers.Container[Messaging] = providers.Container(
        Messaging,
        config=config,
        message_brokers=message_brokers,
    )

    services: providers.Container[Services] = providers.Container(
        Services,
        config=config,
    )

    command_producer: providers.Singleton[CommandProducer] = providers.Singleton(
        CommandProducer,
        messaging.producer,
    )

    domain_event_publisher: providers.Singleton[DomainEventPublisher] = providers.Singleton(
        DomainEventPublisher,
        messaging.producer,
    )

    reference_layout: providers.Singleton[ReferenceLayoutService] = providers.Singleton(
        ReferenceLayoutService,
        prototype_repository=repositories.prototype,
        reference_layout_repository=repositories.reference_layout,
        domain_event_publisher=domain_event_publisher,
        command_producer=command_producer,
    )

    saga_command_producer: providers.Singleton[CommandProducer] = providers.Singleton(
        SagaCommandProducer,
        command_producer,
    )
    saga_data_mapping: providers.Singleton[SagaDataMapping] = providers.Singleton(
        make_saga_data_mapping,
    )
    saga_manager_factory: providers.Singleton[SagaManagerFactory] = providers.Singleton(
        SagaManagerFactory,
        repositories.saga_instance,
        command_producer,
        messaging.consumer,
        saga_command_producer,
        saga_data_mapping,
    )
    saga_steps: providers.Container[SagaSteps] = providers.Container(
        SagaSteps,
        services=services,
        repositories=repositories,
        domain_event_publisher=domain_event_publisher,
        reference_layout=reference_layout,
    )
    sagas = providers.List(
        providers.Singleton(PrototypeCreationSaga, steps=saga_steps.prototype_creation),
        providers.Singleton(ReferenceLayoutProcessingSaga, steps=saga_steps.reference_layout_processing),
    )
    saga_instance_factory: providers.Singleton[SagaManagerFactory] = providers.Singleton(
        SagaInstanceFactory,
        saga_manager_factory,
        sagas,
    )

    message_dispatcher: providers.Singleton[IMessageConsumer] = providers.Singleton(
        make_message_dispatcher,
        messaging.consumer,
        messaging.producer,
    )

    application: providers.Container[Application] = providers.Container(
        Application,
        config=config,
        repositories=repositories,
        domain_event_publisher=domain_event_publisher,
        saga_instance_factory=saga_instance_factory,
        sagas=sagas,
        services=services,
    )
