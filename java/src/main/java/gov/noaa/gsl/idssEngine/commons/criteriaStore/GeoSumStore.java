/*******************************************************************************
 * Copyright (c) 2020 Regents of the University of Colorado. All rights reserved.
 *
 * Contributors:
 *     Geary Layne
 *******************************************************************************/
package gov.noaa.gsl.idssEngine.common.criteriaStore;

import java.awt.Point;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;

import javax.print.DocFlavor.STRING;

import org.joda.time.DateTime;

import gov.noaa.gsd.fiqas.cartography.Projection;
import gov.noaa.gsl.idssEngine.common.GeoSummary;
import gov.noaa.gsl.idssEngine.common.ProductType;
import gov.noaa.gsl.idssEngine.common.criteria.Criteria;

public class GeoSumStore {
      
    public static final String DetermKey = ProductType.DetermKey;
    
    final String product;
    final DateTime issueDt;
    final Criteria criteria;
    final Projection proj;
    final Set<Point> coords;
    
    private Set<String> productKeySet = new HashSet<>();
    private Map<DateTime, Map<String, Map<String, GeoSummary>>> criterionGeoSumsMap = new HashMap<>();
    private Map<DateTime, Map<String, GeoSummary>> criteriaGeoSumMap = new HashMap<>();
    
    public GeoSumStore(String product, Criteria criteria, Projection proj, Set<Point> coords) {
        this.product = product;
        this.issueDt = null;
        this.criteria = criteria;
        this.proj = proj;
        
        this.coords = new HashSet<>(coords);
    }

    public GeoSumStore(String product, DateTime issueDt, Criteria criteria, Projection proj) {
        this.product = product;
        this.issueDt = issueDt;
        this.criteria = criteria;
        this.proj = proj;
        this.coords = GeoSummary.getCoords(criteria.getGeometry(), proj);
    }
    public GeoSumStore(String product, DateTime issueDt, DateTime[] validDts, Map<String, GeoSummary[]> productMap) {
        this.product = product;
        this.issueDt = issueDt;
        this.criteria = null;
        this.proj = null;
        this.coords = null;

        criterionGeoSumsMap = null;
        loadGeoSummary(validDts, productMap);
    }
    
    public GeoSumStore(String product, DateTime issueDt, DateTime[] validDts, GeoSummary[] geoSumArray) {
        this.product = product;
        this.issueDt = issueDt;
        this.criteria = null;
        this.proj = null;
        this.coords = null;

        criterionGeoSumsMap = null;
        loadGeoSummary(validDts, DetermKey, geoSumArray);    
    }
    
    private void loadGeoSummary(DateTime[] validDts, Map<String, GeoSummary[]> productMap) {
        for(String productKey : productMap.keySet()) {
            loadGeoSummary(validDts, productKey, productMap.get(productKey));
        }
    }
    private void loadGeoSummary(DateTime[] validDts, String key, GeoSummary[] geoSumArray) {
        for(int i=0; i<validDts.length; i++)
            addCriteriaGeoSum(validDts[i], key, geoSumArray[i]);
    }   
    
    public boolean addFieldGeoSum(DateTime validDt, String fieldName, Map<Point, float[]> points, float thresh) {
        return addFieldGeoSum(validDt, DetermKey, fieldName, getGeoSum(points, thresh));
    }
    public boolean addFieldGeoSum(DateTime validDt, String fieldName, float[][] grid, float thresh) {
        return addFieldGeoSum(validDt, DetermKey, fieldName, getGeoSum(grid, thresh));
    }
    public boolean addFieldGeoSum(DateTime validDt, String productKey, String fieldName, Map<Point, float[]> points, float thresh) {
        return addFieldGeoSum(validDt, productKey, fieldName, getGeoSum(points, thresh));
    }
    public boolean addFieldGeoSum(DateTime validDt, String productKey, String fieldName, float[][] grid, float[] threshs) {
        return addFieldGeoSum(validDt, productKey, fieldName, getGeoSum(grid, threshs[0], threshs[1]));
    }
    public boolean addFieldGeoSum(DateTime validDt, String fieldName, GeoSummary geoSum) {
        return addFieldGeoSum(validDt, DetermKey, fieldName, geoSum);
    }
    public boolean addFieldGeoSum(DateTime validDt, String productKey, String fieldName, GeoSummary geoSum) {
        if(geoSum!=null) {
            productKeySet.add(productKey);
            getCriterionMap(validDt, productKey).put(fieldName, geoSum);
            return true;
        }
        return false;
    }
    
    public boolean addCriterionGeoSum(DateTime validDt, String criterionString, Map<Point, float[]> points) {
        return addCriterionGeoSum(validDt, DetermKey, criterionString, getGeoSum(points));
    }
    public boolean addCriterionGeoSum(DateTime validDt, String criterionString, float[][] grid) {
        return addCriterionGeoSum(validDt, DetermKey, criterionString, getGeoSum(grid));
    }
    public boolean addCriterionGeoSum(DateTime validDt, String productKey, String criterionString, Map<Point, float[]> points) {
        return addCriterionGeoSum(validDt, productKey, criterionString, getGeoSum(points));
    }
    public boolean addCriterionGeoSum(DateTime validDt, String productKey, String criterionString, float[][] grid) {
        return addCriterionGeoSum(validDt, productKey, criterionString, getGeoSum(grid));
    }
    public boolean addCriterionGeoSum(DateTime validDt, String criterionString, GeoSummary geoSum) {
        return addCriterionGeoSum(validDt, DetermKey, criterionString, geoSum);
    }
    public boolean addCriterionGeoSum(DateTime validDt, String productKey, String criterionString, GeoSummary geoSum) {
        if(geoSum!=null) {
            productKeySet.add(productKey);
            getCriterionMap(validDt, productKey).put(criterionString, geoSum);
            return true;
        }
        return false;
    }
  
    public boolean addCriteriaGeoSum(DateTime validDt, Map<Point, float[]> data) {
        return addCriteriaGeoSum(validDt, DetermKey, getGeoSum(data));
    }
    public boolean addCriteriaGeoSum(DateTime validDt, float[][] grid) {
        return addCriteriaGeoSum(validDt, DetermKey, getGeoSum(grid));
    }
    public boolean addCriteriaGeoSum(DateTime validDt, GeoSummary geoSum) {
        return addCriteriaGeoSum(validDt, DetermKey, geoSum);
    }
    public boolean addCriteriaGeoSum(DateTime validDt, String productKey, Map<Point, float[]> data) {
        return addCriteriaGeoSum(validDt, productKey, getGeoSum(data));
    }
    public boolean addCriteriaGeoSum(DateTime validDt, String productKey, float[][] grid) {
        return addCriteriaGeoSum(validDt, productKey, getGeoSum(grid));
    }
    public boolean addCriteriaGeoSum(DateTime validDt, String productKey, GeoSummary geoSum) {
        if(geoSum!=null) {
            productKeySet.add(productKey);
            getCriteriaMap(validDt).put(productKey, geoSum);
            return true;
        }
        return false;
    }

    public boolean addGridGeoSums(DateTime validDt, float[][] criteriaGrid, Map<String, float[][]> gridsMap) {
        return addGridGeoSums(validDt, DetermKey, criteriaGrid, gridsMap);
    }
    public boolean addGridGeoSums(DateTime validDt, String productKey, float[][] criteriaGrid, Map<String, float[][]> gridsMap) {
        boolean criterionStatus = addGridGeoSums(validDt, productKey, gridsMap);
        boolean criteriaStatus = addCriteriaGeoSum(validDt, productKey, criteriaGrid);
        return criteriaStatus && criterionStatus;
    }

    public boolean addGridGeoSums(DateTime validDt, Map<String, float[][]> gridsMap) {
        return addGridGeoSums(validDt, DetermKey, gridsMap);
    }

//    // GJL, original method that did not support raw fields
//    public boolean addGeoSums(DateTime validDt, String productKey, Map<String, float[][]> gridsMap) {
//        boolean success = true;
//        String criteriaKey = criteria.toShortString();
//        for(String keyString : gridsMap.keySet()) {
//            if(keyString.equals(criteriaKey)) {
//                if(! addCriteriaGeoSum(validDt, productKey, gridsMap.get(keyString))) success=false;
//            } else {
//                if(!addCriterionGeoSum(validDt, productKey, keyString, gridsMap.get(keyString))) success=false;
//            } 
//        }
//        return success;
//    }
    
    public boolean addGridGeoSums(DateTime validDt, String productKey, Map<String, float[][]> gridMap) {
        boolean success = true;
        String criteriaKey = criteria.getKey();
        Map<String, float[]> threshMap = new HashMap<>();
        Map<String, float[][]> fieldGridsMap = new HashMap<>();
        for(String keyString : gridMap.keySet()) {
            if(keyString.equals(criteriaKey)) { // this is the criteria
                if(! addCriteriaGeoSum(validDt, productKey, gridMap.get(keyString))) success=false;
            } else if(keyString.indexOf(' ')>=0) { // this is a criterion, store the thresh for the raw field
                String[] strings = keyString.split(" ");
                String key = strings[1];
                float[] threshs = new float[2];
                if(strings.length==5) {
                    threshs[0] = Float.parseFloat(strings[4]);
                    threshs[1] = threshs[0];
                } else if(strings.length==6) {
                    threshs[0] = Float.parseFloat(strings[4]);
                    threshs[1] = Float.parseFloat(strings[5]);                   
                } else {
                    throw new RuntimeException("keyString not of known format ("+keyString+")");
                }
                threshMap.put(key, threshs);
                
                if(!addCriterionGeoSum(validDt, productKey, keyString, gridMap.get(keyString))) success=false;
            } else { // store raw field for later
                fieldGridsMap.put(keyString, gridMap.get(keyString));
            }
        }
        
//System.out.println("fieldGridsMap keys:"); fieldGridsMap.keySet().forEach(k->System.out.println("\t"+k));        
//System.out.println("threshMap keys:"); threshMap.keySet().forEach(k->System.out.println("\t"+k));        
        // now process raw field grids with stored thresholds
        for(String keyString : fieldGridsMap.keySet()) {          
            if(!addFieldGeoSum(validDt, productKey, keyString, fieldGridsMap.get(keyString), threshMap.get(keyString))) success=false;     
        }
        return success;
    }
    
    /////////////

    public boolean addPointGeoSums(DateTime validDt, Map<String, Map<Point, float[]>> pointsMap) {
        return addPointGeoSums(validDt, DetermKey, pointsMap);
    }
    
    public boolean addPointGeoSums(DateTime validDt, String productKey, Map<String, Map<Point, float[]>> pointsMap) {
        boolean success = true;
        String criteriaKey = criteria.getKey();
        Map<String, Float> threshMap = new HashMap<>();
        Map<String, Map<Point, float[]>> fieldPointsMap = new HashMap<>();
        for(String keyString : pointsMap.keySet()) {
            if(keyString.equals(criteriaKey)) { // this is the criteria
                if(! addCriteriaGeoSum(validDt, productKey, pointsMap.get(keyString))) success=false;
            } else if(keyString.indexOf(' ')>=0) { // this is a criterion, store the thresh for the raw field
                String[] strings = keyString.split(" ");
                threshMap.put(strings[strings.length-4], Float.parseFloat(strings[strings.length-1]));
                if(!addCriterionGeoSum(validDt, productKey, keyString, pointsMap.get(keyString))) success=false;
            } else { // store raw field for later
                fieldPointsMap.put(keyString, pointsMap.get(keyString));
            }
        }
        
        // now process raw field grids with stored thresholds
        for(String keyString : fieldPointsMap.keySet()) {          
            if(!addFieldGeoSum(validDt, productKey, keyString, fieldPointsMap.get(keyString), threshMap.get(keyString))) success=false;     
        }
        return success;
    }
    
    /////////////
    
    
    public boolean isDeterm() {
        return productKeySet.size()==1;
    }
    public String[] getProductKeys() {
        return productKeySet.toArray(new String[productKeySet.size()]);
    }
    
    public String[] getCriterionKeys() {
        if(criterionGeoSumsMap==null) return null;
        if(criterionGeoSumsMap.size()==0) return new String[0];
        
        Set<String> criterionKeySet = criterionGeoSumsMap.values().iterator().next().values().iterator().next().keySet();
        return criterionKeySet.toArray(new String[criterionKeySet.size()]);
    }    
    
    public GeoSummary getCriterionGeoSum(DateTime validDt, String criterionString) {
        return getCriterionGeoSum(validDt, DetermKey, criterionString);
    }
    public GeoSummary getCriterionGeoSum(DateTime validDt, String productKey, String criterionString) {
        try {
            return criterionGeoSumsMap.get(validDt).get(productKey).get(criterionString);
        } catch(Exception e) {
            return null;
        }
    }
    
    public GeoSummary getCriteriaGeoSum(DateTime validDt) {
        return getCriteriaGeoSum(validDt, DetermKey);
    }
    public GeoSummary getCriteriaGeoSum(DateTime validDt, String productKey) {
         try {
            return criteriaGeoSumMap.get(validDt).get(productKey);
        } catch(Exception e) {
            return null;
        }
    }

    private  Map<String, GeoSummary> getCriteriaMap( DateTime validDt) {
        Map<String, GeoSummary> memberCriteriaGridsMap = criteriaGeoSumMap.get(validDt);
        if(memberCriteriaGridsMap == null) {
            memberCriteriaGridsMap = new HashMap<>();
            criteriaGeoSumMap.put(validDt, memberCriteriaGridsMap);
        }
        return memberCriteriaGridsMap;
    }    
    
    private Map<String, GeoSummary> getCriterionMap(DateTime validDt, String productKey) {
        Map<String, Map<String, GeoSummary>> memberCriterionGeoSumsMap = criterionGeoSumsMap.get(validDt);
        if(memberCriterionGeoSumsMap == null) {
            memberCriterionGeoSumsMap = new HashMap<>();
            criterionGeoSumsMap.put(validDt, memberCriterionGeoSumsMap);
        }
        Map<String, GeoSummary> criterionMap = memberCriterionGeoSumsMap.get(productKey);
        if(criterionMap == null) {
            criterionMap = new HashMap<>();
            memberCriterionGeoSumsMap.put(productKey, criterionMap);
        }
        return criterionMap;
    }
          
    private GeoSummary getGeoSum(float[][] grid) {
        return getGeoSum(grid, 0);
    }
    private GeoSummary getGeoSum(float[][] grid, double thresh) {
        return getGeoSum(grid, thresh, thresh);
    }
    private GeoSummary getGeoSum(float[][] grid, double thresh1, double thresh2) {
GeoSummary geoSum = new GeoSummary(coords, grid, thresh1,  thresh2);
        if(Double.isFinite(geoSum.getMax()) && Double.isFinite(geoSum.getPercentCoverage()))
                return geoSum;
        return null;
    }
    
    private GeoSummary getGeoSum(Map<Point, float[]> data) {
        return getGeoSum(data, 0);
    }
    private GeoSummary getGeoSum(Map<Point, float[]> data, double thresh) {
        return getGeoSum(data, thresh, thresh);
    }
    private GeoSummary getGeoSum(Map<Point, float[]> data, double thresh1, double thresh2) {
        GeoSummary geoSum = new GeoSummary(coords, data, thresh1, thresh2);
        if(Double.isFinite(geoSum.getMax()) && Double.isFinite(geoSum.getPercentCoverage()))
                return geoSum;
        return null;
    }
}
