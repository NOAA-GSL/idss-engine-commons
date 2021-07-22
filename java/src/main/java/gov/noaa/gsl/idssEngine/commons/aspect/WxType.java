/*********************************************************************************
  * Copyright (c) 2020 Regents of the University of Colorado. All rights reserved.
 *
 * Contributors:
 *     Geary Layne
*********************************************************************************/
package gov.noaa.gsl.idssEngine.commons.aspect;

import java.util.HashMap;
import java.util.Map;

public enum WxType {

    RAIN,
    THUNDER,
    SNOW,
    ICE,
    SLEET,
    NONE,
    ;
    
    // Declaring the static lookup map 
    private static Map<String, WxType> map; 
  
    // Instantiating the static map, must be on entry per Weather Type
    static
    { 
        map = new HashMap<>(); 

        map.put("Rain", RAIN);
        map.put("Thunderstorms", THUNDER); 
        map.put("Snow", SNOW);
        map.put("Freezing Rain", ICE); 
        map.put("Sleet", SLEET);
        map.put("None", NONE);
    } 

    public static WxType get(String wxTypeString) {
        WxType wxType = map.get(wxTypeString);
        if(wxType == null)  
            wxType = valueOf(wxTypeString);
        if(wxType == null)
            throw new IllegalArgumentException("Invalid WxType string ("+wxTypeString+")");
        return wxType;
    }
}
