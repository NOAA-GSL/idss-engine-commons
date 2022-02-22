/*******************************************************************************
 * Copyright (c) 2020 Regents of the University of Colorado. All rights reserved.
 *
 * Contributors:
 *     Geary Layne
 *******************************************************************************/
package gov.noaa.gsl.idssEngine.commons.aspect;

import java.util.HashMap;
import java.util.Map;

public enum Field {
    
    // new ImsElement type should be added to lookup map    
    RAIN1HR,
    RAIN3HR,
    RAIN6HR,
    RAIN12HR,
    RAIN24HR,
    SNOW1HR,
    SNOW3HR,
    SNOW6HR,
    SNOW12HR,
    SNOW24HR,
    ICE1HR,
    ICE3HR,
    ICE6HR,
    ICE12HR,
    ICE24HR,
    TEMP,
    RH,
    TD,
    VIS,
    CIG,
    WINDSPEED,
    WINDGUST,
    WINDDIR,
    WINDCHILL,
    HEATINDEX,
    LIGHTNING,
    
    SPCSEVERE,
    SPCFIRE,
    WXTYPEIS,
    WPCRAINFALL,
    
    WXRAIN,
    WXSNOW,
    WXFRZR,
    WXTHDR,

    WXFRZP,

    WBGT,
    
    RDSBFRZP,
    ;

    // Declaring the static lookup map 
    private static Map<String, Field> map; 
  
    // Instantiating the static map, must be on entry per IElement type
    static
    { 
        map = new HashMap<>(); 

        map.put("1 hour rainfall", RAIN1HR);
        map.put("1 HR RAINFALL", RAIN1HR);
        map.put("3 hour rainfall", RAIN3HR);
        map.put("3 HR RAINFALL", RAIN3HR);
        map.put("6 hour rainfall", RAIN6HR);
        map.put("6 HR RAINFALL", RAIN6HR);
        map.put("12 hour rainfall", RAIN12HR);
        map.put("12 HR RAINFALL", RAIN12HR);
        map.put("24 hour rainfall", RAIN24HR);
        map.put("24 HR RAINFALL", RAIN24HR);
        
        map.put("1 hour snowfall", SNOW1HR);
        map.put("1 HR SNOWFALL", SNOW1HR);
        map.put("3 hour snowfall", SNOW3HR);
        map.put("3 HR SNOWFALL", SNOW3HR);
        map.put("6 hour snowfall", SNOW6HR);
        map.put("6 HR SNOWFALL", SNOW6HR);
        map.put("12 hour snowfall", SNOW12HR);
        map.put("12 HR SNOWFALL", SNOW12HR);
        map.put("24 hour snowfall", SNOW24HR);
        map.put("24 HR SNOWFALL", SNOW24HR);

        map.put("1 hour ice accumulation", ICE1HR);
        map.put("1 HR ICE ACCUMULATION", ICE1HR);
        map.put("3 hour ice accumulation", ICE3HR);
        map.put("3 HR ICE ACCUMULATION", ICE3HR);
        map.put("6 hour ice accumulation", ICE6HR);
        map.put("6 HR ICE ACCUMULATION", ICE6HR);
        map.put("12 hour ice accumulation", ICE12HR);
        map.put("12 HR ICE ACCUMULATION", ICE12HR);
        map.put("24 hour ice accumulation", ICE24HR);
        map.put("24 HR ICE ACCUMULATION", ICE24HR);

        map.put("Temperature", TEMP);
        map.put("TEMPERATURE", TEMP);
        
        map.put("Relative Humidity", RH);
        map.put("RELATIVE HUMIDITY", RH);

        map.put("Dewpoint", TD);
        map.put("DEWPOINT", TD);

        map.put("Visibility", VIS);
        map.put("VISIBILITY", VIS);

        map.put("Ceiling", CIG);
        map.put("CEILING", CIG);

        map.put("Wind Speed", WINDSPEED);
        map.put("Wind Speed (Sustained)", WINDSPEED);
        map.put("WIND SPEED", WINDSPEED);

        map.put("Wind Gust", WINDGUST);
        map.put("WIND GUST", WINDGUST);
        
        map.put("Wind Direction", WINDDIR);
        map.put("WIND DIRECTION", WINDDIR);
        
        map.put("Wind Chill", WINDCHILL);
        map.put("WIND CHILL", WINDCHILL);

        map.put("Heat Index", HEATINDEX);
        map.put("HEAT INDEX", HEATINDEX);
        
        map.put("Lightning", LIGHTNING);
        map.put("LIGHTNING", LIGHTNING);

        map.put("WEATHER TYPE INCLUDES RAIN", WXRAIN);
        map.put("WEATHER TYPE INCLUDES SNOW", WXSNOW);
        map.put("WEATHER TYPE INCLUDES FREEZING RAIN", WXFRZR);
        map.put("WEATHER TYPE INCLUDES THUNDERSTORM", WXTHDR);

        map.put("WEATHER TYPE INCLUDES FREEZING PRECIP", WXFRZP);
        map.put("FREEZING PRECIP", WXFRZP);

        map.put("RDSBFRZP", RDSBFRZP);
        map.put("Road Subfreeze", RDSBFRZP);
        map.put("ROAD SUBFREEZE", RDSBFRZP);

    } 

    public static Field get(String fieldString) {
        if(fieldString.startsWith("CHANCE OF ")) fieldString = fieldString.substring(10);
        else if(fieldString.startsWith("PROB OF ")) fieldString = fieldString.substring(8);
//System.out.println("->"+fieldString+"<-");
        Field field = map.get(fieldString);
        if(field == null)  
            field = valueOf(fieldString);
        if(field == null)
            throw new IllegalArgumentException("Invalid element string ("+fieldString+")");
        return field;
    }
    
    public static Units getUnits(Field elm) {
        switch(elm) {
//            case Ceiling:
//                return Units.Feet;
//            case Dewpoint:
//                return Units.Fahrenheit;
//            case HeatIndex:
//                return Units.Fahrenheit;
//            case IceAccumulation:
//                return Units.Inches;
//            case Lightning:
//                return Units.Strikes;
//            case ProbPrecipGT1in1:
//                return Units.Percent;
//            case ProbPrecipGT1in3:
//                return Units.Percent;
//            case ProbPrecipGT2in1:
//                return Units.Percent;
//            case ProbPrecipGT2in3:
//                return Units.Percent;
//            case ProbPrecipGT3in3:
//                return Units.Percent;
//            case Rainfall:
//                return Units.Inches;
//            case RelativeHumidity:
//                return Units.Percent;
//            case RiverStage:
//                return Units.Inches;
//            case Snowfall:
//                return Units.Inches;
//            case Temperature:
//                return Units.Fahrenheit;
//            case Visibility:
//                return Units.Miles;
//            case WBGT:
//                return Units.Fahrenheit;
//            case WindChill:
//                return Units.Fahrenheit;
//            case WindDirection:
//                return Units.DegreesNorth;
//            case WindGust:
//                return Units.MilesPerHour;
//            case WindSpeed:
//                return Units.MilesPerHour;
            case RAIN1HR:
            case RAIN3HR:
            case RAIN6HR:
            case RAIN12HR:
            case RAIN24HR:
            case SNOW1HR:
            case SNOW3HR:
            case SNOW6HR:
            case SNOW12HR:
            case SNOW24HR:
            case ICE1HR:
            case ICE3HR:
            case ICE6HR:
            case ICE12HR:
            case ICE24HR:
                return Units.Inches;
            case TEMP:
                return Units.Fahrenheit;
            case RH:
                    return Units.Percent;
            case TD:
                return Units.Fahrenheit;
            case VIS:
                return Units.Miles;
            case CIG:
                return Units.Feet;
            case WINDSPEED:
            case WINDGUST:
                return Units.MilesPerHour;
            case WINDDIR: 
                return Units.DegreesNorth;
            case LIGHTNING:
                return Units.Strikes;  
            case SPCSEVERE:
            case SPCFIRE:
                return Units.Level;
            case WXTYPEIS:
                return Units.Cat;
            case WPCRAINFALL:
                return Units.Percent;
            case WXFRZR:
                return Units.Bool;
            case WXFRZP:
                return Units.Bool;

            default:
                throw new RuntimeException("Passed Field does not have orresponding Units");
        }
    }
    
   


}
