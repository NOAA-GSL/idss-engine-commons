/*******************************************************************************
 * Copyright (c) 2020 Regents of the University of Colorado. All rights reserved.
 *
 * Contributors:
 *     Geary Layne
 *******************************************************************************/
package gov.noaa.gsl.idssEngine.common;

import java.util.Arrays;

import org.apache.commons.math.stat.descriptive.UnivariateStatistic;
import org.apache.commons.math.stat.descriptive.moment.Mean;
import org.apache.commons.math.stat.descriptive.rank.Median;
import org.apache.commons.math.stat.descriptive.rank.Percentile;
import org.joda.time.DateTime;

import gov.noaa.gsd.fiqas.cartography.Projection;
import gov.noaa.gsd.fiqas.util.time.DateTimeFactory;
import gov.noaa.gsl.idssEngine.common.criteriaStore.CriteriaStore;
import gov.noaa.gsl.idssEngine.common.criteriaStore.GeoSumStore;

public class CriteriaSummary {
    
    public enum Type{
        Unknown, Member, Percentile, Deterministic, PointObs
    }
    
    private final String product;
    private final DateTime issueDt;
    private final DateTime[] validDts;
    private final Type type;
    private GeoSumStore geoSums = null;
    private CriteriaStore criteriaStore = null;
    private final DateTime timeStamp;
    
    public CriteriaSummary(String product, DateTime issueDt, DateTime[] validDts, CriteriaStore criteriaStore) {
        this(product, issueDt, validDts, criteriaStore, Type.Unknown);
    }
    public CriteriaSummary(String product, DateTime issueDt, DateTime[] validDts, CriteriaStore criteriaStore, Type type) {
        this(product, issueDt, validDts, null /*this could be build from criteriaGrids*/, criteriaStore, type);
    }
    public CriteriaSummary(String product, DateTime[] validDts, GeoSumStore geoSums, CriteriaStore criteriaStore, Type type) {
        this(product, null, validDts, geoSums, criteriaStore, type);
    }
    public CriteriaSummary(String product, DateTime issueDt, DateTime[] validDts, GeoSumStore geoSums, CriteriaStore criteriaStore, Type type) {
        this.product = product;
        this.issueDt = issueDt;
        this.validDts = Arrays.copyOf(validDts, validDts.length);
        this.geoSums = geoSums; 
        this.criteriaStore = criteriaStore;
        this.type = type;
        timeStamp = DateTimeFactory.now();
    }
    
    
    private int getIdx(DateTime dt) {
        for(int idx=0; idx<validDts.length; idx++) {
            if(!dt.isBefore(validDts[idx]) && !dt.isAfter(validDts[idx])) {
                 return idx;
            }
        }
        return -1;
    }
    
    public String getProduct() {
        return product;
    }
    
    public Projection getProjection() {
        return criteriaStore.getProjection();
    }
    
    public DateTime getIssueDateTime() {
        return issueDt;
    }
    
    public DateTime[] getValidDateTimes() {
        return validDts;
    }

    public Type getType() {
        return type;
    }
    
    public boolean isDeterministic() {
        return type==Type.Deterministic;
    }
    public boolean isNonProb() {
        return type!=Type.Unknown && type!=Type.Percentile;
    }
    
    public DateTime getTimeStamp() {
        return timeStamp;
    }
    
    public DateTime getValidDt(int idx) {
        if(idx<0) idx+=validDts.length;
        if(idx<0 || idx>= validDts.length) return null;
        return validDts[idx];
    }

    public String[] getMemberKeys() {
        return geoSums.getProductKeys();
    }
    
    public String[] getCriterionKeys() {
        return geoSums.getCriterionKeys();
    }
    
    public GeoSummary[] getCriteriaGeoSummary(String memberKey) {
        int len = validDts.length;
        GeoSummary[] criteriaGeoSums = new GeoSummary[len];
        for(int i=0; i<len; i++) criteriaGeoSums[i] = geoSums.getCriteriaGeoSum(validDts[i], memberKey);
        return criteriaGeoSums;
    }
    
    public GeoSummary[] getCriterionGeoSummary(String memberKey, String criterionKey) {
        int len = validDts.length;
        GeoSummary[] criteriaGeoSums = new GeoSummary[len];
        for(int i=0; i<len; i++) criteriaGeoSums[i] = geoSums.getCriterionGeoSum(validDts[i], memberKey, criterionKey);
        return criteriaGeoSums;
    }
    
    public double getMaxIntensity(DateTime dt) {
        int idx = getIdx(dt);
        if(idx<0) return Double.NaN;
        double max = Double.NaN;
        for(String memberKey : getMemberKeys()) {
            GeoSummary[] geoSumArray = getCriteriaGeoSummary(memberKey);
            if(geoSumArray[idx]==null) return Double.NaN;
            double v = geoSumArray[idx].getMax();
            if(!Double.isFinite(max)) max = v;
            else if(max<v) max=v;
        }
        return max;
    }

    public double[] getMaxIntensities() {
        int len = validDts.length;
        double[] maxPerDt = new double[len];
        for(int i=0; i<len; i++) {
            maxPerDt[i] = getMaxIntensity(validDts[i]);
        }
            
        return maxPerDt;
    }
    
    public double getSingleMaxInensity() {
        double[] mi = getMaxIntensities();
        if(mi==null || mi.length==0) return Double.NaN;
        
        double max = mi[0];
        for(int i=mi.length-1; i>0; i--) {
            if(!Double.isFinite(max)) max=mi[i];
            if(max<mi[i]) max=mi[i];
        }
         return max;
    }
    
    public double getMaxPercentExceedance(DateTime dt) {
        int idx = getIdx(dt);
        if(idx<0) return Double.NaN;
        double max = Double.NaN;
        for(String memberKey : getMemberKeys()) {
            GeoSummary[] geoSumArray = getCriteriaGeoSummary(memberKey);
            if(geoSumArray[idx]==null) return Double.NaN;
            double v = geoSumArray[idx].getPercentCoverage();
            if(!Double.isFinite(max)) max = v;
            else if(max<v) max=v;
        }
        return max;
    }

    public double[] getMaxPercentExceedances() {
        int len = validDts.length;
        double[] pePerDt = new double[len];
        for(int i=0; i<len; i++) {
            pePerDt[i] = getMaxPercentExceedance(validDts[i]);
        }
            
        return pePerDt;
    }
    
    public double getSingleMaxPercentExceedance() {
        double[] pe = getMaxPercentExceedances();
        if(pe == null || pe.length==0) return Double.NaN;
        double max = pe[0];
        for(int i=pe.length-1; i>0; i--) {
            if(!Double.isFinite(max)) max=pe[i];
            if(max<pe[i]) max=pe[i];
        }
         return max;
    }
    
    private double getMemberMaxIntensity(String memberKey, int idx) {
        if(idx<0) return Double.NaN;
        GeoSummary[] geoSumArray = getCriteriaGeoSummary(memberKey);
        if(geoSumArray[idx]==null) return Double.NaN;
        return geoSumArray[idx].getMax();
    }
        
    public double getMemberMaxIntensity(String memberKey, DateTime dt) {
        int idx = getIdx(dt);
        return getMemberMaxIntensity(memberKey, idx);
    }

    public double[] getMemberMaxIntensities(String memberKey) {
        int len = validDts.length;
        double[] maxs = new double[len];
        for(int idx=0; idx<len; idx++) {
            maxs[idx] = getMemberMaxIntensity(memberKey, idx);
        }
        return maxs;
    }

    private double getMemberPercentExceedance(String memberKey, int idx) {
        if(idx<0) return Double.NaN;
        GeoSummary[] geoSumArray = getCriteriaGeoSummary(memberKey);
        if(geoSumArray[idx]==null) return Double.NaN;
        return geoSumArray[idx].getPercentCoverage();
    }
        
    public double getMemberPercentExceedance(String memberKey, DateTime dt) {
        int idx = getIdx(dt);
        return getMemberPercentExceedance(memberKey, idx);
    }

    public double[] getMemberPercentExceedance(String memberKey) {
        int len = validDts.length;
        double[] pes = new double[len];
        for(int idx=0; idx<len; idx++) {
            pes[idx] = getMemberPercentExceedance(memberKey, idx);
        }
        return pes;
    }
    
    public float[][] getMemberGrid(String memberKey, DateTime dt) {
        return criteriaStore.getCriteriaGrid(dt, memberKey);
    }

//    public void clear() {
//        if(criteriaStore!=null) criteriaStore.clear();      
//    }

    public String storeGrid(DateTime validDt, String prefix, String outDir) {
        return criteriaStore.write(validDt, prefix, outDir);
    }
    
//    public DateTime[] getOnsets(double[] intensities) {
//        int len = intensities.length;
//        DateTime[] onsetDts = new DateTime[len];
//        int onsetIdx=0;
//        double i1 = intensities[0];
//        for(int idx=1; idx<len; idx++) {
//            double i2 = intensities[idx];
//            if(i1<0 && i2>=0) {
//                double p = -i1/(i2-i1);
//                onsetDts[onsetIdx] = validDts[idx-1].plus((long)(p*(validDts[idx].getMillis()-validDts[idx-1].getMillis())));
//                onsetIdx++;
//            }
//            i1 = i2;
//        }     
//        if(onsetIdx<=0)
//            return null;
//        return Arrays.copyOf(onsetDts, onsetIdx);
//    }
//    
//    public DateTime[] getCessations(double[] intensities) {
//        int len = intensities.length;
//        DateTime[] cessDts = new DateTime[len];
//        int cessIdx=0;
//        double i1 = intensities[0];
//        for(int idx=1; idx<len; idx++) {
//            double i2 = intensities[idx];
//            if(i1>=0 && i2<0) {
//                double p = -i1/(i2-i1);
//                cessDts[cessIdx] = validDts[idx-1].plus((long)(p*(validDts[idx].getMillis()-validDts[idx-1].getMillis())));
//                cessIdx++;
//            }
//            i1 = i2;
//        }     
//        if(cessIdx<=0)
//            return null;
//        return Arrays.copyOf(cessDts, cessIdx);
//    }
    
    public double[][] getOnsetAndCessationInices() {
        return getOnsetAndCessationInices(getMedianMaxIntensities());
    }
    
    public double[][] getOnsetAndCessationInices(double[] intensities) {
        if(intensities==null) return null;
        
         int len = intensities.length;
         if(len == 0) return null;
         
        double[] onsetIdxs = new double[len];
        double[] cessIdxs = new double[len];
        int onsetIdx=0, cessIdx=0;
        double i1 = intensities[0];
        
        if(i1>=0) onsetIdxs[onsetIdx++] = -1;
        
        for(int idx=1; idx<len; idx++) {
            final double i2 = intensities[idx];
            if(i1<0 && i2>=0) { // onset
                onsetIdxs[onsetIdx++] = idx-1.0-i1/(i2-i1);
            }
            else if(i1>=0 && i2<0) { // cess
//                if(onsetIdx == cessIdx) onsetIdxs[onsetIdx++] = -1;
                cessIdxs[cessIdx++] = idx-1.0-i1/(i2-i1);
            }      
            i1=i2;
        }
        if(onsetIdx == 0) return null;
        
        if(intensities[len-1]>=0) cessIdxs[cessIdx++] = -1;
//        if(onsetIdx != cessIdx) cessIdxs[cessIdx++] = -1;
        
        onsetIdxs = Arrays.copyOf(onsetIdxs, onsetIdx);
        cessIdxs = Arrays.copyOf(cessIdxs, cessIdx);
        return new double[][] {onsetIdxs, cessIdxs};
    }
    
    public double getIndexOfMaxIntensityBetween(double[] intensities, double idx1, double idx2) {
        if(idx1< 0) idx1=0;
        else idx1 = Math.ceil(idx1);
        if(idx2 < 0) idx2=intensities.length-1;
        else idx2 = Math.floor(idx2);
        
        int idx = (int)idx1;
        double max = intensities[idx++];
        double maxAt= idx1;
        for(; idx<=idx2; idx++) {
            if(max<intensities[idx]) {
                max=intensities[idx];
                maxAt = idx;
            }
        }
        return maxAt;
    }
  
    public double[] getIndexOfMaxIntensityBetween(double[] intensities, double[] idxs1, double[] idxs2) {
        if(intensities==null || idxs1==null || idxs2==null) return null;
        int len = idxs1.length;
        if(idxs2.length != len) return null;
        double[] idxs = new double[len];
        for(int i=0; i<len; i++) {
            idxs[i] = getIndexOfMaxIntensityBetween(intensities, idxs1[i], idxs2[i]);
        }
        return idxs;
    }
    
    public DateTime getDateTime(double idx) {
        if(idx<0 || idx>=validDts.length) return null;

        int intIdx = (int)idx;
        if(intIdx==idx) return validDts[intIdx];
        
        if(intIdx+1 >= validDts.length) return null;
        
        final double p = (double)intIdx+1.0-idx;
        return validDts[intIdx].plus((long)(p*(validDts[intIdx+1].getMillis()-validDts[intIdx].getMillis())));
    }
    
    public DateTime[] getDateTimes(double[] idxs) {
        if(idxs==null) return null;
        int len = idxs.length;
        DateTime[] dts = new DateTime[len];
        for(int i=0; i<len; i++) {
            dts[i] = getDateTime(idxs[i]);
        }
        return dts;
    }
    
    public double getIntensity(double[] intensities, double idx) {
//System.out.println("idx: "+idx+" vs "+intensities.length);
        if(idx<0 || idx>=intensities.length) return Double.NaN;

        int intIdx = (int)idx;
        if(intIdx==idx) return intensities[intIdx];
        
        if(intIdx+1 >= intensities.length) return Double.NaN;

        final double p = (double)intIdx+1.0-idx;
        return p*intensities[intIdx] + (1.0-p)*intensities[intIdx+1];
    }
    
    public double[] getIntensities(double[] intensities, double[] idxs) {
        if(intensities==null || intensities.length==0 || idxs==null || idxs.length==0) return null;
        int len = idxs.length;
        double[] ans = new double[len];
        for(int i=0; i<len; i++) {
            ans[i] = getIntensity(intensities, idxs[i]);
        }
        return ans;
    }
    
    public double[] getStatFromMaxIntensities(UnivariateStatistic uniStat) {
        if(isNonProb()) {
            int len = validDts.length;
            if(len == 0) return null;
            String[] memberKeys = getMemberKeys();
            int numMbr = memberKeys.length;
            double[] stats = new double[len];
            double[] values = new double[numMbr];
            for(int i=0; i<len; i++) {
                int mbrIdx = 0;
                for(String memberKey : memberKeys) {
                    GeoSummary[] geoSumArray = getCriteriaGeoSummary(memberKey);
                    if(geoSumArray==null || geoSumArray[i]==null)
                        values[mbrIdx] = Double.NaN;
                    else
                        values[mbrIdx] = geoSumArray[i].getMax();
                    mbrIdx++;
                }
                stats[i] = uniStat.evaluate(values);
            }
            return stats;
        } else {
         throw new RuntimeException("Implement this");           
        }
    }
    
    public double[] getStatFromPercentExceedances(UnivariateStatistic uniStat) {
        if(isNonProb()) {
            String[] memberKeys = getMemberKeys();
            int len = validDts.length;
            int numMbr = memberKeys.length;
            double[] stats = new double[len];
            double[] values = new double[numMbr];
            for(int i=0; i<len; i++) {
                int mbrIdx = 0;
                for(String memberKey : memberKeys) {
                    GeoSummary[] geoSumArray = getCriteriaGeoSummary(memberKey);
                    values[mbrIdx] = geoSumArray[i].getPercentCoverage();
                    mbrIdx++;
                }
                stats[i] = uniStat.evaluate(values);
            }
            return stats;
        } else {
         throw new RuntimeException("Implement this");           
        }
    }
    
    public double[] getMeanMaxIntensities( ) {
           return getStatFromMaxIntensities(new Mean());
    }    
    public double[] getMeanPercentExceedances( ) {
           return getStatFromPercentExceedances(new Mean());
    }
    
    public double[] getMedianMaxIntensities( ) {
           return getStatFromMaxIntensities(new Median());
    }    
    public double[] getMedianPercentExceedances( ) {
           return getStatFromPercentExceedances(new Median());
    }

    public double[] getPercentileMaxIntensities(double p) {
           return getStatFromMaxIntensities(new Percentile(p));
    }    
    public double[] getPercentilePercentExceedances(double p) {
           return getStatFromPercentExceedances(new Percentile(p));
    }
    
    public String toString() {
        return String.format("CriteriaSummary(SingleMaxIntensity: %f, SingleMaxPercentExceedance: %f)", getSingleMaxInensity(), getSingleMaxPercentExceedance());
    }
}
