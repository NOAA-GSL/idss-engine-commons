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

public abstract class CriteriaStore {

    public abstract float[][] getCriteriaGrid(DateTime dt, String memberKey);
//    public abstract void clear();
    public abstract String write(DateTime validDt, String prefix, String outDir);

    
    final String product;
    final DateTime issueDt;
    final Criteria criteria;
    final Projection proj;
    
    public CriteriaStore(String product, DateTime issueDt, Criteria criteria, Projection proj) {
        this.product = product;
        this.issueDt = issueDt;
        this.criteria = criteria;
        this.proj = proj;
    }
    
    public Projection getProjection() {
        return proj;
    }
}
