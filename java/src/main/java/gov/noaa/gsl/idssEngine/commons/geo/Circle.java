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


public class Circle extends Point {

    private static final long serialVersionUID = 4296686486631628512L;

    public static final String circle = "Circle";

    final double radius;

    protected Circle(CoordinateSequence coordinates, GeometryFactory factory) {
        this(coordinates, 0, factory);
    }
    private Circle(CoordinateSequence coordinates, double radius, GeometryFactory factory) {
        super(coordinates, factory);
        this.radius = radius;
    }
    
    public Circle(Point pnt, double radius) {
        this(pnt.getCoordinateSequence(), radius, pnt.getFactory());
    }

    @Override
    public String getGeometryType() {
        return circle;
    }
    
    @Override
    public Geometry copy() {
        return new Circle((Point)super.copy(), radius);
    }
    
    public double getRadius() {
        return radius;
    }
    
    @Override
    public String toString() {
        return String.format("CIRCLE (%s, RADIUS (%f))", super.toString(), radius);
    }

}
