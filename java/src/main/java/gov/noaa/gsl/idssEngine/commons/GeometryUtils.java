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

import gov.noaa.gsd.fiqas.cartography.GreatCircle;
import gov.noaa.gsd.fiqas.cartography.Projection;
import gov.noaa.gsd.fiqas.math.coord.cartesian.Polygon;
import gov.noaa.gsd.fiqas.math.coord.cartesian.Polyline;
import gov.noaa.gsd.fiqas.util.grid.tool.MathMorph;
import gov.noaa.gsd.fiqas.util.grid.tool.RadialHood;
import gov.noaa.gsd.fiqas.util.image.draw.PolyDrawler;
import gov.noaa.gsl.idssEngine.commons.aspect.Units;

public class GeometryUtils {

    public static GeoCoords getCoords(Geometry geometry, Projection proj) {
        return getCoords(geometry, proj, 0);
    }
    
    public static GeoCoords getCoords(Geometry geometry, Projection proj, double dilateRadius) {
      
        int numGeo = geometry.getNumGeometries();
        
        if(numGeo==1) return addCoords(geometry, proj, dilateRadius, null);
        
        GeoCoords geoCoords = addCoords(geometry.getGeometryN(0), proj, dilateRadius, null);
        
        for(int i=1; i<geometry.getNumGeometries(); i++) {
            addCoords(geometry.getGeometryN(i), proj, dilateRadius, geoCoords);
        }
        return geoCoords;        
    }
    
    public static GeoCoords addCoords(Geometry geometry, Projection proj, GeoCoords geoCoords) {
        return addCoords(geometry, proj, 0, geoCoords);
    }
    
    public static GeoCoords addCoords(Geometry geometry, Projection proj, double dilateRadius, GeoCoords geoCoords) {
        
        Coordinate[] bdryCoords =  geometry.getCoordinates();

        String geoType = geometry.getGeometryType();
//System.out.println(geoType);
//System.exit(0);
          if(geoType.equals("Point")) {
                int[] coord = proj.mapLatLonToPixel(bdryCoords[0].y, bdryCoords[0].x);
                if(coord != null) {
                    Set<Point> coordSet = new HashSet<>();
                    Set<int[]> hood = RadialHood.getOffsets(dilateRadius, true);
                    final int x = coord[0], y = coord[1];
                    for(int[] offset : hood)
                                coordSet.add(new Point(x+offset[0], y+offset[1]));
                    if(geoCoords == null)
                        return new GeoCoords(coordSet);
                    return geoCoords.add(coordSet);
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
//System.out.printf("%s, (%f, %f) -> (%f, %f)\n", proj.getProjSpec(), bdryCoords[i].y, bdryCoords[i].x, xy[0], xy[1]);
                final double x=xy[0];
                final double y=xy[1];
                if(minX>x) minX=x;
                if(maxX<x) maxX=x;
                if(minY>y) minY=y;
                if(maxY<y) maxY=y;
                xyBdryCoords[i] = xy;
            }
         
            switch(geoType) {
                case "Polygon":
//System.out.println("polygon");
                    int xOffset = (int)minX;
                    int yOffset = (int)minY;
                    int width = (int)maxX-xOffset+1;
                    int height = (int)maxY-yOffset+1;
                    for(int i=0; i<len; i++) {
                        xyBdryCoords[i][0] -= xOffset;
                        xyBdryCoords[i][1] -= yOffset;
                    }
                    byte[][] grid = PolyDrawler.drawPolygon(new Polygon(xyBdryCoords, true), (byte)1, width, height);
                    grid = MathMorph.dilate(grid, dilateRadius);
//GridSummary.printDistribution(grid);

                    if(geoCoords == null)
                        return new GeoCoords(xOffset, yOffset, grid);
                    return geoCoords.add(xOffset, yOffset, grid);
//                {
//                    Set<int[]> coords = PolyDrawler.drawPolygon(new Polygon(xyBdryCoords, true));
//                    Set<Point> coordSet = new HashSet<>(coords.size());
//                    for(int[] coord : coords) {
////System.out.println("\t"+Arrays.toString(coord));
//                        coordSet.add(new Point(coord[0], coord[1]));
//                    }
//System.out.println("coordSet size: "+coordSet.size());
//                    if(geoCoords == null)
//                        return new GeoCoords(coordSet);
//                    return geoCoords.add(coordSet);
//                }   
                case "LineString":
//System.out.println("lineString");
                    Set<int[]> coords = PolyDrawler.drawPolyline(new Polyline(xyBdryCoords, true));
                    Set<Point> coordSet = new HashSet<>(coords.size());
                    if(dilateRadius==0)
                        for(int[] coord : coords) coordSet.add(new Point(coord[0], coord[1]));
                    else {
                        Set<int[]> hood = RadialHood.getOffsets(dilateRadius, true);
System.out.println("hood size: "+hood.size());
                        for(int[] coord : coords) {
                            final int x = coord[0], y = coord[1];
                            for(int[] offset : hood)
                                coordSet.add(new Point(x+offset[0], y+offset[1]));
                        }
                    }
                    if(geoCoords == null)
                        return new GeoCoords(coordSet);
                    return geoCoords.add(coordSet);
                    
                default:
                    throw new UnsupportedOperationException("Geometry type ("+geoType+") not currently supported");
            }
        }
        return null;
    }
}
