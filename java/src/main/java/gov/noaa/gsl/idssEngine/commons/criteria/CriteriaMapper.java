/*******************************************************************************
 * Copyright (c) 2020 Regents of the University of Colorado. All rights reserved.
 *
 * Contributors:
 *     Geary Layne
 *******************************************************************************/
package gov.noaa.gsl.idssEngine.commons.criteria;

import java.awt.Point;
import java.util.Arrays;
import java.util.HashMap;
import java.util.Map;

import gov.noaa.gsl.idssEngine.commons.aspect.Relational;

public class CriteriaMapper {
    
    public static final double defaultFillValue = Double.NaN;
    public static final boolean defaultClip = true;
        
    private final CmCore core;
    
    public static double[][] getControlData(double min, double max, double thresh, boolean clip) {
            if(clip) {
                return new double[][] {{Double.NEGATIVE_INFINITY, min, max, Double.POSITIVE_INFINITY},
                                                               {0,1,0}, {0,1,0}};
            } else {
                return new double[][] {{min, max}, {1},  {1}};
            }
    } 
    
    public static CriteriaMapper newLinearMapper(Relational relational, double[] minMax, double thresh) {
        return newLinearMapper(relational, minMax[0], minMax[1], thresh);
    }
    public static CriteriaMapper newLinearMapper(Relational relational, double[] minMax, double thresh, double secThresh) {
        return newLinearMapper(relational, minMax[0], minMax[1], thresh, secThresh);
    }
    public static CriteriaMapper newLinearMapper(Relational relational, double[] minMax, double thresh, boolean clip) {
        return newLinearMapper(relational, minMax[0], minMax[1], thresh, clip);
   }
    public static CriteriaMapper newLinearMapper(Relational relational, double[] minMax, double thresh, double secThresh, boolean clip) {
        return newLinearMapper(relational, minMax[0], minMax[1], thresh, secThresh, clip);
    }
    public static CriteriaMapper newLinearMapper(Relational relational, double[] minMax, double thresh, double secThresh, double fillValue, boolean clip) {
        return newLinearMapper(relational, minMax[0], minMax[1], thresh, secThresh, fillValue, clip);
    }    
    
    public static CriteriaMapper newLinearMapper(Relational relational, double min, double max, double thresh) {
        return newLinearMapper(relational, min,  max, thresh, Double.NaN, defaultFillValue, defaultClip);
    }
    public static CriteriaMapper newLinearMapper(Relational relational, double min, double max, double thresh, double secThresh) {
        return newLinearMapper(relational, min,  max, thresh, secThresh, defaultFillValue, defaultClip);
    }
    public static CriteriaMapper newLinearMapper(Relational relational, double min, double max, double thresh, boolean clip) {
        return newLinearMapper(relational, min, max, thresh, Double.NaN, defaultFillValue, clip);
    }
    public static CriteriaMapper newLinearMapper(Relational relational, double min, double max, double thresh, double secThresh, boolean clip) {
        return newLinearMapper(relational, min, max, thresh, secThresh, defaultFillValue, clip);
    }
    public static CriteriaMapper newLinearMapper(Relational relational, double min, double max, double thresh, double secThresh, double fillValue, boolean clip) {
        double[][] controlData = getControlData(min, max, thresh, clip);
        return new CriteriaMapper(relational, controlData[0], controlData[1], controlData[2], thresh, secThresh, fillValue);
    }

    public CriteriaMapper(Relational relational, double[] controlPoints, 
                                                double[] startWeights, double[] endWeights, 
                                                double thresh) {
        this(relational, controlPoints, startWeights, endWeights, thresh, Double.NaN, defaultFillValue);
    }
    
    public CriteriaMapper(Relational relational, double[] controlPoints, 
                                                double[] startWeights, double[] endWeights, 
                                                double thresh, double secondaryThresh, double fillValue) {
        switch(relational) {
        case BETWEEN:
            if(!Double.isFinite(secondaryThresh))
                throw new RuntimeException("If relational = BETWEEN, than there must be a secondary threshold");
            core = new CmBetween(controlPoints, startWeights, endWeights, thresh,
                                                              controlPoints, startWeights, endWeights, secondaryThresh,
                                                              (thresh+secondaryThresh)/2.0);
            break;
        case GREATERTHAN:
            core = new CmGreaterThan(controlPoints, startWeights, endWeights, thresh);
            break;
        case GREATERTHANOREQUAL:
            core = new CmGreaterThanEqual(controlPoints, startWeights, endWeights, thresh);
            break;
        case LESSTHAN:
            core = new CmLessThan(controlPoints, startWeights, endWeights, thresh);
            break;
        case LESSTHANOREQUAL:
            core = new CmLessThanEqual(controlPoints, startWeights, endWeights, thresh);
            break;
       default:
           core = null;
           throw new RuntimeException("relational ("+relational+") not supported");
        }
        core.setFill(fillValue);
    }

/*
    public static float mapGteLinearMapper(float grid, double min, double max, double thresh) {
        return mapGteLinearMapper(grid, min, max, thresh, defaultFillValue);
    }
    public static float mapGteLinearMapper(float grid, double min, double max, double thresh, double fillValue) {
        return map(grid, newLinearMapper(relational.GREATERTHANOREQUAL, min, max, thresh, fillValue));
    }
    public static float mapLteLinearMapper(float grid, double min, double max, double thresh) {
        return mapLteLinearMapper(grid, min, max, thresh, defaultFillValue);
   }
    public static float mapLteLinearMapper(float grid, double min, double max, double thresh, double fillValue) {
        return map(grid, newLinearMapper(relational.LESSTHANOREQUAL, min, max, thresh, fillValue));
    }
    
    public static float[][] mapGteLinearMapper(float[][] grid, double min, double max, double thresh) {
        return mapGteLinearMapper(grid, min, max, thresh, defaultFillValue);
    }
    public static float[][] mapGteLinearMapper(float[][] grid, double min, double max, double thresh, double fillValue) {
        return map(grid, newLinearMapper(relational.GREATERTHANOREQUAL, min, max, thresh, fillValue), null);
    }
    public static float[][] mapLteLinearMapper(float[][] grid, double min, double max, double thresh) {
        return mapLteLinearMapper(grid, min, max, thresh, defaultFillValue);
   }
    public static float[][] mapLteLinearMapper(float[][] grid, double min, double max, double thresh, double fillValue) {
        return map(grid, newLinearMapper(relational.LESSTHANOREQUAL, min, max, thresh, fillValue), null);
    }
*/

    public static float map(float value, CriteriaMapper cm) {
        return cm.mapToFloat(value);
    }

    public static double map(double value, CriteriaMapper cm) {
        return cm.core.mapToDouble(value);
    }

   public static float[][] map(float[][] grid, CriteriaMapper cm) {
       return map(grid, cm, null);
   }
    public static float[][] map(float[][] grid, CriteriaMapper cm, float[][] result) {
        int d1=grid.length, d2=grid[0].length;
        if(result==null || result.length!=d1 || result[0].length!=d2)
            result = new float[d1][d2];
        for(int i=0; i<d1; i++) {
            for(int j=0; j<d2; j++) {
                result[i][j] = cm.mapToFloat(grid[i][j]);
            }
        }
        return result;
    }
    
   public static double[][] map(double[][] grid, CriteriaMapper cm) {
       return map(grid, cm, null);
   }
    public static double[][] map(double[][] grid, CriteriaMapper cm, double[][] result) {
        int d1=grid.length, d2=grid[0].length;
        if(result==null || result.length!=d1 || result[0].length!=d2)
            result = new double[d1][d2];
        for(int i=0; i<d1; i++) {
            for(int j=0; j<d2; j++) {
                result[i][j] = cm.core.mapToDouble(grid[i][j]);
            }
        }
        return result;
    }
    
    public float mapToFloat(double v) {
        return (float)core.mapToDouble(v);
    }
    
    public static Map<Point, float[]> map(Map<Point, float[]> fieldData, CriteriaMapper cm) {
        Map<Point, float[]> resultMap = new HashMap<Point, float[]>();
        for(Point pnt : fieldData.keySet()) {
            final float[] data = fieldData.get(pnt);
            int len = data.length;
            float[] result = new float[len];
            resultMap.put(new Point(pnt), result);
            for(int i=0; i<len; i++) result[i] = cm.mapToFloat(data[i]);
        }
        return resultMap;
    }
    
    /////////////////////////////////////////////////////////////// inner classes ///////////////////////////////////////////////////////

    private class CmGreaterThanEqual implements CmCore {
        final int last;
        final double thresh, sumBelow, sumAbove;
        final double[] endPoints, startWeights, endWeights, cumSums;
        double fillValue = Double.NaN;
        
        public CmGreaterThanEqual(double[] endPoints, double[] startWeights, double[] endWeights, double thresh) {
            last = endPoints.length-1;
            if(last<1) 
                throw new RuntimeException("There must be at least two endPoints");
            if(thresh<=endPoints[0] || thresh>=endPoints[last])
                throw new RuntimeException("The threshold must be between the first and last endPoints");
            if(!Double.isFinite(endPoints[0]) && startWeights[0]!=0 && endWeights[0]!=0) 
                throw new RuntimeException("When the first end point is non finite, the weights for the first sub domain must be zero");
            if(!Double.isFinite(endPoints[last]) && startWeights[last-1]!=0 && endWeights[last-1]!=0) 
                throw new RuntimeException("When the last end point is non finite, the weights for the last sub domain must be zero");

            this.thresh = thresh;
            this.endPoints = Arrays.copyOf(endPoints, last+1);
            this.startWeights = Arrays.copyOf(startWeights, last);
            this.endWeights = Arrays.copyOf(endWeights, last);
            cumSums = new double[last+1];
            cumSums[0]=0;
            for(int i=0, ii=1; ii<=last; i++, ii++) {
                double weight = (startWeights[i]+endWeights[i])/2.0;
                cumSums[ii] = cumSums[i] + (weight==0?0:(endPoints[ii]-endPoints[i]) * weight);    
            }
            int idx = getSubDomain(thresh);
            sumBelow = getCumSum(idx, thresh);
            sumAbove = cumSums[last]-sumBelow;
        }
            
        public double mapToDouble(double  v) {
            if(v==thresh) return 0;

            int idx = getSubDomain(v);
            if(idx<0) return fillValue;
            if(v<thresh) return getCumSum(idx,v)/sumBelow - 1.0;
            return (getCumSum(idx,v)-sumBelow)/sumAbove;
        }

        public void setFill(double fillValue) {
            this.fillValue  = fillValue;
        }
                
        protected double getCumSum(int idx, double v) {
            double ans = cumSums[idx]+getDomainSum(idx, v);
            return ans;
        }

        protected int getSubDomain(double v) {
            if(v<endPoints[0] || v>endPoints[last]) return -1;
            for(int i=1; i<last; i++) {
                if(v<endPoints[i]) return i-1;
            }
            return last-1;
        }
        
        protected double getDomainSum(int idx, double v) {
            if(!Double.isFinite(endPoints[idx]) || !Double.isFinite(endPoints[idx+1])) return 0;
            double delta = v-endPoints[idx];
            double p = delta/(endPoints[idx+1]-endPoints[idx]);  
            double weight = (startWeights[idx]+((1.0-p)*startWeights[idx]+p*endWeights[idx]))/2.0;
            double ans = delta * weight;
            return ans;
        }
    }

    private class CmGreaterThan extends CmGreaterThanEqual {
        public CmGreaterThan(double[] endPoints, double[] startWeights,  double[] endWeights, double thresh) {
            super(endPoints, startWeights, endWeights, thresh);
        }

        @Override
        public double mapToDouble(double v) {
            if(v==thresh) v-=Double.MIN_NORMAL;
            return super.mapToDouble(v);
        }
    }

    private class CmLessThan extends CmGreaterThanEqual {
        public CmLessThan(double[] endPoints, double[] startWeights,  double[] endWeights, double thresh) {
            super(endPoints, startWeights, endWeights, thresh);
        }

        @Override
        public double mapToDouble(double v) {
            if(v==thresh) v+=Double.MIN_NORMAL;
            return -super.mapToDouble(v);
        }
    }

    private class CmLessThanEqual extends CmGreaterThanEqual {
        public CmLessThanEqual(double[] endPoints, double[] startWeights,  double[] endWeights, double thresh) {
            super(endPoints, startWeights, endWeights, thresh);
        }

        @Override
        public double mapToDouble(double v) {
            return -super.mapToDouble(v);
        }
    }

    private class CmBetween implements CmCore {
        private final CmCore half1, half2;
        private final double pivot;
        CmBetween(double[] endPoints1, double[] startWeights1,  double[] endWeights1, double thresh1,
                                 double[] endPoints2, double[] startWeights2,  double[] endWeights2, double thresh2,
                                 double pivot) {
            half1 = new CmGreaterThanEqual(endPoints1, startWeights1, endWeights1, thresh1);
            half2 = new CmLessThanEqual(endPoints2, startWeights2, endWeights2, thresh2);            
            this.pivot=pivot;
        }

        @Override
        public double mapToDouble(double v) {
           if(v>pivot) return half2.mapToDouble(v);
            return half1.mapToDouble(v);
        }

        @Override
        public void setFill(double fillValue) {
            half1.setFill(fillValue);
            half2.setFill(fillValue);
        }
    }
    
    interface CmCore {
        double mapToDouble(double v);
        void setFill(double fillValue);
    }


}
