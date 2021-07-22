/*******************************************************************************
 * Copyright (c) 2020 Regents of the University of Colorado. All rights reserved.
 *
 * Contributors:
 *     Geary Layne
 *******************************************************************************/
package gov.noaa.gsl.idssEngine.commons.imsMessage;

import java.util.Arrays;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

public class ImsEvent {
    
//    private final UUID id;
//    private final String name;
    public final long[] validTimes;                                     //seconds since Epoch, Represents the start of an hour over which to evaluate the impact
    public final ImsThresholdSet[] thresholdSets;
    public final ImsLocation[] locations;
    public final Map<String, Object> attrMap = new HashMap<>();

    public ImsEvent(Map<String, Object> attrMap, long[] validTimes, ImsThresholdSet[] thresholdSets, ImsLocation location) {
        this(attrMap, validTimes, thresholdSets, new ImsLocation[] {location});
    }

    public ImsEvent(Map<String, Object> attrMap, long[] validTimes, ImsThresholdSet[] thresholdSets, ImsLocation[] locations) {
        this.attrMap.putAll(attrMap);
        this.validTimes = Arrays.copyOf(validTimes, validTimes.length);
        this.thresholdSets = Arrays.copyOf(thresholdSets, thresholdSets.length);
        this.locations = Arrays.copyOf(locations, locations.length);
    }
    
    public String getName() {
        return attrMap.get("name").toString();
    }
    public UUID getId() {
        return UUID.fromString(getIdString());
    }
    public String getIdString() {
        return attrMap.get("id").toString();
    }

    public String toString() {
        return String.format("ImsEvent(id: %s, name: \"%s\", \n\t\tvalidTimes: %s\n\t\tthresholdSets: %s\n\t\tlocations: %s", 
                                                  getIdString(), getName(), Arrays.toString(validTimes), thresholdSets, locations);
    }
}
