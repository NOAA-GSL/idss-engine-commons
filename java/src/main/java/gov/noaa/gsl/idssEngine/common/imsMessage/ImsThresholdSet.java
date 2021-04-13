/*******************************************************************************
 * Copyright (c) 2020 Regents of the University of Colorado. All rights reserved.
 *
 * Contributors:
 *     Geary Layne
 *******************************************************************************/
package gov.noaa.gsl.idssEngine.common.imsMessage;

import java.util.Arrays;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;
import java.util.UUID;

import gov.noaa.gsl.idssEngine.common.aspect.Model;

public class ImsThresholdSet {

//    public final int arealPercentage;              //0 = 1 gridpoint, 100 = entire bufferedGeometry area
//    public final int duration;                              //0 = Any Occurence, Value is in minutes
    public final ImsThreshold[] thresholds;
    public final Map<String, Object> attrMap = new HashMap<>();

    private static final String useFcst = "useForecast";
    private static final String useObs = "useObservations";
    private static final String duration = "duration";
    private static final String arealPct = "arealPercentage";
    private static final String specModels = "specModel";
    
    public ImsThresholdSet(boolean useFcst, boolean useObs, double duration, double arealPct, Set<Model> specModels, Map<String, Object> attrMap, ImsThreshold[] thresholds) {
        this.attrMap.putAll(attrMap);
        this.thresholds = Arrays.copyOf(thresholds, thresholds.length);
        this.attrMap.put(ImsThresholdSet.useFcst, useFcst);
        this.attrMap.put(ImsThresholdSet.useObs, useObs);
        this.attrMap.put(ImsThresholdSet.duration, duration);
        this.attrMap.put(ImsThresholdSet.arealPct, arealPct);
        this.attrMap.put(ImsThresholdSet.specModels, specModels);
    }
    
    public String getName() {
        return attrMap.get("name").toString();
    }
    public UUID getId() {
        return UUID.fromString(getIdString());
    }
    public String getIdString() {
        return attrMap.get("id").toString();
    }
    
    public boolean useFcst() {      
        try{
            return getBool(attrMap.get(useFcst));
        } catch(Exception e) {
            throw new RuntimeException("Unable to detirmine if Forecast should be used");   
        }
    }

    public boolean useObs() {      
        try{
            return getBool(attrMap.get(useObs));
        } catch(Exception e) {
            throw new RuntimeException("Unable to detirmine if Observation should be used");   
        }
    }
    
    public double getDuration() {
        try{
            return getDouble(attrMap.get(duration));
        } catch(Exception e) {
            throw new RuntimeException("Unable to detirmine the Duration");   
        }
    }
    
    public double getArealPercentage() {
        try{
            return getDouble(attrMap.get(arealPct));
        } catch(Exception e) {
            throw new RuntimeException("Unable to detirmine the ArealPercentage");   
        }
    }
    
    public Set<Model> getSpecModel() {
        return getModels(attrMap.get(specModels));
    }
    
    private boolean getBool(Object obj) {
        if(obj==null)
            return false;
        if(obj.getClass() == Boolean.class)
             return (Boolean)obj;
        if(obj.getClass() == String.class)
            return Boolean.parseBoolean((String)obj);
        throw new IllegalArgumentException();
    }
 
    private double getDouble(Object obj) {
        if(obj==null)
            return 0.0;
        if(obj.getClass() == Double.class)
             return (Double)obj;
        if(obj.getClass() == Integer.class)
            return (Integer)obj;
        throw new IllegalArgumentException();
    }      
    
//    private String getString(Object obj) {
//        if(obj==null)
//            return "";
//        if(obj.getClass() == String.class)
//             return (String)obj;
//        throw new IllegalArgumentException();
//    }      
    
   private Set<Model> getModels(Object obj) {
        if(obj==null)
            return null;
//System.out.println(obj.getClass());
//System.out.println(Set.class.isAssignableFrom(obj.getClass()));
        if(Set.class.isAssignableFrom(obj.getClass())) {
            Set<?> set = (Set<?>)obj;
            if(set.size()==0) return null;
//System.out.println(set.iterator().next().getClass());
            if(set.iterator().next().getClass() == Model.class) {
                Set<Model> modelSet = new HashSet<Model>();
                for(Object model : set) {
                    switch((Model)model) {
                        case ALL:
                            for(Model m : Model.allModels) modelSet.add(m);
                            break;
                        case ANY:
                            modelSet.add(Model.allModels[0]);
                            break;
                        default:
                            modelSet.add((Model)model); 
                    }
                }
//TODO GJL remove hack to limit to only HRRR
//modelSet.clear();
//modelSet.add(Model.HRRR);
                return modelSet;
            }
        }
        
        throw new IllegalArgumentException();
    }  
}
