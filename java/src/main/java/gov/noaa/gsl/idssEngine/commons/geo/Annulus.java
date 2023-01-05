/*********************************************************************************
  * Copyright (c) 2022 Regents of the University of Colorado. All rights reserved.
 *
 * Contributors:
 *     Geary Layne
*********************************************************************************/
package gov.noaa.gsl.idssEngine.commons.geo;

import org.locationtech.jts.geom.CoordinateSequence;
import org.locationtech.jts.geom.Geometry;
import org.locationtech.jts.geom.GeometryFactory;
import org.locationtech.jts.geom.Point;

public class Annulus extends Point {

    private static final long serialVersionUID = -238226395010043772L;

    public static final String annulus = "Annulus";

    public final double innerRadius;
    public final double outerRadius;

    protected Annulus(CoordinateSequence coordinates, GeometryFactory factory) {
        this(coordinates, 0, 0, factory);
    }
    private Annulus(CoordinateSequence coordinates, double outerRadius, double innerRadius, GeometryFactory factory) {
        super(coordinates, factory);
        this.outerRadius = outerRadius;
        this.innerRadius = innerRadius;
    }
    
    public Annulus(Point pnt, double outerRadius, double innerRadius) {
        this(pnt.getCoordinateSequence(), outerRadius, innerRadius, pnt.getFactory());
    }

    @Override
    public String getGeometryType() {
        return annulus;
    }
    
    @Override
    public Geometry copy() {
        return new Annulus((Point)super.copy(), outerRadius, innerRadius);
    }
    
    public double getOuterRadius() {
        return outerRadius;
    }
    
    public double getInnerRadius() {
        return innerRadius;
    }

    @Override
    public String toString() {
        return String.format("ANNULUS (%s, RADIUS (%f, %f))", super.toString(), outerRadius, innerRadius);
    }
}
