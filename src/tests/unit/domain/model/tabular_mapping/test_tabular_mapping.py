import pytest

from deps_prototype.domain.model import HeaderType, IllegalArgumentError, TabularMapping
from deps_prototype.domain.model import TabularMappingFactory as DomainTMFactory
from tests.factories import TabularMappingFactory


@pytest.mark.tabular_mappings
def test_tabular_mapping_init():
    mapping_: TabularMapping = TabularMappingFactory()

    assert mapping_.headers


@pytest.mark.tabular_mappings
def invalid_headers_number__no_headers():
    with pytest.raises(IllegalArgumentError):
        _ = DomainTMFactory.create(
            code="test_code",
            prototype_id="test_prototype_id",
            header_type=HeaderType.ROWS,
            headers=[],
            occurrence_index=0,
        )


@pytest.mark.tabular_mappings
def invalid_aliases_number__no_aliases():
    with pytest.raises(IllegalArgumentError):
        _ = DomainTMFactory.create(
            code="test_code",
            prototype_id="test_prototype_id",
            header_type=HeaderType.ROWS,
            headers=[
                {
                    "name": "test_header",
                    "aliases": set(),
                },
            ],
            occurrence_index=0,
        )
