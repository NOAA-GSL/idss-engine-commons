/*******************************************************************************
 * Copyright (c) 2020 Regents of the University of Colorado. All rights reserved.
 *
 * Contributors:
 *     Geary Layne
 *******************************************************************************/
package gov.noaa.gsl.idssEngine.commons;

import java.awt.Point;
import java.util.HashSet;
import java.util.Set;

import org.locationtech.jts.geom.Coordinate;
import org.locationtech.jts.geom.Geometry;

import gov.noaa.gsd.fiqas.cartography.Projection;
import gov.noaa.gsd.fiqas.math.coord.cartesian.Polygon;
import gov.noaa.gsd.fiqas.math.coord.cartesian.Polyline;
import gov.noaa.gsd.fiqas.util.image.draw.PolyDrawler;

public class GeometryUtils {

//    public static GeoCoords getCoords(Geometry geometry, Projection proj) {
//        
//        Set<Point> coords = new HashSet<>();
//        
//        for(int i=0; i<geometry.getNumGeometries(); i++) {
//            coords.addAll(getCoordsSingle(geometry.getGeometryN(i), proj));
//        }
//        return coords;        
//    }
    
    public static GeoCoords getCoordsSingle(Geometry geometry, Projection proj) {
        
        Set<Point> coords = null;
        
        Coordinate[] bdryCoords =  geometry.getCoordinates();

        String geoType = geometry.getGeometryType();
//System.out.println(geoType);
//System.exit(0);
          if(geoType.equals("Point")) {
                int[] coord = proj.mapLatLonToPixel(bdryCoords[0].y, bdryCoords[0].x);
                if(coord != null) {
                    coords = new HashSet<>();
                    coords.add(new Point(coord[0], coord[1]));
                    return new GeoCoords(coords);
                }
          } else {
            int len = bdryCoords.length;
            double[][] xyBdryCoords = new double[len][2];
            double[] xy = proj.mapLatLon(bdryCoords[0].y, bdryCoords[0].x);
            xyBdryCoords[0] = xy;
            double minX=xy[0], maxX=xy[0];
            double minY=xy[1], maxY=xy[1];
            for(int i=1; i<len; i++) {
                xy = proj.mapLatLon(bdryCoords[i].y, bdryCoords[i].x);
                final double x=xy[0];
                final double y=xy[1];
                if(minX>x) minX=x;
                if(maxX<x) maxX=x;
                if(minY>y) minY=y;
                if(maxY<y) maxY=y;
                xyBdryCoords[i] = xy;
            }
         
            Set<int[]> coordSet = null;
            switch(geoType) {
                case "Polygon":
                    int xOffset = (int)minX;
                    int yOffset = (int)minY;
                    int width = (int)maxX-xOffset+1;
                    int height = (int)maxY-yOffset+1;
                    byte[][] grid = PolyDrawler.drawPolygon(new Polygon(xyBdryCoords, true), (byte)1, width, height);
                    return new GeoCoords(xOffset, yOffset, grid);
                case "LineString":
                    coordSet = PolyDrawler.drawPolyline(new Polyline(xyBdryCoords, true));
                    coords = new HashSet<>(coordSet.size());
                    for(int[] coord : coordSet) coords.add(new Point(coord[0], coord[1]));
                    return new GeoCoords(coords);
                default:
                    throw new UnsupportedOperationException("Geometry type ("+geoType+") not currently supported");
            }
        }
        return null;
    }
}
