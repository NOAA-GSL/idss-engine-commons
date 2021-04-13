/*******************************************************************************
 * Copyright (c) 2020 Regents of the University of Colorado. All rights reserved.
 *
 * Contributors:
 *     Geary Layne
 *******************************************************************************/
package gov.noaa.gsl.idssEngine.common.criteria;

import gov.noaa.gsl.idssEngine.common.aspect.Condition;
import gov.noaa.gsl.idssEngine.common.aspect.Field;
import gov.noaa.gsl.idssEngine.common.aspect.Units;

public class Criterion {
    
    public final String name;
    public final Field field;
    public final Units units;
    public final Condition condition;
    public final double thresh;
    public final double secThresh;

    public Criterion(String name, Field field, Units units, Condition condition, double thresh) {
        this(name, field, units, condition, thresh, Double.NaN);
        if(condition==Condition.BETWEEN) 
            throw new RuntimeException("A criterion with condition==BETWEEN must be given a secondaryValue");
    }
    
    public Criterion(String name, Field field, Units units, Condition condition, double thresh, double secThresh) {
        this.name = name;
        this.field = field;
        this.units = units;
        this.condition = condition;
        this.thresh = thresh;
        this.secThresh = secThresh;
    }
    
    public Criterion copy() {
        return new Criterion(this.name, this.field, this.units, this.condition, this.thresh, this.secThresh);
    }
    
    public String toString() {
        return String.format("Criterion(%s, %s, %s, %s, %f, %f)", name, field, units, condition, thresh, secThresh);
    }

    public String getKey() {
        return getKey(true);
    }
    
    public String getKey(boolean includeName) {
        String str, valueStr = String.format("%3.2f", thresh);
        if(condition==Condition.BETWEEN) {
            valueStr += String.format(" %3.2f", secThresh);
        } 
        if(includeName)
            str = String.format("%s %s %s %s %s", name, field, units, condition.toShortString(), valueStr);
        else 
            str = String.format("%s %s %s %s", field, units, condition.toShortString(), valueStr);
            
        return str;
    }

}
