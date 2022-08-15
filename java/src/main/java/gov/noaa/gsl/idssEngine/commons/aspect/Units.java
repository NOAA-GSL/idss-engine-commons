/*******************************************************************************
 * Copyright (c) 2020 Regents of the University of Colorado. All rights reserved.
 *
 * Contributors:
 *     Geary Layne
 *******************************************************************************/
package gov.noaa.gsl.idssEngine.commons.aspect;

import java.util.HashMap;
import java.util.Map;

public enum Units  {
    
    // new IrisUnits type must be added to lookup map
    Inches,
    Feet,
    Miles,
    Meters,
    KgPerM2,
    MilesPerHour,
    MetersPerSecond,
    MetersPerHour,
    Fahrenheit,
    Kelvin,
    Celcius,
    Percent,
    Strikes,
    DegreesNorth,
    Pascals,
    MilliBars,
    InchesOfMercury,
    WattsPerM2,
    Level,
    Cat,
    Bool,
    None;
    
    public static Units get(String unitString) {
        Units units = map.get(unitString);
        if(units == null)  
            units = valueOf(unitString);
        if(units == null)
            throw new IllegalArgumentException("Invalid unit string ("+unitString+")");
        return units;
    }
    
    // Declaring the static lookup map 
    private static Map<String, Units> map; 
  
    // Instantiating the static map, must be on entry per IrisUnits type
    static
    { 
        map = new HashMap<>(); 
        map.put("inches", Inches); 
        map.put("INCHES", Inches); 
        map.put("feet", Feet); 
        map.put("FEET", Feet); 
        map.put("miles", Miles); 
        map.put("MILES", Miles); 
        map.put("m", Meters);
        map.put("meters", Meters);
        map.put("Meters", Meters);
        map.put("METERS", Meters);
        map.put("gpm", Meters);  //TODO, approximately true
        map.put("kg.m-2", KgPerM2);
        map.put("kgPerM2", KgPerM2);
        map.put("mph", MilesPerHour); 
        map.put("MPH", MilesPerHour); 
        map.put("milesPerHour", MilesPerHour); 
        map.put("MilesPerHour", MilesPerHour); 
        map.put("m/h", MetersPerHour); 
        map.put("m.s-1", MetersPerSecond); 
        map.put("m/s", MetersPerSecond); 
        map.put("metersPerSecond", MetersPerSecond); 
        map.put("MetersPerSecond", MetersPerSecond); 
        map.put("F", Fahrenheit); 
        map.put("DEG F", Fahrenheit); 
        map.put("K", Kelvin); 
        map.put("Kelvin", Kelvin); 
        map.put("C", Celcius); 
        map.put("Celcius", Celcius);         
        map.put("%", Percent);         
        map.put("Percent", Percent); 
        map.put("PERCENT", Percent); 
        map.put("strikes", Strikes); 
        map.put("DegreesN", DegreesNorth); 
        map.put("DEG N", DegreesNorth); 
        map.put("Pa",  Pascals);
        map.put("pascals",  Pascals);
        map.put("Pascals",  Pascals);
        map.put("millibars", MilliBars);
        map.put("inHg", InchesOfMercury);
        map.put("W.m-2", WattsPerM2);
        map.put("wattsPerM2", WattsPerM2);
        map.put("level", Level);
        map.put("catagory", Cat);
        map.put("bool", Bool);
        map.put("BOOL", Bool);
    } 


}
