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
from math import floor
from typing import List, Optional, Tuple, Union

import numpy
from shapely import Geometry, LinearRing, LineString, Point, Polygon, from_wkt

from idsse.common.grid_proj import GridProj, RoundingMethod
from idsse.common.utils import round_half_away as round_

logger = logging.getLogger(__name__)


Pixel = Tuple[int, int]


def rasterize(
        geometry: Union[str, Geometry],
        grid_proj: GridProj = None,
        rounding: RoundingMethod = RoundingMethod.FLOOR
) -> Tuple[numpy.array]:
    """Takes a geographic geometry (specified with lon/lat) and determines all the
    associated pixels in the translated space (as specified by grid_proj).

    Args:
        geometry (Union[str, Geometry]): Either a shapely Geometry (or sub-class)
                                         or a well-known-text representation of a geometry.
        grid_proj (GridProj, optional): A projection (CRS) with scale and offsets. Defaults to None.
        rounding (RoundingMethod, optional): Rounding role for mapping float coordinate values
                                             to integers. Defaults to RoundingMethod.FLOOR.

    Raises:
        ValueError: When the geometry type is not supported

    Returns:
        Tuple[numpy.array]: First array represent the x-coordinate and the seconde the y.
    """
    if isinstance(geometry, str):
        geometry = from_wkt(geometry)

    if isinstance(geometry, Point):
        return rasterize_point(geometry, grid_proj, rounding)
    if isinstance(geometry, LineString):
        return rasterize_linestring(geometry, grid_proj, rounding)
    if isinstance(geometry, Polygon):
        return rasterize_polygon(geometry, grid_proj, rounding)
    raise ValueError(f'Passed geometry (type:{type(geometry)}) is not supported')


def rasterize_point(
        point: Union[str, Point],
        grid_proj: GridProj = None,
        rounding: RoundingMethod = RoundingMethod.FLOOR
) -> Tuple[numpy.array]:
    """Takes a geographic Point (specified with lon/lat) and determines the
    associated pixel in the translated space (as specified by grid_proj).

    Args:
        point (Union[str, Point]): Either a shapely Point
                                   or a well-known-text representation of a Point.
        grid_proj (GridProj, optional): A projection (CRS) with scale and offsets. Defaults to None.
        rounding (RoundingMethod, optional): Rounding role for mapping float coordinate values
                                             to integers. Defaults to RoundingMethod.FLOOR.

    Raises:
        ValueError: When the line_string arg does not represent a Point

    Returns:
        Tuple[numpy.array]: First array represent the x-coordinate and the seconde the y.
    """
    if isinstance(point, str):
        point = from_wkt(point)

    if not isinstance(point, Point):
        raise ValueError(f'Passed geometry is type:{type(point)} but must be Point')

    if grid_proj is not None:
        return _make_numpy([grid_proj.map_geo_to_pixel(*point.coords[0], rounding)])

    return _make_numpy([_round_x_y(*point.coords[0], rounding)])


def rasterize_linestring(
        linestring: Union[str, LineString],
        grid_proj: GridProj = None,
        rounding: RoundingMethod = RoundingMethod.FLOOR
) -> Tuple[numpy.array]:
    """Takes a geographic LineString (specified with lon/lat) and determines all the
    associated pixels in the translated space (as specified by grid_proj).

    Args:
        linestring (Union[str, LineString]): Either a shapely LineString
                                             or a well-known-text representation of a LineString.
        grid_proj (GridProj, optional): A projection (CRS) with scale and offsets. Defaults to None.
        rounding (RoundingMethod, optional): Rounding role for mapping float coordinate values
                                             to integers. Defaults to RoundingMethod.FLOOR.

    Raises:
        ValueError: When the line_string arg does not represent a LineString

    Returns:
        Tuple[numpy.array]: First array represent the x-coordinate and the seconde the y.
    """
    if isinstance(linestring, str):
        linestring = from_wkt(linestring)

    if not isinstance(linestring, LineString):
        raise ValueError(f'Passed geometry is type:{type(linestring)} but must be LineString')

    if grid_proj is not None:
        linestring = geographic_linestring_to_pixel(linestring, grid_proj, rounding)

    return pixels_for_linestring(linestring)


def rasterize_polygon(
        polygon: Union[str, Polygon],
        grid_proj: GridProj = None,
        rounding: RoundingMethod = RoundingMethod.FLOOR
) -> Tuple[numpy.array]:
    """Takes a geographic Polygon (specified with lon/lat) and determines all the
    associated pixels in the translated space (as specified by grid_proj).

    Args:
        geometry (Union[str, Polygon]): Either a shapely Polygon
                                         or a well-known-text representation of a Polygon.
        grid_proj (GridProj, optional): A projection (CRS) with scale and offsets. Defaults to None.
        rounding (RoundingMethod, optional): Rounding role for mapping float coordinate values
                                             to integers. Defaults to RoundingMethod.FLOOR.

    Raises:
        ValueError: When the polygon arg does not represent a Polygon

    Returns:
        Tuple[numpy.array]: First array represent the x-coordinate and the seconde the y.
    """
    if isinstance(polygon, str):
        polygon = from_wkt(polygon)

    if not isinstance(polygon, Polygon):
        raise ValueError(f'Passed geometry is type:{type(polygon)} but must be Polygon')

    if grid_proj is not None:
        polygon = geographic_polygon_to_pixel(polygon, grid_proj, rounding)

    return pixels_in_polygon(polygon)


def geographic_geometry_to_pixel(
        geo: Geometry,
        grid_proj: GridProj,
        rounding: Optional[RoundingMethod] = None
) -> Geometry:
    """Map a geometry specified in lat/lon space to geometry specified in pixel space

    Args:
        geo (Geometry): Shapely geometry with vertices defined by lon,lat
        grid_proj (GridProj): Projection plus pixel resolution
        rounding (RoundingMethod, optional): One of None, 'floor', 'round'. Defaults to None.

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
    raise ValueError('Passed geometry is not of supported types')


def geographic_linestring_to_pixel(
        line_string: LineString,
        grid_proj: GridProj,
        rounding: RoundingMethod = None
) -> LineString:
    """Map a LineString specified in lat/lon space to geometry specified in pixel space

    Args:
        line_string (LineString): Shapely geometry with vertices defined by lon,lat
        grid_proj (GridProj): Projection plus pixel resolution
        rounding (RoundingMethod, optional): One of None, 'floor', 'round'. Defaults to None.

    Raises:
        ValueError: If geometry is not a LineString
    Returns:
        LineString: Shapely LineString with vertices defined by x,y pixels
    """
    if not isinstance(line_string, LineString):
        raise ValueError(f'Geometry must be a LineString but is a {type(line_string)}')

    coords = [grid_proj.map_geo_to_pixel(*ll, rounding) for ll in line_string.coords]

    pixel_linestring = LineString(coords)
    return pixel_linestring


def geographic_polygon_to_pixel(
        poly: Polygon,
        grid_proj: GridProj,
        rounding: RoundingMethod = None
) -> Polygon:
    """Map a Polygon specified in lat/lon space to geometry specified in pixel space

    Args:
        poly (Polygon): Shapely geometry with vertices defined by lon,lat
        grid_proj (GridProj): Projection plus pixel resolution
        rounding (RoundingMethod, optional): One of None, 'floor', 'round'. Defaults to None.

    Raises:
        ValueError: If geometry is not a LineString
    Returns:
        Polygon: Shapely Polygon with vertices defined by x,y pixels
    """
    if not isinstance(poly, Polygon):
        raise ValueError(f'Geometry must be a Polygon but is a {type(poly)}')

    exterior = [grid_proj.map_geo_to_pixel(*ll, rounding) for ll in poly.exterior.coords]
    interiors = [[grid_proj.map_geo_to_pixel(*ll, rounding) for ll in interior.coords]
                 for interior in poly.interiors]

    pixel_poly = Polygon(exterior, holes=interiors)
    return pixel_poly


def pixels_for_linestring(linestring: LineString) -> Tuple[numpy.array]:
    """Determine the pixels that represent the specified LineString

    Args:
        linestring (LineString): Shapely geometry with vertices defined by x,y in pixel space

    Returns:
        Tuple[numpy.array]: First array represent the x-coordinate and the seconde the y.
    """
    return _make_numpy(_pixels_for_linestring(linestring))


def pixels_in_polygon(poly: Polygon) -> Tuple[numpy.ndarray]:
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


def _make_numpy(points: List[Pixel]) -> Tuple[numpy.ndarray]:
    """Map a list of (x,y) tuples to a tuple of x values (as numpy array) and y values (numpy array)

    Args:
        points (List[Pixel]): list of (x,y) coordinates

    Returns:
        Tuple[numpy.ndarray]: Same coordinates but restructured
    """
    return tuple(numpy.array(dim_coord, dtype=numpy.int64) for dim_coord in map(list, zip(*points)))


def _pixels_for_linestring(
        linestring: LineString
) -> List[Pixel]:
    """Get pixels crossed while traversing a linestring

    Args:
        linestring (LineString): A linestring made of one or more line segments

    Returns:
        List[Pixel]: List of x,y tuples in pixel space
    """
    pixels = _pixels_for_line_seg(linestring.coords[0], linestring.coords[1])
    for pnt1, pnt2 in zip(linestring.coords[1:-1], linestring.coords[2:]):
        pixels.extend(_pixels_for_line_seg(pnt1, pnt2, exclude_first=True))
    return pixels


# pylint: disable=invalid-name
def _pixels_for_line_seg(
        pnt1: Tuple[float, float],
        pnt2: Tuple[float, float],
        exclude_first: bool = False
) -> List[Pixel]:
    """Get pixels crossed while traversing a line segment

    Args:
        pnt1 (Tuple[float, float]): One of the line segment end points in x,y
        pnt2 (Tuple[float, float]): The other line segment end point in x,y
        exclude_first (bool): If true, pnt1 is not included in returned list

    Returns:
        List[Pixel]: List of x,y tuples in pixel space
    """
    x1, y1 = pnt1
    x2, y2 = pnt2
    dx = x2 - x1
    dy = y2 - y1

    pixels = []
    if not exclude_first:
        pixels.append((int(x1), int(y1)))

    slope = float(dy) / float(dx) if dx else 0
    if dx != 0 and -1 <= slope <= 1:
        intercept = y1 - slope * x1
        dx = 1 if x2 > x1 else -1
        while x1 != x2:
            x1 += dx
            y1 = round_(slope * x1 + intercept)
            pixels.append((int(x1), y1))
    else:
        slope = float(dx) / float(dy) if dy else 0
        intercept = x1 - slope * y1
        dy = 1 if y2 > y1 else -1
        while y1 != y2:
            y1 += dy
            x1 = round_(slope * y1 + intercept)
            pixels.append((x1, int(y1)))

    return pixels


# pylint: disable=too-many-locals
def _pixels_for_polygon(
        polygon_boundary: LinearRing
) -> List[Pixel]:
    """Get all pixels in a polygon using a line scan algorithm

    Args:
        polygon_boundary (LineString): The outside of a polygon as linestring, must
                                       repeat first vertex as last, likely generated by
                                       call the polygon.boundary property
    Returns:
        List[Pixel]: List of x,y tuples in pixel space
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


def _round_x_y(x, y, rounding: Union[str, RoundingMethod]) -> Pixel:
    if isinstance(rounding, str):
        rounding = RoundingMethod[rounding.upper()]

    if rounding is RoundingMethod.ROUND:
        return (round_(x), round_(y))
    if rounding is RoundingMethod.FLOOR:
        return (floor(x), floor(y))
    return (int(x), int(y))
