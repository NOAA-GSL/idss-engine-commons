/*******************************************************************************
 * Copyright (c) 2020 Regents of the University of Colorado. All rights reserved.
 *
 * Contributors:
 *     Geary Layne
 *******************************************************************************/
package gov.noaa.gsl.idssEngine.common.criteriaStore;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;

import org.joda.time.DateTime;
import org.joda.time.Duration;

import gov.noaa.gsd.fiqas.cartography.Projection;
import gov.noaa.gsd.fiqas.util.io.NetcdfWrite;
import gov.noaa.gsd.fiqas.util.time.DateTimeFactory;

import gov.noaa.gsl.idssEngine.common.criteria.Criteria;
import gov.noaa.gsl.idssEngine.common.criteria.Criterion;

public class CriteriaGridStore extends CriteriaStore {
    
    final String rootDir;
    
    private boolean includeMeanWhenWrite = false;
    
    private Set<String> memberStringSet = new HashSet<>();
    private Map<DateTime, Map<String, Map<String, float[][]>>> criterionGridsMap = new HashMap<>();
    private Map<DateTime, Map<String, float[][]>> criteriaGridMap = new HashMap<>();
    private Map<DateTime, String> fileNameMap = null;
    
    
    public CriteriaGridStore(String product, DateTime issueDt, Criteria criteria, Projection proj) {
        this(product, issueDt, criteria, proj, null);
    }
    
    public CriteriaGridStore(String product, DateTime issueDt, Criteria criteria, Projection proj, String rootDir) {
        super(product, issueDt, criteria, proj);
        this.rootDir = rootDir;
    }
    
    public CriteriaGridStore(String product, DateTime issueDt, DateTime[] validDts, String[] fileNames) {
        super(product, issueDt, null, null);
       this.rootDir = null;

        memberStringSet = null;
        criteriaGridMap = null;
        criteriaGridMap = null;
        
        int len = validDts.length;
        fileNameMap = new HashMap<>();
        for(int i=0; i<len; i++) {
            fileNameMap.put(validDts[i], fileNames[i]);
        }
    }
    
    public void addCriterionGrid(DateTime validDt, String memberString, String criterionString, float[][] grid) {
        memberStringSet.add(memberString);
        getCriterionMap(validDt, memberString).put(criterionString, grid);
    }
  
    public void addCriteriaGrid(DateTime validDt, String memberString, float[][] grid) {
        memberStringSet.add(memberString);
        getCriteriaMap(validDt).put(memberString, grid);
    }
   
    public void addGrids(DateTime validDt, String memberString, float[][] criteriaGrid, Map<String, float[][]> gridsMap) {
        addGrids(validDt, memberString, gridsMap);
        addCriteriaGrid(validDt, memberString, criteriaGrid);
    }

    public void addGrids(DateTime validDt, String memberString, Map<String, float[][]> gridsMap) {
        String criteraKey = criteria.getKey();
        for(String keyString : gridsMap.keySet()) {
            if(keyString.equals(criteraKey))
                addCriteriaGrid(validDt, memberString, gridsMap.get(keyString));
            else
                addCriterionGrid(validDt, memberString, keyString, gridsMap.get(keyString));
        }
    }
    
    public float[][] getCriterionGrid(DateTime validDt, String memberString, String criterionString) {
        try {
            return criterionGridsMap.get(validDt).get(memberString).get(criterionString);
        } catch(Exception e1) {
            try {
                load(validDt, fileNameMap.get(validDt));
                return criterionGridsMap.get(validDt).get(memberString).get(criterionString);              
            } catch(Exception e2) {
                return null;
            }
        }
    }
    
    @Override
    public float[][] getCriteriaGrid(DateTime validDt, String memberString) {
         try {
            return criteriaGridMap.get(validDt).get(memberString);
        } catch(Exception e1) {
            try {
                load(validDt, fileNameMap.get(validDt));
                return criteriaGridMap.get(validDt).get(memberString);
            } catch(Exception e2) {
                return null;
            }
        }
    }

    private void load(DateTime validDt, String string) {
        // TODO Auto-generated method stub
        
    }

    public boolean flushToFile() {
        if(rootDir==null) return false;
        try {
            if(fileNameMap == null)
                fileNameMap = store(rootDir);
            else
                fileNameMap.putAll(store(rootDir));
            clearMaps();
            return true;
        } catch(Exception e) {
            throw new RuntimeException( "Failed to flush", e);
        }
    }
    
    private void clearMaps() {        
        criteriaGridMap.clear();
        criterionGridsMap.clear();
    }

    public Map<DateTime, String> store(String rootDir) {
        Map<DateTime, String> fileNameMap = new HashMap<>();
        for(DateTime validDt : criteriaGridMap.keySet()) {
            fileNameMap.put(validDt, store(validDt, rootDir));
        }
        return fileNameMap;
    }
    
    private  Map<String, float[][]> getCriteriaMap( DateTime validDt) {
        Map<String, float[][]> memberCriteriaGridsMap = criteriaGridMap.get(validDt);
        if(memberCriteriaGridsMap == null) {
            memberCriteriaGridsMap = new HashMap<>();
            criteriaGridMap.put(validDt, memberCriteriaGridsMap);
        }
        return memberCriteriaGridsMap;
    }

    private Map<String, float[][]> getCriterionMap(DateTime validDt, String memberString) {
        Map<String, Map<String, float[][]>> memberCriterionGridsMap = criterionGridsMap.get(validDt);
        if(memberCriterionGridsMap == null) {
            memberCriterionGridsMap = new HashMap<>();
            criterionGridsMap.put(validDt, memberCriterionGridsMap);
        }
        Map<String, float[][]> criterionMap = memberCriterionGridsMap.get(memberString);
        if(criterionMap == null) {
            criterionMap = new HashMap<>();
            memberCriterionGridsMap.put(memberString, criterionMap);
        }
        return criterionMap;
    }
    
    @Override
    public String write(DateTime validDt, String prefix, String outDir) {
        if(fileNameMap!=null && fileNameMap.containsKey(validDt)) {
            int leadInMin = (int)(new Duration(issueDt, validDt).getStandardMinutes());       

            String srcFileName = fileNameMap.get(validDt);
            String destFileName = String.format("%s/%s_%s", outDir, prefix, getFileName(product, issueDt, leadInMin, criteria));
            try {
                File dest = new File(destFileName);
                File src = new File(srcFileName);
                if(!src.equals(dest)) {
                    if(dest.exists()) dest.delete();
                    dest.getParentFile().mkdirs();
                    Files.copy(new File(fileNameMap.get(validDt)).toPath(), dest.toPath());
                }
                return destFileName;
            } catch( IOException e ) {
                throw new RuntimeException(e);
            }
        }
        return null;
    }
    
    private String store(DateTime validDt, String rootDir) {
        if(!criteriaGridMap.containsKey(validDt)) return null;

        int leadInMin = (int)(new Duration(issueDt, validDt).getStandardMinutes());       
        String fileName = getFullFileName(product, issueDt, leadInMin, criteria, rootDir);
        Map<String, float[][]> caGridMap = criteriaGridMap.get(validDt);
        Map<String, Map<String, float[][]>> cnGridsMap = criterionGridsMap.get(validDt);
        List<String> memberStrings = new ArrayList<>(memberStringSet);

        return store(issueDt, leadInMin, memberStrings, caGridMap, cnGridsMap, fileName);
    }
    
    private String store(DateTime issueDt, int leadInMin, List<String> memberStrings, 
                                             Map<String, float[][]> caGridMap, 
                                             Map<String, Map<String, float[][]>> cnGridsMap,
                                             String fileName) { 
        
       Collections.sort(memberStrings);
        
        Criterion[] criterions = criteria.criterions;
        int numCriterion = criterions.length;
        int numMember = memberStrings.size();
        String[] criterionKeys = new String[numCriterion];
        for(int i=0; i<numCriterion; i++) criterionKeys[i] = criterions[i].getKey();
        float[][][] memberCriteriaGrids = new float[numMember][][];
        float[][][][] memberCriterionGrids = new float[numMember][numCriterion][][];
        for(int i=0; i<numMember; i++) {
            String memberStr = memberStrings.get(i);
            final float[][] criteriaGrid = caGridMap.get(memberStr);
            
            if(criteriaGrid == null) return null;
            
            memberCriteriaGrids[i] = criteriaGrid;
            
            Map<String, float[][]> criterionGridMap = cnGridsMap.get(memberStr);
            for(int j=0; j<numCriterion; j++) {
                String key = criterionKeys[j];
                final float[][] criterionGrid = criterionGridMap.get(key);
                
                if(criterionGrid == null) return null;
                
                memberCriterionGrids[i][j] = criterionGrid;
            }
        }
                
        boolean success = writeNetcdf(product, issueDt, leadInMin, criteria, proj, memberCriterionGrids,
                                                                        memberCriteriaGrids, includeMeanWhenWrite, fileName);
        if(success)
            return fileName;
        return null;
    }
    
    private static float[][] getMean(int d1, int d2, float[][][] grids) {
        double numGrids = grids.length;
        float[][] grid = new float[d1][d2];
        for(int i=0; i<d1; i++) {
            for(int j=0; j<d2; j++) {
                double sum=0; for(int k=0; k<numGrids; k++) sum+=grids[k][i][j];
                grid[i][j] = (float)(sum/numGrids);
            }
        }
        return grid;
    }
    
    private static float[][][] getMean(int d1, int d2, float[][][][] grids) {
        int numMember = grids.length;
        int numCriterion = grids[0].length;
        float[][][] meanCriterionGrids = new float[numCriterion][][];
        float[][][] tmpCriterionGrids = new float[numMember][][];
        for(int i=0; i<numCriterion; i++) {
            for(int j=0; j<numMember; j++) {
                tmpCriterionGrids[j] = grids[j][i];
            }
            meanCriterionGrids[i] = getMean(d1, d2, tmpCriterionGrids);
        }
        return meanCriterionGrids;
    }
    
    public static boolean writeNetcdf(String product, DateTime issueDt, int leadInMin, Criteria criteria, Projection proj, 
                                                                           float[][][] criterionGrids, float[][] criteriaGrid, String fileName) {
        return writeNetcdf(product, issueDt, leadInMin, criteria, proj, new float[][][][] {criterionGrids}, new float[][][] {criteriaGrid}, false, fileName);
    }

    private static boolean writeNetcdf(String product, DateTime issueDt, int leadInMin, Criteria criteria, Projection proj, 
                                                                           float[][][][] memberCriterionGrids, float[][][] memberCriteriaGrids,
                                                                           boolean includeMean, String fileName) {
        
        float[][] meanCriteriaGrid = null;
        float[][][] meanCriterionGrids = null;
        
        if(includeMean) {
            int d1=proj.getIntendedWidth(), d2=proj.getIntendedHeight();
            meanCriteriaGrid = getMean(d1, d2, memberCriteriaGrids);
            meanCriterionGrids = getMean(d1, d2, memberCriterionGrids);
        }

        String mbrDimName = "member";
        String crtnDimName = "criterion";
        String xDimName = "x";
        String yDimName = "y";
        String meanCriteriaVarName = "mean_criteria";
        String meanCriterionsVarName = "mean_criterion";
        String mbrCriteriaVarName = "member_criteria";
        String mbrCriterionsVarName = "member_criterion";

        HashMap<String, Object> meanCriteriaAttrMap  = new HashMap<>();      
        NetcdfWrite.addOrderToAttrMap(meanCriteriaAttrMap, 1,0);
        NetcdfWrite.addDimNamesToAttrMap(meanCriteriaAttrMap, xDimName, yDimName);
        
        HashMap<String, Object> meanCriterionsAttrMap  = new HashMap<>();      
        NetcdfWrite.addOrderToAttrMap(meanCriterionsAttrMap, 0,2,1);
        NetcdfWrite.addDimNamesToAttrMap(meanCriterionsAttrMap, crtnDimName, xDimName, yDimName);
  
        HashMap<String, Object> mbrCriteriaAttrMap  = new HashMap<>();      
        NetcdfWrite.addOrderToAttrMap(mbrCriteriaAttrMap, 0,2,1);
        NetcdfWrite.addDimNamesToAttrMap(mbrCriteriaAttrMap, mbrDimName, xDimName, yDimName);
        
        HashMap<String, Object> mbrCriterionsAttrMap  = new HashMap<>();      
        NetcdfWrite.addOrderToAttrMap(mbrCriterionsAttrMap, 0,1,3,2);
        NetcdfWrite.addDimNamesToAttrMap(mbrCriterionsAttrMap, mbrDimName, crtnDimName, xDimName, yDimName);
      
        String[] varNames;
        if(includeMean) {
            varNames = new String[] {meanCriteriaVarName, meanCriterionsVarName, mbrCriteriaVarName, mbrCriterionsVarName};
        } else {
            varNames = new String[] {mbrCriteriaVarName, mbrCriterionsVarName};
        }
        
        List<Map<String, ?>> attrList = new ArrayList<>();
        if(includeMean) {
            attrList.add(meanCriteriaAttrMap);
            attrList.add(meanCriterionsAttrMap);
        }
        attrList.add(mbrCriteriaAttrMap);
        attrList.add(mbrCriterionsAttrMap);
       
        List<Object> dataList = new ArrayList<>();
        if(includeMean) {
            dataList.add(meanCriteriaGrid);
            dataList.add(meanCriterionGrids);
        }
        dataList.add(memberCriteriaGrids);
        dataList.add(memberCriterionGrids);
             
        Map<String, Object> globalAttrMap = new LinkedHashMap<>();
        globalAttrMap.put("title", criteria.name);
        globalAttrMap.put("issue", DateTimeFactory.getDateTimeString(issueDt));
        globalAttrMap.put("lead minutes", leadInMin);
        Criterion[] criterions = criteria.criterions;
        int len = criterions.length;
        for(int idx=0; idx<len; idx++)
            globalAttrMap.put("criterion "+idx, criterions[idx].getKey(false));        
        globalAttrMap.put("input model", product);
        
        globalAttrMap.put("proj string", proj.getProjSpec());
        globalAttrMap.put("grid string", proj.getGridSpec());
        double[] latlon = proj.mapXY(0, 0);
        globalAttrMap.put("lowLeftLat", Double.toString(latlon[0]));
        globalAttrMap.put("lowLeftLon", Double.toString(latlon[1]));
        
        NetcdfWrite.staticWrite(fileName, globalAttrMap, varNames, attrList, dataList);
        return true;
    }

    
    private static String getKey(Criteria criteria) {
        return criteria.getKey(false).replace(", ", "__").replace(' ','_').replace('.', 'p');
    }
    
    private static String getFileName(String product, DateTime issueDt, int leadInMin, Criteria criteria) {
        int leadHour = leadInMin/60;
        int leadMin = leadInMin%60;

        String fileName = String.format("%d%02d%02d_%02d%02d_%02d%02d.nc.gz", 
                                                                          issueDt.getYear(), issueDt.getMonthOfYear(), issueDt.getDayOfMonth(),
                                                                          issueDt.getHourOfDay(), issueDt.getMinuteOfHour(),
                                                                          leadHour, leadMin);
        return fileName;           
    }
    
    private static String getFullFileName(String product, DateTime issueDt, int leadInMin, Criteria criteria, String rootDir) {
        String fileName = String.format("%s/criteria/%s/%d/%02d/%02d/%s/%s", 
                                                                          rootDir, product, issueDt.getYear(), issueDt.getMonthOfYear(), issueDt.getDayOfMonth(),
                                                                          getKey(criteria), getFileName(product, issueDt, leadInMin, criteria));
        return fileName;
     }

//    @Override
//    public void clear() {
//        if(fileNameMap==null || fileNameMap.size()==0) return;
//        
//        for(String fileName : fileNameMap.values()) System.err.println("Delete: "+fileName);
//        
//        throw new RuntimeException("Delete files needs to be implemented");
//    }



}
