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
from math import ceil, floor
from typing import Optional, Tuple, Union

import numpy
from shapely import contains_xy, Geometry, LineString, Point, Polygon, from_wkt

from idsse.common.grid_proj import GridProj, RoundingMethod

logger = logging.getLogger(__name__)


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
    if isinstance(geometry, LineString):
        return rasterize_linestring(geometry, grid_proj, rounding)
    if isinstance(geometry, Polygon):
        return rasterize_polygon(geometry, grid_proj, rounding)
    raise ValueError(f'Passed geometry (type:{type(geometry)}) is not supported')


def rasterize_linestring(
        line_string: Union[str, LineString],
        grid_proj: GridProj = None,
        rounding: RoundingMethod = RoundingMethod.FLOOR
) -> Tuple[numpy.array]:
    """Takes a geographic LineString (specified with lon/lat) and determines all the
    associated pixels in the translated space (as specified by grid_proj).

    Args:
        geometry (Union[str, LineString]): Either a shapely LineString
                                         or a well-known-text representation of a LineString.
        grid_proj (GridProj, optional): A projection (CRS) with scale and offsets. Defaults to None.
        rounding (RoundingMethod, optional): Rounding role for mapping float coordinate values
                                             to integers. Defaults to RoundingMethod.FLOOR.

    Raises:
        ValueError: When the line_string arg does not represent a LineString

    Returns:
        Tuple[numpy.array]: First array represent the x-coordinate and the seconde the y.
    """
    if isinstance(line_string, str):
        line_string = from_wkt(line_string)

    if not isinstance(line_string, LineString):
        raise ValueError(f'Passed geometry is type:{type(line_string)} but must be LineString')

    if grid_proj is not None:
        line_string = geographic_linestring_to_pixel(line_string, grid_proj, rounding)

    return pixels_near_line_string(line_string)


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

    print(grid_proj)
    exterior = [grid_proj.map_geo_to_pixel(*ll, rounding) for ll in poly.exterior.coords]
    interiors = [[grid_proj.map_geo_to_pixel(*ll, rounding) for ll in interior.coords]
                 for interior in poly.interiors]

    pixel_poly = Polygon(exterior, holes=interiors)
    return pixel_poly


def pixels_near_line_string(line_string: LineString,
                            dist: float = 0.25) -> Tuple[numpy.array]:
    """Determine the pixels that are close to a specified LineString

    Args:
        line_string (LineString): Shapely geometry with vertices defined by x,y
        dist (float, optional): Distance cutoff used to determine in a pixel is "near".
                                Defaults to 0.25.

    Returns:
        Tuple[numpy.array]: First array represent the x-coordinate and the seconde the y.
    """
    xmin, ymin, xmax, ymax = line_string.bounds
    xmin = int(floor(xmin))
    xmax = int(ceil(xmax))
    ymin = int(floor(ymin))
    ymax = int(ceil(ymax))

    points = []
    for y_coord in range(ymin, ymax):
        for x_coord in range(xmin, xmax):
            points.append(Point(x_coord, y_coord))

    points_near_line_string = [(pnt.x, pnt.y) for pnt in points if line_string.distance(pnt) < dist]
    return tuple(numpy.array(dim_coord) for dim_coord in map(list, zip(*points_near_line_string)))


def pixels_in_polygon(poly: Polygon) -> Tuple[numpy.ndarray]:
    """Determine the pixels that are within the specified Polygon

    Args:
        poly (Polygon): Shapely geometry with vertices defined by x,y

    Returns:
        Tuple[numpy.array]: First array represent the x-coordinate and the seconde the y.
    """
    xmin, ymin, xmax, ymax = poly.bounds
    xmin = int(floor(xmin))
    xmax = int(ceil(xmax))
    ymin = int(floor(ymin))
    ymax = int(ceil(ymax))

    # create prepared polygon
    # prep_poly = prep(poly)

    # construct a rectangular mesh
    points = []
    for y_coord in range(ymin, ymax):
        for x_coord in range(xmin, xmax):
            points.append((x_coord, y_coord))

    # validate if each point falls inside shape using
    # the prepared polygon
    # points_in_poly = list(filter(prep_poly.contains, points))
    points_in_poly = [pnt for pnt in points if contains_xy(poly, *pnt)]
    return tuple(numpy.array(dim_coord) for dim_coord in map(list, zip(*points_in_poly)))
