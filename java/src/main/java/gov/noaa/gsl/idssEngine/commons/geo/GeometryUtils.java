/*******************************************************************************
 * Copyright (c) 2020 Regents of the University of Colorado. All rights reserved.
 *
 * Contributors:
 *     Geary Layne
 *******************************************************************************/
package gov.noaa.gsl.idssEngine.commons.geo;

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

public class GeometryUtils {

    public static GeoCoords getCoords(Geometry geometry, Projection proj) {
        return getCoords(geometry, proj, 0);
    }
    
    public static GeoCoords getCoords(Geometry geometry, Projection proj, double dilateRadiusInKm) {
      
        int numGeo = geometry.getNumGeometries();
        
        if(numGeo==1) return addCoords(geometry, proj, dilateRadiusInKm, null);
        
        GeoCoords geoCoords = addCoords(geometry.getGeometryN(0), proj, dilateRadiusInKm, null);
        
        for(int i=1; i<geometry.getNumGeometries(); i++) {
            addCoords(geometry.getGeometryN(i), proj, dilateRadiusInKm, geoCoords);
        }
        return geoCoords;        
    }
    
    public static GeoCoords addCoords(Geometry geometry, Projection proj, GeoCoords geoCoords) {
        return addCoords(geometry, proj, 0, geoCoords);
    }
    
    public static GeoCoords addCoords(Geometry geometry, Projection proj, double dilateRadiusInKm, GeoCoords geoCoords) {
        
        Coordinate[] bdryCoords =  geometry.getCoordinates();
        
        if(geometry instanceof org.locationtech.jts.geom.Point) {
          
            if(geometry instanceof Circle) 
                dilateRadiusInKm += ((Circle)geometry).radius;
            else if(geometry instanceof Annulus) 
                dilateRadiusInKm += ((Annulus)geometry).outerRadius;
            
            int[] coord = proj.mapLatLonToPixel(bdryCoords[0].y, bdryCoords[0].x);
            double dilateRadiusInPixel = getDistInPixel(proj, coord, dilateRadiusInKm);
           
            if(coord != null) {
                Set<Point> coordSet = new HashSet<>();
                Set<int[]> hood = RadialHood.getOffsets(dilateRadiusInPixel, true);
                final int x = coord[0], y = coord[1];
                for(int[] offset : hood) {
                    coordSet.add(new Point(x+offset[0], y+offset[1]));
                }
                
                //remove inner hole, mind dilateRadius
                if(geometry instanceof Annulus) {
                    double radiusInKm = ((Annulus)geometry).outerRadius - dilateRadiusInKm;
                    dilateRadiusInPixel = getDistInPixel(proj, coord, radiusInKm);
                    hood = RadialHood.getOffsets(dilateRadiusInPixel, true);
                    for(int[] offset : hood) {
                        coordSet.remove(new Point(x+offset[0], y+offset[1]));
                    }
                }
                
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
         
          double dilateRadiusInPixel = getDistInPixel(proj, bdryCoords[0], dilateRadiusInKm);
          
          String geoType = geometry.getGeometryType();
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
         
//System.out.println("dilateRadius: "+dilateRadius);
                  if(dilateRadiusInPixel>=1.)
                      grid = MathMorph.dilate(grid, dilateRadiusInPixel);
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
                  if(dilateRadiusInKm==0)
                      for(int[] coord : coords) coordSet.add(new Point(coord[0], coord[1]));
                  else {
                      Set<int[]> hood = RadialHood.getOffsets(dilateRadiusInPixel, true);
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

    private static double getDistInPixel(Projection proj, Coordinate coord, double distInKm) {
        int[] xyCoord = proj.mapLatLonToPixel(coord.y, coord.x);
        return getDistInPixel(proj, xyCoord, distInKm);
    }
    private static double getDistInPixel(Projection proj, int[] pixelCoord, double distInKm) {
        int x = pixelCoord[0];
        int y = pixelCoord[1];
        double[] latLon1 = proj.mapXY(x, y);
        double[] latLon2 = proj.mapXY(x+1, y+1);
        return distInKm/(GreatCircle.getDistance(latLon1, latLon2)/Math.sqrt(2));
    }
}
