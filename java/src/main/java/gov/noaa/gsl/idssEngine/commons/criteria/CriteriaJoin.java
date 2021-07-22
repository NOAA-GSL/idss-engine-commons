/*******************************************************************************
 * Copyright (c) 2020 Regents of the University of Colorado. All rights reserved.
 *
 * Contributors:
 *     Geary Layne
 *******************************************************************************/
package gov.noaa.gsl.idssEngine.commons.criteria;

import java.awt.Point;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class CriteriaJoin {

    public enum Type {
        OR,
        AND;
    }
    
    public final String input1, input2, output;
    public final Type type;
    private static int idx = 0;
    
    private CriteriaJoin(Type type, String input1, String input2, String output) {
        this.type = type;
        this.input1 = input1;
        this.input2 = input2;
        this.output = output;
    }
    public static CriteriaJoin newAnd(String input1, String input2, String output) {
        return new CriteriaJoin(Type.AND, input1, input2, output);
    }
    public static CriteriaJoin newOr(String input1, String input2, String output) {
        return new CriteriaJoin(Type.OR, input1, input2, output);
    }    
  
    public static CriteriaJoin newAnd(String input1, String input2) {
        return new CriteriaJoin(Type.AND, input1, input2, "c"+getIdx());
    }
    public static CriteriaJoin newOr(String input1, String input2) {
        return new CriteriaJoin(Type.OR, input1, input2, "c"+getIdx());
    }   
    
    private static synchronized int getIdx() {
        return idx++;
    }
    
    //// Point data ////
    
    public static Map<Point, float[]> joinPointData(CriteriaJoin[] joins, Map<String, Map<Point, float[]>> criterionPointDataMap) {
        Map<String, Map<Point, float[]>> gridMap = new HashMap<>(criterionPointDataMap);
        List<CriteriaJoin> joinList = new ArrayList<>();
        for(CriteriaJoin join : joins) joinList.add(join);

        String lastOutput=null;
        while(!joinList.isEmpty()) {
            CriteriaJoin join = joinList.remove(0);
            Map<Point, float[]> points1 = gridMap.get(join.input1);
            Map<Point, float[]> points2 = gridMap.get(join.input2);
            if(points1!=null && points2!=null) {
                final Map<Point, float[]> points = joinPointData(join.type, points1, points2);
                if(points==null) return null;
                gridMap.put(join.output, points);
                lastOutput = join.output;
            } else {
                joinList.add(join);
            }
        }
        return gridMap.get(lastOutput);
    }

    private static Map<Point, float[]> joinPointData(Type type, Map<Point, float[]> points1, Map<Point, float[]> points2) {
        Map<Point, float[]> points = new HashMap<>();
        for(Point pnt : points1.keySet()) {
            points.put(pnt, joinArrays(type, points1.get(pnt), points2.get(pnt)));
        }
        return points;
    }
    
    //// Point data ////
    //// Grid data ////
    
    public static float[][] joinGridData(CriteriaJoin[] joins, Map<String, float[][]> criterionGridDataMap) {
        Map<String, float[][]> gridMap = new HashMap<>(criterionGridDataMap);
        List<CriteriaJoin> joinList = new ArrayList<>();
        for(CriteriaJoin join : joins) joinList.add(join);

        String lastOutput=null;
        while(!joinList.isEmpty()) {
            CriteriaJoin join = joinList.remove(0);
            float[][] grid1 = gridMap.get(join.input1);
            float[][] grid2 = gridMap.get(join.input2);
            if(grid1!=null && grid2!=null) {
                final float[][] grid = joinGrids(join.type, grid1, grid2);
                if(grid==null) return null;
                gridMap.put(join.output, grid);
                lastOutput = join.output;
            } else {
                joinList.add(join);
            }
        }
        return gridMap.get(lastOutput);
    }
    
    //// Grid data ////
    
    public static float[] joinArrays(Type type, float[] array1, float[] array2) {
        switch(type) {
            case AND:
                return joinAnd(array1, array2);
            case OR:
                return joinOr(array1, array2);
        }
        return null;
    }
    public static float[][] joinGrids(Type type, float[][] grid1, float[][] grid2) {
        switch(type) {
            case AND:
                return joinAnd(grid1, grid2);
            case OR:
                return joinOr(grid1, grid2);
        }
        return null;
    }
    
    public static float[] joinOr(float[] array1, float[] array2) {
        int len=array1.length;
        float[] array = new float[len];
        for(int i=0; i<len; i++) {
            array[i] = joinOr(array1[i], array2[i]);
        }
        return array;
    }
    public static float[][] joinOr(float[][] grid1, float[][] grid2) {
        int d1=grid1.length, d2=grid1[0].length;
        float[][] grid = new float[d1][d2];
        for(int i=0; i<d1; i++) {
            for(int j=0; j<d2; j++) {
                grid[i][j] = joinOr(grid1[i][j], grid2[i][j]);
            }
        }
        return grid;
    }
    
    public static float[] joinAnd(float[] array1, float[] array2) {
        int len=array1.length;
        float[] array = new float[len];
        for(int i=0; i<len; i++) {
            array[i] = joinAnd(array1[i], array2[i]);
        }
        return array;
    }    
    
    public static float[][] joinAnd(float[][] grid1, float[][] grid2) {
        int d1=grid1.length, d2=grid1[0].length;
        float[][] grid = new float[d1][d2];
        for(int i=0; i<d1; i++) {
            for(int j=0; j<d2; j++) {
                grid[i][j] =joinAnd(grid1[i][j], grid2[i][j]);
            }
        }
        return grid;
    }

    public static float joinOr(float v1, float v2) {
        return Math.max(v1, v2);
    }
    
    private static final double root2 = Math.sqrt(2);
    public static float joinAnd(float v1, float v2) {
        double v;
        if(v1>=0 && v2>=0) {
            v=Math.sqrt(v1*v1+v2*v2)/root2;
        } else if(v1>=0) {
            v=v2;
        } else if(v2>=0) {
            v=v1;
        } else {
            v=-Math.sqrt(v1*v1+v2*v2);
        }
       
        if(v>1) v=1;
        else if(v<-1) v=-1;
        
        return (float)v;
    }
    
    public String toString() {
        return String.format("CriteriaJoin(%s, %s, %s, %s)", type.toString(), input1, input2, output);
    }
}
