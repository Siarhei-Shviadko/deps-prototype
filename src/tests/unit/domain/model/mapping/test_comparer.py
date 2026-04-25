import pytest

from deps_prototype.domain.model.mapping.allocators import Comparer


@pytest.mark.mappings
@pytest.mark.parametrize(
    "keys,content,expected_result",
    [
        (set(), "content", False),
        ({""}, "content", False),
        ({"con", "tent"}, "content", False),
        ({"content"}, "content ", True),
        ({"content "}, "content", True),
        ({"content\t\n"}, "content\n\t", True),
        ({"content"}, "content", True),
        ({"content", "content"}, "content", True),
        ({"con", "content", "tent"}, "content", True),
        ({"con", "content", "tent"}, "cOnteNt", True),
        ({"con", "cOnteNt", "tent"}, "content", True),
    ],
)
def test_compare__ok(keys, content, expected_result):
    actual_result = Comparer.is_content_satisfying(keys, content)

    assert actual_result == expected_result
