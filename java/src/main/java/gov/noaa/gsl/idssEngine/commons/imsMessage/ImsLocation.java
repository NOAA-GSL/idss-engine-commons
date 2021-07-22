/*******************************************************************************
 * Copyright (c) 2020 Regents of the University of Colorado. All rights reserved.
 *
 * Contributors:
 *     Geary Layne
 *******************************************************************************/
package gov.noaa.gsl.idssEngine.commons.imsMessage;

import java.util.Arrays;
import java.util.UUID;

import org.locationtech.jts.geom.Geometry;

public class ImsLocation {
    public final UUID id;
    public final String name;
    public final Geometry geometry;
    public final int buffer;
    public final Geometry bufferedGeometry;
    public final String[] observationSites;

    public ImsLocation(UUID id, String name, Geometry geometry, int buffer, Geometry bufferedGeometry, String[] observationSites) {
        this.id = id;
        this.name = name;
        this.geometry = geometry;
        this.buffer = buffer;
        this.bufferedGeometry = bufferedGeometry;
        if(observationSites!=null) this.observationSites = Arrays.copyOf(observationSites, observationSites.length);
        else this.observationSites = null;
    }
    
    public String toString() {
        return String.format("IrisLocation(%s, %s, %s, %s) ", id.toString(), name, geometry, bufferedGeometry); 
    }
}
