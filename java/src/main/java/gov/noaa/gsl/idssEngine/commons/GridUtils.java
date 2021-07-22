/*******************************************************************************
 * Copyright (c) 2020 Regents of the University of Colorado. All rights reserved.
 *
 * Contributors:
 *     Geary Layne
 *******************************************************************************/
package gov.noaa.gsl.idssEngine.commons;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;
import java.util.Set;
import java.util.concurrent.ForkJoinPool;
import java.util.concurrent.RecursiveAction;

import gov.noaa.gsd.fiqas.util.grid.tool.RadialHood;

public class GridUtils {
    
    public static float getMax(float[][] grid, Set<int[]> domainSet) {
        if(domainSet.size()==0) return Float.NaN;
        
        int[] ij = domainSet.iterator().next();
        float max = grid[ij[0]][ij[1]];
        for(int[] xy : domainSet) {
            float v = grid[xy[0]][xy[1]];
            if(max<v) max=v;
        }
        return max;
    }
    
    public static float[][] getDiff(float[][] grid1, float[][] grid2) {
        if(grid1==null || grid2==null) return null;
        
        int d1=grid1.length, d2=grid1[0].length;
        for(int i=0; i<d1; i++) {
            for(int j=0; j<d2; j++) {
                grid1[i][j] -= grid2[i][j];
            }
        }
        return grid1;
    }
    
    public static float[][] getDiff(float[][] grid1, float[][] grid2, float min, float max) {
        if(grid2==null || grid1==null) return null;
        
        int d1=grid1.length, d2=grid1[0].length;
        for(int i=0; i<d1; i++) {
            for(int j=0; j<d2; j++) {
                final float v = grid1[i][j] - grid2[i][j];
                if(v<min) grid1[i][j]=min;
                else if(v>max) grid1[i][j]=max;
                grid1[i][j] = v;
            }
        }
        return grid1;
    } 
    
    public static float[][] getSum(float[][] grid1, float[][] grid2) {
        if(grid1==null || grid2==null) return null;
        
        int d1=grid1.length, d2=grid1[0].length;
        for(int i=0; i<d1; i++) {
            for(int j=0; j<d2; j++) {
                grid1[i][j] += grid2[i][j];
            }
        }
        return grid1;
    }

    public static float[][] getSum(float[][] grid1, float[][] grid2, float min, float max) {
        if(grid2==null || grid1==null) return null;
        
        int d1=grid1.length, d2=grid1[0].length;
        for(int i=0; i<d1; i++) {
            for(int j=0; j<d2; j++) {
                final float v = grid1[i][j] + grid2[i][j];
                if(v<min) grid1[i][j]=min;
                else if(v>max) grid1[i][j]=max;
                grid1[i][j] = v;
            }
        }
        return grid1;
    } 
    
    public static float[][] copy(float[][] grid) {
        if(grid==null) return null;
        
        int d1=grid.length, d2=grid[0].length;
        float[][] ansGrid = new float[d1][d2];
        for(int i=0; i<d1; i++) {
            for(int j=0; j<d2; j++) {
                ansGrid[i][j] = grid[i][j];
            }
        }
        return ansGrid;
   }
    
   public static float[][] getSubGrid(float[][] grid, int xOffset, int yOffset, int width, int height) {
        float[][] subGrid = new float[width][height];
        for(int i=0, ii=xOffset; i<width; i++, ii++) {
            for(int j=0, jj=yOffset; j<height; j++, jj++) {
                subGrid[i][j] = grid[ii][jj];
            }
        }
        return subGrid;
    }
   
   public static void ensureLowerBounds(float[][] grid, float value) {
        if(grid==null) return;
        
       int d1=grid.length, d2=grid[0].length;
       for(int i=0; i<d1; i++) {
            for(int j=0; j<d2; j++) {
                if(grid[i][j]<value) grid[i][j]=value;
            }
        }
    }
   
   public static void ensureUpperBounds(float[][] grid, float value) {
        if(grid==null) return;
        
       int d1=grid.length, d2=grid[0].length;
       for(int i=0; i<d1; i++) {
            for(int j=0; j<d2; j++) {
                if(grid[i][j]>value) grid[i][j]=value;
            }
        }
    }
      
    public static void ensureBounds(float[][] grid, float lowerValue, float upperValue) {
        if(grid==null) return;
        
       int d1=grid.length, d2=grid[0].length;
       for(int i=0; i<d1; i++) {
            for(int j=0; j<d2; j++) {
                final float v = grid[i][j];
                if(v<lowerValue) grid[i][j]=lowerValue;
                if(v>upperValue) grid[i][j]=upperValue;
            }
        }
    }
    
    
    //    RH: =100*(EXP((17.625*TD)/(243.04+TD))/EXP((17.625*T)/(243.04+T)))
    public static float[][] getRelativeHumidityGrid(float[][] tempInKelvin, float[][] dewpointInKelvin) {
        if(tempInKelvin==null || dewpointInKelvin==null) return null;
        
        int d1=tempInKelvin.length, d2=tempInKelvin[0].length;
        float[][] grid = new float[d1][d2];
        for(int i=0; i<d1; i++) {
            for(int j=0; j<d2; j++) {
                final double dp = dewpointInKelvin[i][j];
                final double t = tempInKelvin[i][j];
                grid[i][j] = (float)(100.0*(Math.exp((17.625*dp)/(243.04+dp))/Math.exp((17.625*t)/(243.04+t))));
            }
        }
        return grid;
    }
        
    public static float[][] getWindDirGrid(float[][] uWind, float[][] vWind) {
        if(uWind==null || vWind==null) return null;
        
        int d1=uWind.length, d2=uWind[0].length;
        double rad2Deg = Math.PI/180.0;
        float[][] grid = new float[d1][d2];
        for(int i=0; i<d1; i++) {
            for(int j=0; j<d2; j++) {
                double direction = Math.atan2(uWind[i][j], vWind[i][j]) * rad2Deg;
                if(direction < 0.0) direction+=360.0;
                grid[i][j] = (float)direction;
            }
        }
        return grid;
    }
    
    public static float[][] getWindSpeedGrid(float[][] uWind, float[][] vWind) {
        if(uWind==null || vWind==null) return null;
        
        int d1=uWind.length, d2=uWind[0].length;
        float[][] grid = new float[d1][d2];
        for(int i=0; i<d1; i++) {
            for(int j=0; j<d2; j++) {
                final double u = uWind[i][j];
                final double v = vWind[i][j];
                double speed = Math.sqrt(u*u+v*v);
                grid[i][j] = (float)speed;
            }
        }
        return grid;
    }
    
    public static float[][] getHeatIndexGrid(float[][] rhInPercent, float[][] tempInFahrenheit) {    
        if(rhInPercent==null || tempInFahrenheit==null) return null;
        
        int d1=rhInPercent.length, d2=rhInPercent[0].length;
        float[][] grid = new float[d1][d2];
        for(int i=0; i<d1; i++) {
            for(int j=0; j<d2; j++) {
                final float rh = rhInPercent[i][j];
                final float t = tempInFahrenheit[i][j];
                grid[i][j] = (t+(float)(0.5 * (t + 61.0 + ((t-68.0)*1.2) + (rh*0.094)))) * 0.5f;
                if(grid[i][j]>=80) {
                    final float rh2 = rh*rh;
                    final float t2 = t*t;
                    grid[i][j] = (float)(-42.379 + 2.04901523*t + 10.14333127*rh 
                                                       - .22475541*t*rh - .00683783*t2 - .05481717*rh2 
                                                       + .00122874*t2*rh + .00085282*t*rh2 - .00000199*t2*rh2);
                    if(rh<13 && (t>80 && t<=112)) {
                        grid[i][j] -= ((13.0-rh)/4.0)*Math.sqrt((17.0-Math.abs(t-95.0))/17.0);                        
                    }
                    else if(rh>85 && (t>80 && t<=87)) {
                        grid[i][j] += ((rh-85.0)/10.0) * ((87.0-t)/5.0);
                    }                
                }
            }
        }

        return grid;
    }
    
    // wc = 35.74 + (0.6215 × Temperature) − (35.75 × WindSpeed^0.16) + (0.4275 × Temperature × WindSpeed^0.16)
    public static float[][] getWindChillGrid(float[][] windSpeedInMilesPerHour, float[][] tempInFahrenheit) {    
        if(windSpeedInMilesPerHour==null || tempInFahrenheit==null) return null;
        
        int width=windSpeedInMilesPerHour.length, height=windSpeedInMilesPerHour[0].length;
        float[][] grid = new float[width][height];
        for(int i=0; i<width; i++) {
            for(int j=0; j<height; j++) {
                final double wsEp16 = Math.pow(windSpeedInMilesPerHour[i][j], 0.16);
                final double t = tempInFahrenheit[i][j];
                grid[i][j] = (float)(35.74 + (0.6215 * t) - (35.75 * wsEp16) + (0.4275 * t * wsEp16));
            }
        }

        return grid;
    }   
    
    public static float[][] buildProbFromNeighborhood(float[][] grid, float thresh, double radius) {
        if(grid==null) return null;
        
        RadialHood rh = new RadialHood(radius);
        int d1=grid.length, d2=grid[0].length;
        int xMax = d1-1, yMax = d2-1;
        float[][] ansGrid = new float[d1][d2];
        for(int i=0; i<d1; i++) {
            for(int j=0; j<d2; j++) {
                Set<int[]> xySet = rh.getNeighborhood(i, j, 0, 0, xMax, yMax);
                double cnt=0;
                for(int[] xy : xySet) {
                    if(grid[xy[0]][xy[1]]>=thresh) cnt++;
                }
                ansGrid[i][j] = (float)(cnt/(double)xySet.size());
            }
        }
        return ansGrid;
    }
    
    public static float[][] getMaxInHood(float[][] grid, Collection<int[]> offsets) {
        if(grid==null) return null;
        
        int d1=grid.length, d2=grid[0].length;
        float[][] outputGrid = new float[d1][d2];
//        getMaxInHoodCore(0, d1, 0, d2, grid, offsets, outputGrid);
        forkJoinPool.invoke(new MaxInHood(0,d1,0,d2,grid, offsets, outputGrid));
        return grid;
    }
    
    public static void getMaxInHoodCore(int startD1, int endD1, int startD2, int endD2, float[][] inputGrid, Collection<int[]> offsets, float[][] outputGrid) {
        final int d1=inputGrid.length, d2=inputGrid[0].length;
        for(int i=startD1; i<endD1; i++) {
            for(int j=startD2; j<endD2; j++) {
                float max = inputGrid[i][j];
                for(int[] offset : offsets) {
                    final int x=i+offset[0], y=j+offset[1];
                    if(x>=0 && x<d1 && y>=0 && y<d2) {
                        final float v = inputGrid[x][y];
                        if(max<v) max = v;
                    }
                }
                outputGrid[i][j] = max;
            }
        }
    }
    
   static ForkJoinPool forkJoinPool = new ForkJoinPool();
    static int splitThreshold = 100;
 
    @SuppressWarnings("serial")
    static class MaxInHood extends RecursiveAction {
        final float[][] inputGrid, outputGrid;
        final List<int[]> offsets;
        final int startD1, endD1, startD2, endD2;
        
        MaxInHood(int startD1, int endD1, int startD2, int endD2, float[][] inputGrid, Collection<int[]> offsets, float[][] outputGrid) {
            this.startD1 = startD1;             this.endD1 = endD1;
            this.startD2 = startD2;             this.endD2 = endD2;
            this.inputGrid = inputGrid;      this.outputGrid = outputGrid;
            this.offsets = new ArrayList<>(offsets);
       }
        
        protected void compute() {
            int deltaD1 = endD1-startD1;
            int deltaD2 = endD2-startD2;
            if (deltaD1*deltaD2 < splitThreshold) {
                getMaxInHoodCore(deltaD2, deltaD2, deltaD1, deltaD2, inputGrid, offsets, outputGrid);
            } else {
                if(deltaD1>deltaD2) {
                    int midD1 = (startD1+endD1) >>> 1;
                    invokeAll(new MaxInHood(startD1, midD1, startD2, endD2, inputGrid, offsets, outputGrid),
                                      new MaxInHood(midD1, endD1, startD2, endD2, inputGrid, offsets, outputGrid));   
                } else {
                    int midD2 = (startD2+endD2) >>> 1;
                    invokeAll(new MaxInHood(startD1, endD1, startD2, midD2, inputGrid, offsets, outputGrid),
                                      new MaxInHood(startD1, endD1, midD2, endD2, inputGrid, offsets, outputGrid));   
                }
            }
        }
    }





}
