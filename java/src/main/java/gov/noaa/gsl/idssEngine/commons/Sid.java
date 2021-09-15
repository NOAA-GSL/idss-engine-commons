/*********************************************************************************
  * Copyright (c) 2021 Regents of the University of Colorado. All rights reserved.
 *
 * Contributors:
 *     Geary Layne
*********************************************************************************/
package gov.noaa.gsl.idssEngine.commons;

import java.util.UUID;

import org.joda.time.DateTime;
import org.joda.time.DateTimeZone;

import gov.noaa.gsd.fiqas.util.time.DateTimeFactory;

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
    
    
}
