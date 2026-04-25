import pytest

from deps_prototype.domain.model import Point, Polygon


@pytest.mark.point
def test_to_bbox__two_points__ok():
    point1 = Point(x=0.1, y=0.3)
    point2 = Point(x=0.4, y=0.2)

    bbox = Polygon(points=[point1, point2]).to_bbox()

    assert bbox.x == point1.x
    assert bbox.y == point2.y
    assert bbox.w == point2.x - point1.x
    assert bbox.h == point1.y - point2.y


@pytest.mark.point
def test_to_bbox__three_points__ok():
    point1 = Point(x=0.1, y=0.3)
    point2 = Point(x=0.4, y=0.2)
    point3 = Point(x=0.2, y=0.2)

    bbox = Polygon(points=[point1, point2, point3]).to_bbox()

    assert bbox.x == point1.x
    assert bbox.y == point2.y
    assert bbox.w == point2.x - point1.x
    assert bbox.h == point1.y - point2.y


@pytest.mark.point
def test_to_bbox__four_points__ok():
    point1 = Point(x=0.1, y=0.3)
    point2 = Point(x=0.1, y=0.6)
    point3 = Point(x=0.5, y=0.3)
    point4 = Point(x=0.4, y=0.2)

    bbox = Polygon(points=[point1, point2, point3, point4]).to_bbox()

    assert bbox.x == point1.x
    assert bbox.y == point4.y
    assert bbox.w == point3.x - point1.x
    assert bbox.h == point2.y - point4.y


@pytest.mark.point
def test_to_bbox__five_points__ok():
    point1 = Point(x=0.1, y=0.3)
    point2 = Point(x=0.4, y=0.2)
    point3 = Point(x=0.5, y=0.2)
    point4 = Point(x=0.4, y=0.9)
    point5 = Point(x=0.4, y=0.1)

    bbox = Polygon(points=[point1, point2, point3, point4, point5]).to_bbox()

    assert bbox.x == point1.x
    assert bbox.y == point5.y
    assert bbox.w == point3.x - point1.x
    assert bbox.h == point4.y - point5.y
