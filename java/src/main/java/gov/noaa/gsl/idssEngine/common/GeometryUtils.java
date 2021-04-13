/*******************************************************************************
 * Copyright (c) 2020 Regents of the University of Colorado. All rights reserved.
 *
 * Contributors:
 *     Geary Layne
 *******************************************************************************/
package gov.noaa.gsl.idssEngine.common;

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

    public static Set<Point> getCoords(Geometry geometry, Projection proj) {
        
        Set<Point> coords = new HashSet<>();
        
        for(int i=0; i<geometry.getNumGeometries(); i++) {
            coords.addAll(getCoordsSingle(geometry.getGeometryN(i), proj));
        }
        return coords;        
    }
    
    public static Set<Point> getCoordsSingle(Geometry geometry, Projection proj) {
        
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
                }
          } else {
            int len = bdryCoords.length;
            double[][] xyBdryCoords = new double[len][2];
            for(int i=0; i<len; i++) {
                xyBdryCoords[i] = proj.mapLatLon(bdryCoords[i].y, bdryCoords[i].x);
            }
         
            Set<int[]> coordSet = null;
            switch(geoType) {
                case "Polygon":
                    coordSet = PolyDrawler.drawPolygon(new Polygon(xyBdryCoords, true));
                    break;
                case "LineString":
                    coordSet = PolyDrawler.drawPolyline(new Polyline(xyBdryCoords, true));
                    break;
                default:
                    throw new UnsupportedOperationException("Geometry type ("+geoType+") not currently supported");
            }
            
            coords = new HashSet<>(coordSet.size());
            for(int[] coord : coordSet) coords.add(new Point(coord[0], coord[1]));
        }

        return coords;
    }
}
