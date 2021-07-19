/*******************************************************************************
 * Copyright (c) 2020 Regents of the University of Colorado. All rights reserved.
 *
 * Contributors:
 *     Geary Layne
 *******************************************************************************/
package gov.noaa.gsl.idssEngine.common.imsMessage;

import java.util.UUID;

import gov.noaa.gsl.idssEngine.common.aspect.Relational;
import gov.noaa.gsl.idssEngine.common.aspect.Field;
import gov.noaa.gsl.idssEngine.common.aspect.Model;
import gov.noaa.gsl.idssEngine.common.aspect.Units;
import gov.noaa.gsl.idssEngine.common.aspect.WxType;

public class ImsThreshold {

    private final UUID id;
    public final Field element;
    public final Units units;
    public final Relational condition;
//    public final WxType wxType;
//    public final Model model;
    public final double thresh;
    public final double secThresh;
    public final boolean isProb;
    public final double probThresh;
    
    public ImsThreshold(UUID id, Field element, Units units, Relational condition, double value) {
        this(id, element, units, condition, value, Double.NaN, false, Double.NaN);
    }
    public ImsThreshold(UUID id, Field element, Units units, Relational condition, double value, boolean isProb, double prob) {
        this(id, element, units, condition, value, Double.NaN, isProb, prob);
    }
    public ImsThreshold(UUID id, Field element, Units units, Relational condition, double value, double secondaryValue) {
        this(id, element, units, condition, value, secondaryValue, false, Double.NaN);
    }
    public ImsThreshold(UUID id, Field element, Units units, Relational condition, double value, double secondaryValue, boolean isProb, double prob) {
//        this(id, element, units, condition, value, secondaryValue, isProb, prob, WxType.NONE, Model.NONE);
//    }
//    public ImsThreshold(UUID id, Field element, Units units, Condition condition, double value, double secondaryValue,
//                                              boolean isProb, double prob, WxType wxType, Model model) {
        this.id = id;
        this.element = element;
        this.units = units;
        this.condition = condition;
        this.thresh = value;
        this.secThresh = secondaryValue;
        this.isProb = isProb;
        this.probThresh = prob;
//        this.wxType = wxType;
//        this.model = model;
        
    }
    
    public UUID getId() {
        return id;
    }
    public String getIdString() {
        UUID id = getId();
        return (id==null?"null":id.toString());
    }
    
    public String toString() {
        if(isProb) {
            if(!Double.isNaN(secThresh))
                return String.format("ImsThreshold(%s, %s, %s, %s, %f, %f, %b, %f)", id, element, units, condition, thresh, secThresh, isProb, probThresh);
            
            return String.format("ImsThreshold(%s, %s, %s, %s, %f, %b, %f)", id, element, units, condition, thresh, isProb, probThresh);
        }
        
        if(!Double.isNaN(secThresh))
                return String.format("ImsThreshold(%s, %s, %s, %s, %f, %f)", id, element, units, condition, thresh, secThresh);
            
        return String.format("ImsThreshold(%s, %s, %s, %s, %f)", id, element, units, condition, thresh);
    }
}
