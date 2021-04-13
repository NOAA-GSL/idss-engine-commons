/*******************************************************************************
 * Copyright (c) 2020 Regents of the University of Colorado. All rights reserved.
 *
 * Contributors:
 *     Geary Layne
 *******************************************************************************/
package gov.noaa.gsl.idssEngine.common;


public enum ProductType {
    Deterministic,
    MemberEnsemble,
    PercentileEnsemble,
    PointObs;
    
    public static final String DetermKey = ProductType.Deterministic.toString();
}
