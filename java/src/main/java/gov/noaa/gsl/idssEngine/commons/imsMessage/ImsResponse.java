/*******************************************************************************
 * Copyright (c) 2020 Regents of the University of Colorado. All rights reserved.
 *
 * Contributors:
 *     Geary Layne
 *******************************************************************************/
package gov.noaa.gsl.idssEngine.commons.imsMessage;

import java.util.UUID;

import org.joda.time.DateTime;

public class ImsResponse {
   

    public final UUID id;
    public final boolean thresholdExceeded;
    public final boolean isFcst, isObs;
    public final String product;
    public final String description;
    public final DateTime evaluatedAt;
    public final String location;
    public final ThreatPeriod[] threatPeriods;
    
//    String description
//    The alert description (ie. a NWS product segment)
//
//Long evaluatedAt
//    The time at which this alert was evaluated (ms. past Epoch)
//
//String eventId
//    The id of the event to which this alert applies
//
//String geojson
//    The geojson of the threat area as GeoJSON
//
//String id
//    The unique ID for the entity
//
//Boolean isForecast
//    If this alert is based on a forecast
//
//Boolean isObservation
//    If this alert is based on an observation
//
//String primarySource
//    The primary source of the alert (ie. IDSSENGINE)
//
//String secondarySource
//    The secondary source of the alert (ie. HRRR)
//
//Set<ThreatPeriod> threatPeriods
//    The periods of the threat

 
    public ImsResponse(String id, String description, boolean isFcst, boolean isObs, String product, String location,  DateTime evaluatedAt) {
        this(id, description, isFcst, isObs, product, location, evaluatedAt, null, null, null, null);
    }

    public ImsResponse(String id, String description, boolean isFcst, boolean isObs, String product, String location, 
                                              DateTime evaluatedAt, DateTime[] start, DateTime[] end, DateTime[] maxAt, double[] max) {
       
        this.id = UUID.fromString(id);
        this.description = description;
        this.isFcst = isFcst;
        this.isObs = isObs;
        this.product = product;
        this.location = location;
        threatPeriods = getThreadPeriods(start, end, maxAt, max);
        this.thresholdExceeded = threatPeriods.length>0;
        this.evaluatedAt = evaluatedAt;
    }

    private ThreatPeriod[] getThreadPeriods(DateTime[] start, DateTime[] end, DateTime[] maxAt, double[] max) {
        if(start==null) return new ThreatPeriod[0];
        
        int len = start.length;
        ThreatPeriod[] tps = new ThreatPeriod[len];
        for(int i=0; i<len; i++) {
            tps[i] = new ThreatPeriod(start[i], end[i], maxAt[i], max[i]);
        }
        return tps;
    }

//    public String toString() {
//        return String.format("ImsResponse(%s, %s, %s, %s, %d, %d, %d)", id, thresholdExceeded, forecastOrOb, source, start, end, evaluatedAt);
//    }
    
    public class ThreatPeriod {
        public final DateTime begins, ends, maxThreat;
        public final double maxValue;
        
        public ThreatPeriod(DateTime begins, DateTime ends, DateTime maxThreat, double max) {
            this.begins = begins;
            this.ends = ends;
            this.maxThreat = maxThreat;
            this.maxValue = max;                    
        }
    }
}
