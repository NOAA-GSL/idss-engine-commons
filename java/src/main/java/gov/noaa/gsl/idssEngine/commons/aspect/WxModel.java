/*********************************************************************************
  * Copyright (c) 2020 Regents of the University of Colorado. All rights reserved.
 *
 * Contributors:
 *     Geary Layne
*********************************************************************************/
package gov.noaa.gsl.idssEngine.commons.aspect;

import java.util.Arrays;
import java.util.HashMap;
import java.util.Map;

public enum WxModel {

    ALL,
    ANY,
    GFS,
    GEFS,
    HRRR,
    HRRRE,
    SREF,
    HREF,
    NBM,
    NDFD,
    NONE,
    ;
    
//    public static Model[] allModels = {GFS, GEFS,  HRRR, HRRRE, SREF, HREF, NBM, NDFD};
    public static WxModel[] allModels = {HRRR};
    
    // Declaring the static lookup map 
    private static Map<String, WxModel> map; 
  
    // Instantiating the static map, must be on entry per Weather Type
    static
    { 
        map = new HashMap<>(); 

        map.put("Any model", ANY);
        map.put("ANY MODEL", ANY);
        map.put("All models", ALL);
        map.put("ALL MODELS", ALL);
        map.put("GFS", GFS); 
        map.put("GEFS", GEFS);
        map.put("HRRR", HRRR); 
        map.put("HRRRE", HRRRE); 
        map.put("SREF", SREF);
        map.put("NBM", NBM);
        map.put("NDFD", NDFD);
        map.put("None", NONE);
    } 

    public static WxModel get(String modelString) {
        WxModel model = map.get(modelString);
        if(model == null)  
            model = valueOf(modelString);
        if(model == null)
            throw new IllegalArgumentException("Invalid Model string ("+modelString+")");
        return model;
    }

    public static WxModel[] getAllModels() {
        return Arrays.copyOf(allModels, allModels.length);
    }
    
    public static String[] getAllModelsAsStrings() {
        int len = allModels.length;
        String[] modelStrings = new String[len];
        int idx =0;
        for(WxModel model : allModels) modelStrings[idx++] = model.toString(); 
        return modelStrings;
    }
}
