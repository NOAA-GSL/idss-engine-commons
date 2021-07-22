/*******************************************************************************
 * Copyright (c) 2020 Regents of the University of Colorado. All rights reserved.
 *
 * Contributors:
 *     Geary Layne
 *******************************************************************************/
package gov.noaa.gsl.idssEngine.common;

import java.awt.Point;
import java.util.Arrays;
import java.util.Collection;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Iterator;
import java.util.Map;
import java.util.Set;

import org.locationtech.jts.geom.Geometry;

import gov.noaa.gsd.fiqas.cartography.Projection;

public class GeoSummary {
    
    private double[] data=null;
    private double min=Double.NaN;
    private double max=Double.NaN;
    private double above = Double.NaN;
    private double below = Double.NaN;
    private double count = Double.NaN;
    private double thresh1 = Double.NaN;
    private double thresh2 = Double.NaN;
    
    public GeoSummary(double max, double pCov) {
        this(Double.NaN, max, pCov, 1);
    }
    public GeoSummary(double min, double max, double pCov, double size) {
        this.max=max;
        this.above=pCov;
        this.count=size;
    }
    
    public GeoSummary(Collection<Double> data) {
        init(data);
    }

    public GeoSummary(double[] data) {
        init(data);
    }
    
    public GeoSummary(Set<Point> coords, float[][] criteriaGrid) {
        this(coords, criteriaGrid, 0, 0);
    }
//    public GeoSummary(int[][] coords, float[][] criteriaGrid, double thresh) {
//        if(coords != null && criteriaGrid != null) {
//        
//            int len = coords.length;
//            if(len != 0) {
//                double[] data = new double[len];
//                for(int i=0; i<len; i++) {
//                    int[] coord = coords[i];
//                    data[i] = (double)criteriaGrid[coord[0]][coord[1]];
//                }
//                init(data, thresh);
//            }
//        }
//    }
    
    public GeoSummary(Set<Point> coords, float[][] criteriaGrid, double thresh1, double thresh2) {
        if(coords != null && criteriaGrid != null) {
        
            int len = coords.size();
            if(len != 0) {
                double[] data = new double[len];
                int idx = 0; 
                for(Point coord : coords) {
                    data[idx++] = (double)criteriaGrid[coord.x][coord.y];
                }
                init(data, thresh1, thresh2);
            }
        }
    }
    
    public GeoSummary(Geometry geometry, Projection proj, float[][] criteriaGrid) {
        this(getCoords(geometry, proj), criteriaGrid);
    }

    public GeoSummary(Set<Point> coords, Map<Point, float[]> criteriaData, double thresh1, double thresh2) {
        if(coords != null && criteriaData != null) {
            int numCoords = coords.size();
            if(numCoords != 0) {
                double[] data = new double[numCoords];
                int idx = 0; 
                for(Point coord : coords) {
                    float[] values = criteriaData.get(coord);
                    if(values!=null) {
                        int len = values.length;
                        if(len>1) data = Arrays.copyOf(data, data.length+len-1);
                        for(float v : values) {
                            data[idx++] = (double)v;
                        }
                    }
                }
                init(data, thresh1, thresh2);
            }
        }
    }
    
    private void init(Collection<Double> data) {
        init(data, 0, 0);
    }
    private void init(Collection<Double> data, double thresh1, double thresh2) {        
        int len = data.size();
        
        Iterator<Double> it = data.iterator();
        this.thresh1 = thresh1;
        this.thresh2 = thresh2;
        this.data = new double[len];
        min = max = Double.NaN;
        count = above = below = 0;
        
        int idx = 0;
        while(it.hasNext()) { // find first finite value
            final double v = it.next();
            this.data[idx++] = v;
            if(Double.isFinite(v)) {
                count++;
                min = max = v;
                if(v<thresh1) below++;
                else if(v>thresh2) above++;
                break;
            }
        }
        while(it.hasNext()) { // iterate over rest checking for finite
            final double v = it.next();
            this.data[idx++] = v;
            if(Double.isFinite(v)) {
                count++;
                if(min>v) min=v;
                if(max<v) max=v;
                if(v<thresh1) below++;
                else if(v>thresh2) above++;
            }
        }
    }

    private void init(double[] data) {
        init(data, 0, 0);
    }
    private void init(double[] data, double thresh1, double thresh2) {
        int len = data.length;
        this.data = Arrays.copyOf(data, len);
        
        this.thresh1 = thresh1;
        this.thresh2 = thresh2;
        count = above = below = 0;
        
        int idx=0;
        for(; idx<len; idx++) {
            if(Double.isFinite(data[idx])) {            
                min = max = data[idx];
                break;
            }
        }
        for(; idx<len; idx++) {
            final double v = data[idx];
            if(Double.isFinite(v)) {
                count++;
                if(min>v) min=v;
                if(max<v) max=v;
                if(v<thresh1) below++;
                else if(v>thresh2) above++;
            }
        }
    }
    
    public static Set<Point> getCoords(Geometry geometry, Projection proj) {
        return GeometryUtils.getCoords(geometry, proj);
    }    

    public static Set<Point> getCoords(Geometry geometry, Projection proj, Collection<double[]> latlons) {
        Set<Point> coords =  new HashSet<>(latlons.size());
        for(double[] latlon : latlons) {
            final int[] xy = proj.mapLatLonToPixel(latlon);
            coords.add(new Point(xy[0], xy[1]));
        }
        return getCoords(geometry, proj, coords);
    }
    public static Set<Point> getCoords(Geometry geometry, Projection proj, Set<Point> coordSet) {
        Set<Point> coords = GeometryUtils.getCoords(geometry, proj);
        Set<Point> filteredCoordSet = new HashSet<>(Math.min(coords.size(), coordSet.size()));
        for(Point coord : coordSet) {
            if(coords.contains(coord))
                filteredCoordSet.add(coord);
        }
        return filteredCoordSet;
    }    

    
    public double getCount() {
        return count;
    }
    public double getMin() {
        return min;
    }
    public double getMax() {
        return max;
    }
    public double getAbove() {
        return above;
    }
    public double getBelow() {
        return below;
    }
    public double getLowerThresh() {
        return thresh1;
    }
    public double getUpperThresh() {
        return thresh2;
    }    
    
    public double getPercentCoverage() {
        return (count-below)/count;
    }
    
    public double[] getDistribution() {
        double[] dist = new double[101];
        if(min==max) {
            Arrays.fill(dist, 1.0/101.0);
            return dist;
        }
        double delta = 100.0/(max-min);
        Map<Double, Integer> map = getDistributionMap();
        for(Double v : map.keySet()) {
            final int idx = v==max ? 100 : (int)((v-min)*delta);
            dist[idx] = map.get(v)/count;
        }
        
        return dist;
    }
    
    public Map<Double, Integer> getDistributionMap() {
        HashMap<Double, Integer> map = new HashMap<>();
        for(Double v : data) {
            map.put(v, map.getOrDefault(v, 0)+1);
        }
        return map;
    }
    
    public String toString() {
        String str = String.format("GeoSummary(min: %.3f, max: %.3f, percentCov: %.3f)", min, max, getPercentCoverage());
//for(Double v : data) str+=", "+v;
        return str;
    }
}
