/*********************************************************************************
  * Copyright (c) 2021 Regents of the University of Colorado. All rights reserved.
 *
 * Contributors:
 *     Geary Layne
*********************************************************************************/
package gov.noaa.gsl.idssEngine.commons;

import java.util.Objects;
import java.util.UUID;

import org.joda.time.DateTime;
import org.joda.time.DateTimeZone;

import gov.noaa.gsd.fiqas.util.time.DateTimeFactory;
import gov.noaa.gsl.idssEngine.riskProc.RiskProcessor;

public class Sid {
    
    public final String key;
    public final String originator;
    public final DateTime issueDt;
    
    public static final Sid Empty = new Sid("None", "none", new DateTime(0, DateTimeZone.UTC));
    public Sid(String key, String originator, DateTime issueDt) {
        this.key = key;
        this.originator = originator;
        this.issueDt = issueDt;
    }

    public Sid(UUID key, String originator, DateTime issueDt) {
        this(key.toString(), originator, issueDt);
    }
    
    public Sid(String key, String originator, String issueDt) {
        this(key, originator, DateTimeFactory.newInstance(issueDt));
    }
    
    @Override
    public int hashCode() {
        return Objects.hash(issueDt, key, originator);
    }

    @Override
    public boolean equals(Object obj) {
        if( this == obj )
            return true;
        if( obj == null )
            return false;
        if( getClass() != obj.getClass() )
            return false;
        Sid other = (Sid) obj;
        return Objects.equals(issueDt, other.issueDt)
                && Objects.equals(key, other.key)
                && Objects.equals(originator, other.originator);
    }
    
    @Override
    public int toString() {
        return String.format("Sid(%s, %s, %s)", key, originator, issueDt);
    }
    
}
