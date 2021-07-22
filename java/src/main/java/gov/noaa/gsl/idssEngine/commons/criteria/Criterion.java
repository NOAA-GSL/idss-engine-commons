/*******************************************************************************
 * Copyright (c) 2020 Regents of the University of Colorado. All rights reserved.
 *
 * Contributors:
 *     Geary Layne
 *******************************************************************************/
package gov.noaa.gsl.idssEngine.commons.criteria;

import gov.noaa.gsl.idssEngine.commons.aspect.Field;
import gov.noaa.gsl.idssEngine.commons.aspect.Relational;
import gov.noaa.gsl.idssEngine.commons.aspect.Units;

public class Criterion {
    
    public final String name;
    public final Field field;
    public final Units units;
    public final Relational relational;
    public final double thresh;
    public final double secThresh;

    public Criterion(String name, Field field, Units units, Relational relational, double thresh) {
        this(name, field, units, relational, thresh, Double.NaN);
        if(relational==Relational.BETWEEN) 
            throw new RuntimeException("A criterion with relational==BETWEEN must be given a secondaryValue");
    }
    
    public Criterion(String name, Field field, Units units, Relational relational, double thresh, double secThresh) {
        this.name = name;
        this.field = field;
        this.units = units;
        this.relational = relational;
        this.thresh = thresh;
        this.secThresh = secThresh;
    }
    
    public Criterion copy() {
        return new Criterion(this.name, this.field, this.units, this.relational, this.thresh, this.secThresh);
    }
    
    public String toString() {
        return String.format("Criterion(%s, %s, %s, %s, %f, %f)", name, field, units, relational, thresh, secThresh);
    }

    public String getKey() {
        return getKey(true);
    }
    
    public String getKey(boolean includeName) {
        String str, valueStr = String.format("%3.2f", thresh);
        if(relational==Relational.BETWEEN) {
            valueStr += String.format(" %3.2f", secThresh);
        } 
        if(includeName)
            str = String.format("%s %s %s %s %s", name, field, units, relational.toShortString(), valueStr);
        else 
            str = String.format("%s %s %s %s", field, units, relational.toShortString(), valueStr);
            
        return str;
    }

}
