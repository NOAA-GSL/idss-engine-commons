/*******************************************************************************
 * Copyright (c) 2020 Regents of the University of Colorado. All rights reserved.
 *
 * Contributors:
 *     Geary Layne
 *******************************************************************************/
package gov.noaa.gsl.idssEngine.commons.criteria;

import java.awt.Color;

import gov.noaa.gsd.fiqas.util.image.ColorMapping;
import gov.noaa.gsd.fiqas.util.image.RainbowColorMapping;

public class CriteriaUtil {

    private static final float[] floatAnchors = {-1, 0,0,1};
    private static final Color[] colors = {Color.white, new Color(248,158,0), Color.RED, new Color(83,23,125)};

    public static final ColorMapping floatCm = new RainbowColorMapping(floatAnchors, colors);
}
