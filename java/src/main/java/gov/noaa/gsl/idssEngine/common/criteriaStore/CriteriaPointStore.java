/*********************************************************************************
  * Copyright (c) 2020 Regents of the University of Colorado. All rights reserved.
 *
 * Contributors:
 *     Geary Layne
*********************************************************************************/
package gov.noaa.gsl.idssEngine.common.criteriaStore;

import org.joda.time.DateTime;

import gov.noaa.gsd.fiqas.cartography.Projection;
import gov.noaa.gsl.idssEngine.common.criteria.Criteria;

public class CriteriaPointStore extends CriteriaStore {

    public CriteriaPointStore(String product, Criteria criteria, Projection proj) {
        super(product, null, criteria, proj);
    }

    @Override
    public float[][] getCriteriaGrid(DateTime dt, String memberKey) {
        throw new RuntimeException("Implment this");
    }

//    @Override
//    public void clear() {
//        throw new RuntimeException("Implment this");
//    }

    @Override
    public String write(DateTime validDt, String prefix, String outDir) {
        throw new RuntimeException("Implment this");
    }

    
}
