from dataclasses import dataclass

from deps_extracted_data import Bbox

__all__ = ["Point", "Polygon"]


@dataclass
class Point:
    x: float
    y: float

    @classmethod
    def from_dict(cls, point: dict[str, float]) -> "Point":
        return cls(x=point["x"], y=point["y"])


@dataclass
class Polygon:
    points: list[Point]

    @property
    def xs(self) -> list[float]:
        return [point.x for point in self.points]

    @property
    def ys(self) -> list[float]:
        return [point.y for point in self.points]

    @classmethod
    def from_dict(cls, points: list[dict[str, float]]) -> "Polygon":
        return cls([Point.from_dict(point) for point in points])

    def to_bbox(self) -> Bbox:
        x = min(self.xs)
        y = min(self.ys)

        return Bbox(x=x, y=y, w=max(self.xs) - x, h=max(self.ys) - y)
