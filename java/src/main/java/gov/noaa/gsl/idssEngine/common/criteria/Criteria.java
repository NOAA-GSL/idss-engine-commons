/*******************************************************************************
 * Copyright (c) 2020 Regents of the University of Colorado. All rights reserved.
 *
 * Contributors:
 *     Geary Layne
 *******************************************************************************/
package gov.noaa.gsl.idssEngine.common.criteria;

import java.util.Collection;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;

import org.joda.time.DateTime;
import org.locationtech.jts.geom.Coordinate;
import org.locationtech.jts.geom.Geometry;

import gov.noaa.gsl.idssEngine.common.aspect.Field;
import gov.noaa.gsl.idssEngine.common.aspect.Units;

public class Criteria {

    public static final double defaultBuffer = 0.25;
    public static final double defaultAccuracy = 0.05;
    
    public final String name;
    public final String criterionsName;
    public final Criterion[] criterions;
    public final CriteriaJoin[] joins;
    public final double accuracy;
    public final double aerialPercent, durationInMin;
    public final int preValidBuffer, postValidBuffer;
    private DateTime[] validDts = null;
    private Geometry geometry = null;
    private Geometry bufferGeometry = null;
    private double[] mbrLatLon = null;
    
    public Criteria(String name, String criterionsName, Criterion[] criterions, CriteriaJoin... joins) {
        this(name, criterionsName, criterions, joins, null, 0, 0,0,0);
    }
    public Criteria(String name, String criterionsName, Criterion[] criterions, CriteriaJoin[] joins, DateTime[] validDts, int preValidBuffer, int postValidBuffer, double arealPercent, double durationInMin) {
        this(name, criterionsName, criterions, joins, validDts, preValidBuffer, postValidBuffer, null, null, null, arealPercent, durationInMin, defaultAccuracy);
    }
//    public Criteria(String name, Criterion[] criterions, CriteriaJoin[] joins, 
//                                  DateTime[] validDts, Geometry geometry, double buffer, 
//                                  int arealPercent, int durationInMin, double accuracy) {
//        this(name, criterions, joins, validDts, geometry, geometry.buffer(buffer), null, arealPercent, durationInMin, accuracy);
//    }
    public Criteria(String name, String criterionsName, Criterion[] criterions, CriteriaJoin[] joins, 
                                 DateTime[] validDts, int preValidBuffer, int postValidBuffer,
                                 Geometry geometry, Geometry bufferGeometry, Geometry mbrGeomentry,
                                 double arealPercent, double durationInMin, double accuracy) {
        this.name = name;
        this.criterionsName = criterionsName;
        this.criterions = getCriterionArrayCopy(criterions);
        this.joins = getCriteriaJoinArrayCopy(joins);
        this.validDts = getDateTimeArrayCopy(validDts);
        this.accuracy = accuracy;
        this.aerialPercent = arealPercent;
        this.durationInMin = durationInMin;
        this.preValidBuffer = preValidBuffer;
        this.postValidBuffer = postValidBuffer;
        if(geometry!=null) setGeometry(geometry, bufferGeometry, mbrGeomentry);
    }
    
    public DateTime[] getValidDts() {
        return getDateTimeArrayCopy(validDts);
    }
    
    public DateTime getStartValidDt() {
        if(validDts==null || validDts.length==0) return null;
        return validDts[0].minusHours(preValidBuffer);
    }
    public DateTime getEndValidDt() {
        if(validDts==null || validDts.length==0) return null;
        return validDts[validDts.length-1].plusHours(postValidBuffer);
    }
    
    public void setGeometry(Geometry geometry, Geometry bufferGeometry, Geometry mbrGeometry) {
        this.geometry = geometry.copy();
        this.bufferGeometry = bufferGeometry.copy();
        if(mbrGeometry!=null) {
            mbrLatLon = getMbrLowLeftUpRightLatLon(mbrGeometry);
        } else
            mbrLatLon = null; //new double[] {Double.NaN, Double.NaN, Double.NaN, Double.NaN};
    }
    
    public Geometry getGeometry() {
        return geometry;
    }
    
    public Geometry getBufferGeometry() {
        return bufferGeometry;
    }
    
    public double[] getMbrLowLeftUpRightLatLon() {
        return mbrLatLon;
    }
    private double[] getMbrLowLeftUpRightLatLon(Geometry mbrGeometry) {
        if(mbrGeometry==null) return null;
        
        double minLat, maxLat, minLon, maxLon;

        Coordinate[] coords = mbrGeometry.getEnvelope().getCoordinates();
        minLat = maxLat = coords[0].y;
        minLon = maxLon = coords[0].x;
        for(int i=1; i<coords.length; i++) {
            Coordinate coord = coords[i];
            double lat = coord.y;
            double lon = coord.x;
            if(minLat>lat) minLat = lat;
            else if(maxLat<lat) maxLat = lat;
            if(minLon>lon) minLon = lon;
            else if(maxLon<lon) maxLon = lon;
        }

        return new double[] {minLat, minLon, maxLat, maxLon};
    }
    
    public String getName() {
        return name;
    }
    
    public String getCriterionsName() {
        return criterionsName;
    }    
    
    public String getKey() {
        return getKey(true);
    }

    public String getKey(boolean includeName) {
        String str;
        if(includeName) str = name+", " + criterions[0].getKey(false);
        else str = criterions[0].getKey(false);
        
        for(int i=1;  i<criterions.length; i++)
            str += ", "+criterions[i].getKey(false);
            
        return str;
    }    
    
    public Map<Field, Set<Units>> getFieldMap() {
        Map<Field, Set<Units>> fieldMap = new HashMap<>();
        for(Criterion criterion : criterions) {
            Set<Units> unitsSet = fieldMap.get(criterion.field);
            if(unitsSet==null)   { 
                unitsSet = new HashSet<>();
                fieldMap.put(criterion.field, unitsSet);
            }
            unitsSet.add(criterion.units);
        }
        return fieldMap;
    }
    
    public String toString() {
        String str = "Criteria()\n";
        for(Criterion criterion : criterions) {
            str+="\t"+criterion+"\n";
        }
        return str;
    }
    
    private Criterion[] getCriterionArrayCopy(Criterion[] criterions) {
        int len = criterions.length;
        Criterion[] copy = new Criterion[len];
        for(int i=0; i<len; i++) {
            copy[i] = criterions[i].copy();
        }
        return copy;        
    }
    private CriteriaJoin[] getCriteriaJoinArrayCopy(CriteriaJoin[] joins) {
        int len = joins.length;
        CriteriaJoin[] copy = new CriteriaJoin[len];
        for(int i=0; i<len; i++) {
            copy[i] = joins[i];
        }
        return copy;
    }
    private DateTime[] getDateTimeArrayCopy(DateTime[] dts) {
        int len = dts.length;
        DateTime[] copy = new DateTime[len];
        for(int i=0; i<len; i++) {
            copy[i] = dts[i].plus(0);
        }
        return copy;
    }

}
