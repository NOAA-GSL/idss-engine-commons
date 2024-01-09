"""Utility module for vector/raster conversion"""
# ----------------------------------------------------------------------------------
# Created on Thu Dec 07 2023
#
# Copyright (c) 2023 Regents of the University of Colorado. All rights reserved. (1)
#
# Contributors:
#     Geary Layne (1)
#
# ----------------------------------------------------------------------------------

import logging
from collections.abc import Iterable, Sequence
from math import floor
from numbers import Number
from typing import NewType

import numpy
from shapely import Geometry, LinearRing, LineString, MultiPolygon, Point, Polygon, from_wkt

from idsse.common.grid_proj import GridProj, RoundingMethod
from idsse.common.utils import round_half_away


logger = logging.getLogger(__name__)


Pixel = NewType('Pixel', Sequence[int])
Coord = NewType('Coord', Sequence[float])
Coords = NewType('Coords', Sequence[Coord])


def rasterize(
        geometry: str | Geometry,
        grid_proj: GridProj | None = None,
        rounding: RoundingMethod = RoundingMethod.FLOOR
) -> tuple[numpy.array]:
    """Takes a geographic geometry (specified with lon/lat) and determines all the
    associated pixels in the translated space (as specified by grid_proj).

    Args:
        geometry (str | Geometry): Either a shapely Geometry (or sub-class)
                                   or a well-known-text representation of a geometry.
        grid_proj (GridProj | None): A projection (CRS) with scale and offsets. Defaults to None.
        rounding (RoundingMethod | None): Rounding role for mapping float coordinate values
                                             to integers. Defaults to RoundingMethod.FLOOR.

    Raises:
        TypeError: When the geometry type is not supported

    Returns:
        tuple[numpy.array]: First array represent the x-coordinate and the seconde the y.
    """
    if isinstance(geometry, str):
        geometry = from_wkt(geometry)

    if isinstance(geometry, Point):
        return rasterize_point(geometry, grid_proj, rounding)
    if isinstance(geometry, LineString):
        return rasterize_linestring(geometry, grid_proj, rounding)
    if isinstance(geometry, Polygon):
        return rasterize_polygon(geometry, grid_proj, rounding)
    if isinstance(geometry, MultiPolygon):
        x_coords = numpy.empty(0, dtype=numpy.int32)
        y_coords = numpy.empty(0, dtype=numpy.int32)
        for poly in geometry.geoms:
            poly_coords = rasterize_polygon(poly, grid_proj, rounding)
            x_coords = numpy.concatenate((x_coords, poly_coords[0]))
            y_coords = numpy.concatenate((y_coords, poly_coords[1]))

        return x_coords, y_coords

    raise TypeError(f'Passed geometry is type:{type(geometry)}, which is not supported')


def rasterize_point(
        point: str | Coord | Point,
        grid_proj: GridProj | None = None,
        rounding: RoundingMethod = RoundingMethod.FLOOR
) -> tuple[numpy.array]:
    """Takes a geographic Point (specified with lon/lat) and determines the
    associated pixel in the translated space (as specified by grid_proj).

    Args:
        point (str | Coord | Point): Either a 2D coordinate, a shapely Point,
                                          or a well-known-text representation of a Point.
        grid_proj (GridProj | None): A projection (CRS) with scale and offsets. Defaults to None.
        rounding (RoundingMethod |  None): Rounding role for mapping float coordinate values
                                           to integers. Defaults to RoundingMethod.FLOOR.

    Raises:
        TypeError: When the point arg does not represent a Point

    Returns:
        Tuple[numpy.array]: First array represent the x-coordinate and the seconde the y.
    """
    if isinstance(point, str):
        point = from_wkt(point)

    if isinstance(point, Point):
        coord = point.coords[0]
    elif _is_coord(point):
        coord = point
    else:
        raise TypeError(f'Passed geometry is type:{type(point)}, but must be Point')

    if grid_proj is not None:
        return _make_numpy([grid_proj.map_geo_to_pixel(*coord, rounding)])

    return _make_numpy([_round(*coord, rounding=rounding)])


def rasterize_linestring(
        linestring: str | Sequence[Coord] | LineString,
        grid_proj: GridProj | None = None,
        rounding: RoundingMethod = RoundingMethod.FLOOR
) -> tuple[numpy.array]:
    """Takes a geographic LineString (specified with lon/lat) and determines all the
    associated pixels in the translated space (as specified by grid_proj).

    Args:
        linestring (str | Sequence[Coord] | LineString): Either a sequence of coords, a shapely
                                                         LineString, or a well-known-text
                                                         representation of a LineString.
        grid_proj (GridProj | None): A projection (CRS) with scale and offsets. Defaults to None.
        rounding (RoundingMethod | None): Rounding role for mapping float coordinate values
                                          to integers. Defaults to RoundingMethod.FLOOR.

    Raises:
        TypeError: When the line_string arg does not represent a LineString

    Returns:
        tuple[numpy.array]: First array represent the x-coordinate and the seconde the y.
    """
    if isinstance(linestring, str):
        linestring = from_wkt(linestring)

    if isinstance(linestring, Polygon):
        x_coords, y_coords = rasterize_linestring(linestring.exterior)
        for interior in linestring.interiors:
            interior_coords = rasterize_linestring(interior)
            x_coords = numpy.concatenate((x_coords, interior_coords[0]))
            y_coords = numpy.concatenate((y_coords, interior_coords[1]))
        return x_coords, y_coords

    if isinstance(linestring, MultiPolygon):
        x_coords = numpy.empty(0, dtype=numpy.int32)
        y_coords = numpy.empty(0, dtype=numpy.int32)
        for poly in linestring.geoms:
            interior_coords = rasterize_linestring(poly)
            x_coords = numpy.concatenate((x_coords, interior_coords[0]))
            y_coords = numpy.concatenate((y_coords, interior_coords[1]))
        return x_coords, y_coords

    if isinstance(linestring, LineString):
        coords = linestring.coords
    elif _is_coords(linestring):
        coords = linestring
    else:
        raise TypeError(f'Passed geometry is type:{type(linestring)}, but must be LineString')

    if grid_proj is not None:
        linestring = geographic_linestring_to_pixel(coords, grid_proj, rounding)
    else:
        linestring = LineString([_round(*coord, rounding=rounding) for coord in linestring.coords])

    return pixels_for_linestring(linestring)


def rasterize_polygon(
        polygon: str | Sequence[Coords] | Polygon,
        grid_proj: GridProj | None = None,
        rounding: RoundingMethod = RoundingMethod.FLOOR
) -> tuple[numpy.array]:
    """Takes a geographic Polygon (specified with lon/lat) and determines all the
    associated pixels in the translated space (as specified by grid_proj).

    Args:
        geometry (str | Sequence[Coords] | Polygon): Either a sequence of coords, a shapely Polygon,
                                                   or a well-known-text representation of a Polygon.
        grid_proj (GridProj | None): A projection (CRS) with scale and offsets. Defaults to None.
        rounding (RoundingMethod | None): Rounding role for mapping float coordinate values
                                             to integers. Defaults to RoundingMethod.FLOOR.

    Raises:
        TypeError: When the polygon arg does not represent a Polygon

    Returns:
        Tuple[numpy.array]: First array represent the x-coordinate and the seconde the y.
    """
    if isinstance(polygon, str):
        polygon = from_wkt(polygon)

    if isinstance(polygon, Polygon):
        coords = [list(interior.coords) for interior in polygon.interiors]
        coords.insert(0, list(coord for coord in polygon.exterior.coords))
    elif all(_is_coords(coords) for coords in polygon):
        coords = polygon
    else:
        raise TypeError(f'Passed geometry is type:{type(polygon)}, but must be Polygon')

    if grid_proj is not None:
        polygon = geographic_polygon_to_pixel(coords, grid_proj, rounding)
    else:
        coords = [[_round(*coord, rounding=rounding)
                  for coord in ring] for ring in coords]
        polygon = Polygon(coords[0], holes=coords[1:])

    return pixels_in_polygon(polygon)


def geographic_to_pixel(
        geo: Geometry,
        grid_proj: GridProj,
        rounding: RoundingMethod | None = None
) -> Geometry:
    """Map a geometry specified in lat/lon space to geometry specified in pixel space

    Args:
        geo (Geometry): Shapely geometry with vertices defined by lon,lat
        grid_proj (GridProj): Projection plus pixel resolution
        rounding (RoundingMethod | None): One of None, 'floor', 'round'. Defaults to None.

    Raises:
        ValueError: If geometry type is not currently supported

    Returns:
        Geometry: Shapely geometry of the same type as input geometry with vertices
                    defined by x,y pixels
    """
    if isinstance(geo, LineString):
        return geographic_linestring_to_pixel(geo, grid_proj, rounding)
    if isinstance(geo, Polygon):
        return geographic_polygon_to_pixel(geo, grid_proj, rounding)
    if isinstance(geo, MultiPolygon):
        return MultiPolygon([geographic_polygon_to_pixel(poly, grid_proj, rounding)
                             for poly in geo.geoms])

    raise ValueError(f'Passed geometry is type:{type(geo)}, which is not of supported types')


def geographic_linestring_to_pixel(
        linestring: LineString | Sequence[Coord],
        grid_proj: GridProj,
        rounding: RoundingMethod | None = None
) -> LineString:
    """Map a LineString specified in lat/lon space to geometry specified in pixel space

    Args:
        linestring (LineString | Sequence[Coord]): Shapely geometry with vertices defined by lon,lat
        grid_proj (GridProj): Projection plus pixel resolution
        rounding (RoundingMethod | None): One of None, 'floor', 'round'. Defaults to None.

    Raises:
        TypeError: If geometry is not a LineString
    Returns:
        LineString: Shapely LineString with vertices defined by x,y pixels
    """
    if _is_coords(linestring):
        coords = linestring
    elif isinstance(linestring, LineString):
        coords = linestring.coords
    else:
        raise TypeError(f'Geometry must be a LineString but is a {type(linestring)}')

    # coords = [grid_proj.map_geo_to_pixel(*ll, rounding) for ll in line_string.coords]
    coords = list(zip(*grid_proj.map_geo_to_pixel(*list(zip(*coords)), rounding)))

    pixel_linestring = LineString(coords)
    return pixel_linestring


def geographic_polygon_to_pixel(
        poly: Polygon | Sequence[Coords],
        grid_proj: GridProj,
        rounding: RoundingMethod | None = None
) -> Polygon:
    """Map a Polygon specified in lat/lon space to geometry specified in pixel space

    Args:
        poly (Polygon | Sequence[Coords]): A sequence of coords used as the exterior of the polygon,
                                        or Shapely geometry, either with vertices defined by lon,lat
        grid_proj (GridProj): Projection plus pixel resolution
        rounding (RoundingMethod | None): One of None, 'floor', 'round'. Defaults to None.

    Raises:
        TypeError: If geometry is not a LineString
    Returns:
        Polygon: Shapely Polygon with vertices defined by x,y pixels
    """
    if isinstance(poly, Polygon):
        exterior = poly.exterior.coords
        interiors = poly.interiors
    elif all(_is_coords(coords) for coords in poly):
        exterior = poly[0]
        interiors = poly[1:]
    else:
        raise TypeError(f'Geometry must be a Polygon but is a {type(poly)}')

    exterior = list(zip(*grid_proj.map_geo_to_pixel(*list(zip(*exterior)), rounding)))
    interiors = [list(zip(*grid_proj.map_geo_to_pixel(*list(zip(*interior.coords)), rounding)))
                 for interior in interiors]

    pixel_poly = Polygon(exterior, holes=interiors)
    return pixel_poly


def pixels_for_linestring(linestring: LineString) -> tuple[numpy.array]:
    """Determine the pixels that represent the specified LineString

    Args:
        linestring (LineString): Shapely geometry with vertices defined by x,y in pixel space

    Returns:
        Tuple[numpy.array]: First array represent the x-coordinate and the seconde the y.
    """
    return _make_numpy(_pixels_for_linestring(linestring))


def pixels_in_polygon(poly: Polygon) -> tuple[numpy.ndarray]:
    """Determine the pixels that represent the specified Polygon

    Args:
        poly (Polygon): Shapely geometry with vertices defined by x,y in pixel space

    Returns:
        Tuple[numpy.array]: First array represent the x-coordinate and the seconde the y.
    """
    pixels = _pixels_for_polygon(poly.exterior)
    for inner in poly.interiors:
        pixels_on_inner_edge = _pixels_for_linestring(inner)
        for pixel in _pixels_for_polygon(inner):
            if pixel not in pixels_on_inner_edge:
                pixels.remove(pixel)

    return _make_numpy(pixels)


def _make_numpy(points: Sequence[Pixel]) -> tuple[numpy.ndarray]:
    """Map a list of (x,y) tuples to a tuple of x values (as numpy array) and y values (numpy array)

    Args:
        points (Sequence[Pixel]): list of (x,y) coordinates

    Returns:
        Tuple[numpy.ndarray]: Same coordinates but restructured
    """
    return tuple(numpy.array(dim_coord, dtype=numpy.int64) for dim_coord in map(list, zip(*points)))


def _pixels_for_linestring(
        linestring: LineString
) -> list[Pixel]:
    """Get pixels crossed while traversing a linestring

    Args:
        linestring (LineString): A linestring made of one or more line segments

    Returns:
        list[Pixel]: List of x,y tuples in pixel space
    """
    coords = linestring.coords
    pixels = _pixels_for_line_seg(coords[0], coords[1])
    for pnt1, pnt2 in zip(coords[1:-1], coords[2:]):
        pixels.extend(_pixels_for_line_seg(pnt1, pnt2, exclude_first=True))
    return pixels


# pylint: disable=invalid-name
def _pixels_for_line_seg(
        pnt1: tuple[int, int],
        pnt2: tuple[int, int],
        exclude_first: bool = False
) -> list[Pixel]:
    """Get pixels crossed while traversing a line segment

    Args:
        pnt1 (Pixel): One of the line segment end points in x,y
        pnt2 (Pixel): The other line segment end point in x,y
        exclude_first (bool): If true, pnt1 is not included in returned list

    Returns:
        list[Pixel]: List of x,y tuples in pixel space
    """
    x1, y1 = pnt1
    x2, y2 = pnt2

    if int(x1) != x1 or int(x2) != x2 or int(y1) != y1 or int(y2) != y2:
        raise TypeError('Line segment end points coordinates must be integers')
    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

    dx = x2 - x1
    dy = y2 - y1

    if abs(dy) <= abs(dx):
        slope = dy / dx if dx != 0 else 0
        intercept = y1 - slope * x1
        step = 1 if x1 < x2 else -1
        if exclude_first:
            x1 += step
        pixels = [(x, round_half_away(slope * x + intercept)) for x in range(x1, x2+step, step)]
    else:
        slope = dx / dy
        intercept = x1 - slope * y1
        step = 1 if y1 < y2 else -1
        if exclude_first:
            y1 += step
        pixels = [(round_half_away(slope * y + intercept), y) for y in range(y1, y2+step, step)]

    return pixels


# pylint: disable=too-many-locals
def _pixels_for_polygon(
        polygon_boundary: LinearRing
) -> list[Pixel]:
    """Get all pixels in a polygon using a line scan algorithm

    Args:
        polygon_boundary (LineString): The outside of a polygon as linestring, must
                                       repeat first vertex as last, likely generated by
                                       call the polygon.boundary property
    Returns:
        list[Pixel]: List of x,y tuples in pixel space
    """
    xmin, ymin, _, ymax = polygon_boundary.bounds
    x_offset = 0 if xmin >= 0 else int(1-xmin)
    ymin = floor(ymin)
    ymax = floor(ymax)

    edge_info = []
    for (x1, y1), (x2, y2) in zip(polygon_boundary.coords[:-1], polygon_boundary.coords[1:]):
        int_y1, int_y2 = int(y1), int(y2)
        if int_y1 != int_y2:  # only need to include if y values differ
            if int_y1 > int_y2:  # need to swap order so y1 < y2
                x1, x2 = x2, x1
                y1, y2 = y2, y1
                int_y1, int_y2 = int_y2, int_y1

            edge_info.append((int_y1, int_y2, x1+x_offset, (x2 - x1)/(y2 - y1)))

    pixels = []
    for y in range(ymin, ymax+1):
        x_list = []
        for y1, y2, x, slope in edge_info:
            if y1 <= y <= y2:
                x_list.append(int(x + (y-y1) * slope))

        x_list.sort()

        for x1, x2 in zip(x_list[:-1], x_list[1:]):
            pixels.extend([(x, y) for x in range(x1-x_offset, x2-x_offset+1)])

    return pixels


def _is_coord(arg) -> bool:
    return isinstance(arg, Iterable) and all(isinstance(v, Number) for v in arg)


def _is_coords(arg) -> bool:
    return isinstance(arg, Iterable) and all(_is_coord(v) for v in arg)


def _round(*args, rounding: str | RoundingMethod) -> list[int]:
    if isinstance(rounding, str):
        rounding = RoundingMethod[rounding.upper()]

    if rounding is RoundingMethod.ROUND:
        return [round_half_away(v) for v in args]
    if rounding is RoundingMethod.FLOOR:
        return [floor(v) for v in args]
    return [int(v) for v in args]
