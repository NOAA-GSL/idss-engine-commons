/*******************************************************************************
 * Copyright (c) 2020 Regents of the University of Colorado. All rights reserved.
 *
 * Contributors:
 *     Geary Layne
 *******************************************************************************/
package gov.noaa.gsl.idssEngine.commons;

import gov.noaa.gsl.idssEngine.commons.aspect.Units;

public class UnitsConversion {
    
    public static final  double nineFifth = 9.0/5.0;
    public static final double fiveNinth = 5.0/9.0;

    public static float convert(Units srcUnits, Units destUnits, float value) {
        if(srcUnits == destUnits) return value;
        switch(srcUnits) {
        case Inches:
            return convertInches(destUnits, value);                        
        case Feet:
            return convertFeet(destUnits, value);            
        case Miles:
            return convertMiles(destUnits, value);
        case KgPerM2:
            return convertKgPerM2(destUnits, value);
        case Meters:
            return convertMeters(destUnits, value);            
        case Fahrenheit:
            return convertFahrenheit(destUnits, value);
        case Kelvin:
            return convertKelvin(destUnits, value);
        case Celcius:
            return convertCelcius(destUnits, value);
        case MetersPerSecond:
            return convertMetersPerSecond(destUnits, value);
        case MilesPerHour:
            return convertMilesPerHour(destUnits, value);
        case Knots:
            return convertKnots(destUnits, value);
        case Pascals:
            return convertPascals(destUnits, value);
        default:
        }
        throw new UnsupportedOperationException("Units covertion for ("+srcUnits+") not currently supported");
    }
    public static double convert(Units srcUnits, Units destUnits, double value) {
        if(srcUnits == destUnits) return value;
        switch(srcUnits) {
        case Inches:
            return convertInches(destUnits, value);                        
        case Feet:
            return convertFeet(destUnits, value);            
        case Miles:
            return convertMiles(destUnits, value);
        case KgPerM2:
            return convertKgPerM2(destUnits, value);
        case Meters:
            return convertMeters(destUnits, value);            
        case Fahrenheit:
            return convertFahrenheit(destUnits, value);
        case Kelvin:
            return convertKelvin(destUnits, value);
        case Celcius:
            return convertCelcius(destUnits, value);
        case MetersPerSecond:
            return convertMetersPerSecond(destUnits, value);
         case MilesPerHour:
            return convertMilesPerHour(destUnits, value);
        case Knots:
            return convertKnots(destUnits, value);
        case Pascals:
            return convertPascals(destUnits, value);
        default:
        }
        throw new UnsupportedOperationException("Units covertion for ("+srcUnits+") not currently supported");
    }

    public static float[] convert(Units srcUnits, Units destUnits, float[] array) {
        if(srcUnits == destUnits) return array;
        switch(srcUnits) {
        case Inches:
            return convertInches(destUnits, array);                        
        case Feet:
            return convertFeet(destUnits, array);            
        case Miles:
            return convertMiles(destUnits, array);
        case KgPerM2:
            return convertKgPerM2(destUnits, array);
        case Meters:
            return convertMeters(destUnits, array);            
        case Fahrenheit:
            return convertFahrenheit(destUnits, array);
        case Kelvin:
            return convertKelvin(destUnits, array);
        case Celcius:
            return convertCelcius(destUnits, array);
        case MetersPerSecond:
            return convertMetersPerSecond(destUnits, array);
        case MilesPerHour:
            return convertMilesPerHour(destUnits, array);
        case Knots:
            return convertKnots(destUnits, array);
         case Pascals:
            return convertPascals(destUnits, array);
        default:
        }
        throw new UnsupportedOperationException("Units covertion for ("+srcUnits+") not currently supported");
    }
    
    public static double[] convert(Units srcUnits, Units destUnits, double[] array) {
        if(srcUnits == destUnits) return array;
        switch(srcUnits) {
        case Inches:
            return convertInches(destUnits, array);                        
        case Feet:
            return convertFeet(destUnits, array);            
        case Miles:
            return convertMiles(destUnits, array);
        case KgPerM2:
            return convertKgPerM2(destUnits, array);
        case Meters:
            return convertMeters(destUnits, array);            
        case Fahrenheit:
            return convertFahrenheit(destUnits, array);
        case Kelvin:
            return convertKelvin(destUnits, array);
        case Celcius:
            return convertCelcius(destUnits, array);
        case MetersPerSecond:
            return convertMetersPerSecond(destUnits, array);
        case MilesPerHour:
            return convertMilesPerHour(destUnits, array);
        case Knots:
            return convertKnots(destUnits, array);
        case Pascals:
            return convertPascals(destUnits, array);
        default:
        }
        throw new UnsupportedOperationException("Units covertion for ("+srcUnits+") not currently supported");
    }
    
    public static float[][] convert(Units srcUnits, Units destUnits, float[][] grid) {
        if(srcUnits == destUnits) return grid;
        switch(srcUnits) {
        case Inches:
            return convertInches(destUnits, grid);                        
        case Feet:
            return convertFeet(destUnits, grid);            
        case Miles:
            return convertMiles(destUnits, grid);
        case KgPerM2:
            return convertKgPerM2(destUnits, grid);
        case Meters:
            return convertMeters(destUnits, grid);            
        case Fahrenheit:
            return convertFahrenheit(destUnits, grid);
        case Kelvin:
            return convertKelvin(destUnits, grid);
        case Celcius:
            return convertCelcius(destUnits, grid);
        case MetersPerSecond:
            return convertMetersPerSecond(destUnits, grid);
        case MilesPerHour:
            return convertMilesPerHour(destUnits, grid);
        case Knots:
            return convertKnots(destUnits, grid);
        case Pascals:
            return convertPascals(destUnits, grid);
        default:
        }
        throw new UnsupportedOperationException("Units covertion for ("+srcUnits+") not currently supported");
    }
    
    public static double[][] convert(Units srcUnits, Units destUnits, double[][] grid) {
        if(srcUnits == destUnits) return grid;
        switch(srcUnits) {
        case Inches:
            return convertInches(destUnits, grid);                        
        case Feet:
            return convertFeet(destUnits, grid);            
        case Miles:
            return convertMiles(destUnits, grid);
        case KgPerM2:
            return convertKgPerM2(destUnits, grid);
        case Meters:
            return convertMeters(destUnits, grid);            
        case Fahrenheit:
            return convertFahrenheit(destUnits, grid);
        case Kelvin:
            return convertKelvin(destUnits, grid);
        case Celcius:
            return convertCelcius(destUnits, grid);
        case MetersPerSecond:
            return convertMetersPerSecond(destUnits, grid);
        case MilesPerHour:
            return convertMilesPerHour(destUnits, grid);
        case Knots:
            return convertKnots(destUnits, grid);
         case Pascals:
            return convertPascals(destUnits, grid);
       default:
        }
        throw new UnsupportedOperationException("Units covertion for ("+srcUnits+") not currently supported");
    }
    
    ////////////////////////////////////// convert Inches ///////////////////////////////////////////////
    public static float convertInches(Units destUnits, float value) {
        switch(destUnits) {
        case Inches:
            return value;                        
        case Feet:
            return inchesToFeet(value);            
        case Miles:
            return inchesToMiles(value);
        case Meters:
            return inchesToMeters(value);            
        case KgPerM2:
            return inchesToKgPerM2(value);
        default:
        }
        throw new UnsupportedOperationException("Units covertion from inches to ("+destUnits+") not currently supported");
    }
    public static double convertInches(Units destUnits, double value) {
        switch(destUnits) {
        case Inches:
            return value;                        
        case Feet:
            return inchesToFeet(value);            
        case Miles:
            return inchesToMiles(value);
        case Meters:
            return inchesToMeters(value);            
        case KgPerM2:
            return inchesToKgPerM2(value);
        default:
        }
        throw new UnsupportedOperationException("Units covertion from inches to ("+destUnits+") not currently supported");
    }
    
    public static float[] convertInches(Units destUnits, float[] array) {
        switch(destUnits) {
        case Inches:
            return array;                        
//        case Feet:
//            return inchesToFeet(grid);            
//        case Miles:
//            return inchesToMiles(grid);
//        case Meters:
//            return inchesToMeters(grid);            
//        case KgPerM2:
//            return inchesToKgPerM2(grid);
        default:
        }
        throw new UnsupportedOperationException("Units covertion from inches to ("+destUnits+") not currently supported");
    }
    public static double[] convertInches(Units destUnits, double[] array) {
        switch(destUnits) {
        case Inches:
            return array;                        
//        case Feet:
//            return inchesToFeet(grid);            
//        case Miles:
//            return inchesToMiles(grid);
//        case Meters:
//            return inchesToMeters(grid);            
//        case KgPerM2:
//            return inchesToKgPerM2(grid);
        default:
        }
        throw new UnsupportedOperationException("Units covertion from inches to ("+destUnits+") not currently supported");
    }    
    public static float[][] convertInches(Units destUnits, float[][] grid) {
        switch(destUnits) {
        case Inches:
            return grid;                        
//        case Feet:
//            return inchesToFeet(grid);            
//        case Miles:
//            return inchesToMiles(grid);
//        case Meters:
//            return inchesToMeters(grid);            
//        case KgPerM2:
//            return inchesToKgPerM2(grid);
        default:
        }
        throw new UnsupportedOperationException("Units covertion from inches to ("+destUnits+") not currently supported");
    }
    public static double[][] convertInches(Units destUnits, double[][] grid) {
        switch(destUnits) {
        case Inches:
            return grid;                        
//        case Feet:
//            return inchesToFeet(grid);            
//        case Miles:
//            return inchesToMiles(grid);
//        case Meters:
//            return inchesToMeters(grid);            
//        case KgPerM2:
//            return inchesToKgPerM2(grid);
        default:
        }
        throw new UnsupportedOperationException("Units covertion from inches to ("+destUnits+") not currently supported");
    }
    ////////////////////////////////////// convert Inches ///////////////////////////////////////////////
    ////////////////////////////////////// convert Feet //////////////////////////////////////////////////
    
    public static float convertFeet(Units destUnits, float value) {
        switch(destUnits) {
        case Inches:
            return feetToInches(value);                        
        case Feet:
            return value;            
        case Miles:
            return feetToMiles(value);
        case Meters:
            return feetToMeters(value);            
        case KgPerM2:
            return feetToKgPerM2(value);
        default:
        }
        throw new UnsupportedOperationException("Units covertion from feet to ("+destUnits+") not currently supported");
    }
    public static double convertFeet(Units destUnits, double value) {
        switch(destUnits) {
        case Inches:
            return feetToInches(value);                        
        case Feet:
            return value;            
        case Miles:
            return feetToMiles(value);
        case Meters:
            return feetToMeters(value);            
        case KgPerM2:
            return feetToKgPerM2(value);
        default:
        }
        throw new UnsupportedOperationException("Units covertion from feet to ("+destUnits+") not currently supported");
    }
    public static float[] convertFeet(Units destUnits, float[] array) {
        switch(destUnits) {
        case Inches:
            return feetToInches(array);                        
        case Feet:
            return array;            
        case Miles:
            return feetToMiles(array);
        case Meters:
            return feetToMeters(array);            
        case KgPerM2:
            return feetToKgPerM2(array);
        default:
        }
        throw new UnsupportedOperationException("Units covertion from feet to ("+destUnits+") not currently supported");
    } 
    public static double[] convertFeet(Units destUnits, double[] array) {
        switch(destUnits) {
        case Inches:
            return feetToInches(array);                        
        case Feet:
            return array;            
        case Miles:
            return feetToMiles(array);
        case Meters:
            return feetToMeters(array);            
        case KgPerM2:
            return feetToKgPerM2(array);
        default:
        }
        throw new UnsupportedOperationException("Units covertion from feet to ("+destUnits+") not currently supported");
    } 
    public static float[][] convertFeet(Units destUnits, float[][] grid) {
        switch(destUnits) {
        case Inches:
            return feetToInches(grid);                        
        case Feet:
            return grid;            
        case Miles:
            return feetToMiles(grid);
        case Meters:
            return feetToMeters(grid);            
        case KgPerM2:
            return feetToKgPerM2(grid);
        default:
        }
        throw new UnsupportedOperationException("Units covertion from feet to ("+destUnits+") not currently supported");
    }    
    ////////////////////////////////////// convert Feet //////////////////////////////////////////////////
    ////////////////////////////////////// convert Meters ///////////////////////////////////////////////
    
    public static float convertMeters(Units destUnits, float value) {
        switch(destUnits) {
        case Inches:
            return metersToInches(value);                        
        case Feet:
            return metersToFeet(value);            
        case Miles:
            return metersToMiles(value);
        case Meters:
            return value;            
//        case KgPerM2:
//            return metersToKgPerM2(value);
        default:
        }
        throw new UnsupportedOperationException("Units covertion from meters to ("+destUnits+") not currently supported");
    }
    public static double convertMeters(Units destUnits, double value) {
        switch(destUnits) {
        case Inches:
            return metersToInches(value);                        
        case Feet:
            return metersToFeet(value);            
        case Miles:
            return metersToMiles(value);
        case Meters:
            return value;         
//        case KgPerM2:
//            return metersToKgPerM2(value);
        default:
        }
        throw new UnsupportedOperationException("Units covertion from meters to ("+destUnits+") not currently supported");
    }

    public static float[] convertMeters(Units destUnits, float[] array) {
        switch(destUnits) {
        case Inches:
            return metersToInches(array);                        
        case Feet:
            return metersToFeet(array);            
        case Miles:
            return metersToMiles(array);
        case Meters:
            return array;     
//        case KgPerM2:
//            return metersToKgPerM2(grid);
        default:
        }
        throw new UnsupportedOperationException("Units covertion from meters to ("+destUnits+") not currently supported");
    }
    public static double[] convertMeters(Units destUnits, double[] array) {
        switch(destUnits) {
        case Inches:
            return metersToInches(array);                        
        case Feet:
            return metersToFeet(array);            
        case Miles:
            return metersToMiles(array);
        case Meters:
            return array;   
//        case KgPerM2:
//            return metersToKgPerM2(grid);
        default:
        }
        throw new UnsupportedOperationException("Units covertion from meters to ("+destUnits+") not currently supported");
    }
    public static float[][] convertMeters(Units destUnits, float[][] grid) {
        switch(destUnits) {
        case Inches:
            return metersToInches(grid);                        
        case Feet:
            return metersToFeet(grid);            
        case Miles:
            return metersToMiles(grid);
        case Meters:
            return grid;     
//        case KgPerM2:
//            return metersToKgPerM2(grid);
        default:
        }
        throw new UnsupportedOperationException("Units covertion from meters to ("+destUnits+") not currently supported");
    }
    public static double[][] convertMeters(Units destUnits, double[][] grid) {
        switch(destUnits) {
        case Inches:
            return metersToInches(grid);                        
        case Feet:
            return metersToFeet(grid);            
        case Miles:
            return metersToMiles(grid);
        case Meters:
            return grid;   
//        case KgPerM2:
//            return metersToKgPerM2(grid);
        default:
        }
        throw new UnsupportedOperationException("Units covertion from meters to ("+destUnits+") not currently supported");
    }
    
    ////////////////////////////////////// convert Meters ///////////////////////////////////////////////
    ////////////////////////////////////// convert Miles /////////////////////////////////////////////////

    public static float convertMiles(Units destUnits, float value) {
        switch(destUnits) {
        case Inches:
            return milesToInches(value);                        
        case Feet:
            return milesToFeet(value);            
        case Miles:
            return value;
        case Meters:
            return milesToMeters(value);            
        default:
        }
        throw new UnsupportedOperationException("Units covertion from miles to ("+destUnits+") not currently supported");
    }
    public static double convertMiles(Units destUnits, double value) {
        switch(destUnits) {
        case Inches:
            return milesToInches(value);                        
        case Feet:
            return milesToFeet(value);            
        case Miles:
            return value;
        case Meters:
            return milesToMeters(value);            
        default:
        }
        throw new UnsupportedOperationException("Units covertion from miles to ("+destUnits+") not currently supported");
    }
    public static float[] convertMiles(Units destUnits, float[] array) {
        switch(destUnits) {
        case Inches:
            return milesToInches(array);                        
        case Feet:
            return milesToFeet(array);            
        case Miles:
            return array;
        case Meters:
            return milesToMeters(array);            
        default:
        }
        throw new UnsupportedOperationException("Units covertion from miles to ("+destUnits+") not currently supported");
    }
    public static float[][] convertMiles(Units destUnits, float[][] grid) {
        switch(destUnits) {
        case Inches:
            return milesToInches(grid);                        
        case Feet:
            return milesToFeet(grid);            
        case Miles:
            return grid;
        case Meters:
            return milesToMeters(grid);            
        default:
        }
        throw new UnsupportedOperationException("Units covertion from miles to ("+destUnits+") not currently supported");
    }
    public static double[] convertMiles(Units destUnits, double[] array) {
        switch(destUnits) {
        case Inches:
            return milesToInches(array);                        
        case Feet:
            return milesToFeet(array);            
        case Miles:
            return array;
        case Meters:
            return milesToMeters(array);            
        default:
        }
        throw new UnsupportedOperationException("Units covertion from miles to ("+destUnits+") not currently supported");
    }
    public static double[][] convertMiles(Units destUnits, double[][] grid) {
        switch(destUnits) {
        case Inches:
            return milesToInches(grid);                        
        case Feet:
            return milesToFeet(grid);            
        case Miles:
            return grid;
        case Meters:
            return milesToMeters(grid);         
        default:
        }
        throw new UnsupportedOperationException("Units covertion from miles to ("+destUnits+") not currently supported");
    }
    
    ////////////////////////////////////// convert Miles /////////////////////////////////////////////////
    ////////////////////////////////////// convert KgPerM2 ////////////////////////////////////////////

    public static float convertKgPerM2(Units destUnits, float value) {
        switch(destUnits) {
        case Inches:
            return kgPerM2ToInches(value);                          
        case KgPerM2:
            return value;
        default:
        }
        throw new UnsupportedOperationException("Units covertion from kgPerM2 to ("+destUnits+") not currently supported");
    }
    
    public static double convertKgPerM2(Units destUnits, double value) {
        throw new UnsupportedOperationException("Implement this convertion");
    }

    public static float[] convertKgPerM2(Units destUnits, float[] array) {
        switch(destUnits) {
        case Inches:
            return kgPerM2ToInches(array);                          
        case KgPerM2:
            return array;
        default:
        }
        throw new UnsupportedOperationException("Units covertion from kgPerM2 to ("+destUnits+") not currently supported");
    }
    
    public static double[] convertKgPerM2(Units destUnits, double[] array) {
        switch(destUnits) {
        case Inches:
            return kgPerM2ToInches(array);                          
        case KgPerM2:
            return array;
        default:
        }
        throw new UnsupportedOperationException("Units covertion from kgPerM2 to ("+destUnits+") not currently supported");
    }
    
    public static float[][] convertKgPerM2(Units destUnits, float[][] grid) {
        switch(destUnits) {
        case Inches:
            return kgPerM2ToInches(grid);                          
        case KgPerM2:
            return grid;
        default:
        }
        throw new UnsupportedOperationException("Units covertion from kgPerM2 to ("+destUnits+") not currently supported");
    }
    
    public static double[][] convertKgPerM2(Units destUnits, double[][] grid) {
        throw new UnsupportedOperationException("Implement this convertion");
    }    

    ////////////////////////////////////// convert KgPerM2 ////////////////////////////////////////////
    ////////////////////////////////////// convert Fahrenheit ///////////////////////////////////////////

    public static float convertFahrenheit(Units destUnits, float value) {
        switch(destUnits) {
        case Kelvin:
            return fahrenheitToKelvin(value);                        
        default:
        }
        throw new UnsupportedOperationException("Implement this convertion for ("+destUnits+")");
    }
    
    public static double convertFahrenheit(Units destUnits, double value) {
        switch(destUnits) {
        case Kelvin:
            return fahrenheitToKelvin(value);                        
        default:
        }
        throw new UnsupportedOperationException("Implement this convertion for ("+destUnits+")");
    }

    public static float[] convertFahrenheit(Units destUnits, float[] array) {
        switch(destUnits) {
        case Kelvin:
            return fahrenheitToKelvin(array);                        
        default:
        }
        throw new UnsupportedOperationException("Implement this convertion for ("+destUnits+")");
    }
    public static double[] convertFahrenheit(Units destUnits, double[] array) {
        switch(destUnits) {
        case Kelvin:
            return fahrenheitToKelvin(array);                        
        default:
        }
        throw new UnsupportedOperationException("Implement this convertion for ("+destUnits+")");
    }
    
    public static float[][] convertFahrenheit(Units destUnits, float[][] grid) {
        switch(destUnits) {
        case Kelvin:
            return fahrenheitToKelvin(grid);                        
        default:
        }
        throw new UnsupportedOperationException("Implement this convertion for ("+destUnits+")");
    }
    public static double[][] convertFahrenheit(Units destUnits, double[][] grid) {
        switch(destUnits) {
        case Kelvin:
            return fahrenheitToKelvin(grid);                        
        default:
        }
        throw new UnsupportedOperationException("Implement this convertion for ("+destUnits+")");
    }
    
    ////////////////////////////////////// convert Fahrenheit //////////////////////////////////////////
    ////////////////////////////////////// convert Kelvin ////////////////////////////////////////////////

    public static float convertKelvin(Units destUnits, float value) {
        switch(destUnits) {
        case Fahrenheit:
            return kelvinToFahrenheit(value);                        
        case Celcius:
            return kelvinToCelcius(value);                        
        default:
        }
        throw new UnsupportedOperationException("Implement this convertion for ("+destUnits+")");
    }
    
    public static double convertKelvin(Units destUnits, double value) {
        switch(destUnits) {
        case Fahrenheit:
            return kelvinToFahrenheit(value);                        
        case Celcius:
            return kelvinToCelcius(value);                        
        default:
        }
        throw new UnsupportedOperationException("Implement this convertion for ("+destUnits+")");
    }
    
    public static float[] convertKelvin(Units destUnits, float[] array) {
        switch(destUnits) {
        case Fahrenheit:
            return kelvinToFahrenheit(array);                        
        case Celcius:
            return kelvinToCelcius(array);                        
        default:
        }
        throw new UnsupportedOperationException("Implement this convertion for ("+destUnits+")");
    }
    public static double[] convertKelvin(Units destUnits, double[] array) {
        switch(destUnits) {
        case Fahrenheit:
            return kelvinToFahrenheit(array);                        
        case Celcius:
            return kelvinToCelcius(array);                        
        default:
        }
        throw new UnsupportedOperationException("Implement this convertion for ("+destUnits+")");
    }
    
    public static float[][] convertKelvin(Units destUnits, float[][] grid) {
        switch(destUnits) {
        case Fahrenheit:
            return kelvinToFahrenheit(grid);                        
        case Celcius:
            return kelvinToCelcius(grid);                        
        default:
        }
        throw new UnsupportedOperationException("Implement this convertion for ("+destUnits+")");
    }
    public static double[][] convertKelvin(Units destUnits, double[][] grid) {
        switch(destUnits) {
        case Fahrenheit:
            return kelvinToFahrenheit(grid);                        
        case Celcius:
            return kelvinToCelcius(grid);                        
        default:
        }
        throw new UnsupportedOperationException("Implement this convertion for ("+destUnits+")");
    }
    
    ////////////////////////////////////// convert Kelvin ////////////////////////////////////////////////
    ////////////////////////////////////// convert Celcius ////////////////////////////////////////////////

    public static float convertCelcius(Units destUnits, float value) {
        switch(destUnits) {
        case Fahrenheit:
            return celciusToFahrenheit(value);                            
        default:
        }
        throw new UnsupportedOperationException("Implement this convertion for ("+destUnits+")");
    }
    
    public static double convertCelcius(Units destUnits, double value) {
        switch(destUnits) {
        case Fahrenheit:
            return celciusToFahrenheit(value);                     
        default:
        }
        throw new UnsupportedOperationException("Implement this convertion for ("+destUnits+")");
    }

    public static float[] convertCelcius(Units destUnits, float[] array) {
        switch(destUnits) {
        case Fahrenheit:
            return celciusToFahrenheit(array);                            
        default:
        }
        throw new UnsupportedOperationException("Implement this convertion for ("+destUnits+")");
    }
    
    public static double[] convertCelcius(Units destUnits, double[] array) {
        switch(destUnits) {
        case Fahrenheit:
            return celciusToFahrenheit(array);                     
        default:
        }
        throw new UnsupportedOperationException("Implement this convertion for ("+destUnits+")");
    }
    
    public static float[][] convertCelcius(Units destUnits, float[][] grid) {
        switch(destUnits) {
        case Fahrenheit:
            return celciusToFahrenheit(grid);                        
        default:
        }
        throw new UnsupportedOperationException("Implement this convertion for ("+destUnits+")");
    }
    public static double[][] convertCelcius(Units destUnits, double[][] grid) {
        switch(destUnits) {
        case Fahrenheit:
            return celciusToFahrenheit(grid);                                             
        default:
        }
        throw new UnsupportedOperationException("Implement this convertion for ("+destUnits+")");
    }
    
    ////////////////////////////////////// convert Celcius //////////////////////////////////////////////
    ////////////////////////////////////// convert Pascals ////////////////////////////////////////////// 

    public static float convertPascals(Units destUnits, float value) {
        switch(destUnits) {
        case MilliBars:
            return pascalsToMilliBars(value);        
        case InchesOfMercury:
            return pascalsToInchesOfMercury(value);
        default:
        }
        throw new UnsupportedOperationException("Implement this convertion for ("+destUnits+")");
    }
    
    public static double convertPascals(Units destUnits, double value) {
        switch(destUnits) {
        case MilliBars:
            return pascalsToMilliBars(value);                        
        case InchesOfMercury:
            return pascalsToInchesOfMercury(value);
        default:
        }
        throw new UnsupportedOperationException("Implement this convertion for ("+destUnits+")");
    }
    
    public static float[] convertPascals(Units destUnits, float[] array) {
        switch(destUnits) {
        case MilliBars:
            return pascalsToMilliBars(array);        
        case InchesOfMercury:
            return pascalsToInchesOfMercury(array);
        default:
        }
        throw new UnsupportedOperationException("Implement this convertion for ("+destUnits+")");
    }
    
    public static double[] convertPascals(Units destUnits, double[] array) {
        switch(destUnits) {
        case MilliBars:
            return pascalsToMilliBars(array);                        
        case InchesOfMercury:
            return pascalsToInchesOfMercury(array);
        default:
        }
        throw new UnsupportedOperationException("Implement this convertion for ("+destUnits+")");
    }

    public static float[][] convertPascals(Units destUnits, float[][] grid) {
        switch(destUnits) {
        case MilliBars:
            return pascalsToMilliBars(grid);                        
        case InchesOfMercury:
            return pascalsToInchesOfMercury(grid);
        default:
        }
        throw new UnsupportedOperationException("Implement this convertion for ("+destUnits+")");
    }
    public static double[][] convertPascals(Units destUnits, double[][] grid) {
        switch(destUnits) {
        case MilliBars:
            return pascalsToMilliBars(grid);                        
        case InchesOfMercury:
            return pascalsToInchesOfMercury(grid);
       default:
        }
        throw new UnsupportedOperationException("Implement this convertion for ("+destUnits+")");
    }
    
    ////////////////////////////////////// convert Pascals //////////////////////////////////////////////    
    ////////////////////////////////////// convert MetersPerSecond /////////////////////////////////    

    public static float convertMetersPerSecond(Units destUnits, float value) {
        switch(destUnits) {
        case MilesPerHour:
            return metersPerSecToMilesPerHour(value);                        
        case MetersPerHour:
            return metersPerSecToMetersPerHour(value);    
        case Knots:
            return metersPerSecToKnots(value);
        default:
        }
        throw new UnsupportedOperationException("Implement this convertion for ("+destUnits+")");
    }
    
    public static double convertMetersPerSecond(Units destUnits, double value) {
        switch(destUnits) {
        case MilesPerHour:
            return metersPerSecToMilesPerHour(value);                        
        case MetersPerHour:
            return metersPerSecToMetersPerHour(value);                        
        case Knots:
            return metersPerSecToKnots(value);
        default:
        }
        throw new UnsupportedOperationException("Implement this convertion for ("+destUnits+")");
    }

    public static float[] convertMetersPerSecond(Units destUnits, float[] array) {
        switch(destUnits) {
        case MilesPerHour:
            return metersPerSecToMilesPerHour(array);                        
        case MetersPerHour:
            return metersPerSecToMetersPerHour(array);                        
        case Knots:
            return metersPerSecToKnots(array);
        default:
        }
        throw new UnsupportedOperationException("Implement this convertion for ("+destUnits+")");
    }
    
    public static double[] convertMetersPerSecond(Units destUnits, double[] array) {
        switch(destUnits) {
        case MilesPerHour:
            return metersPerSecToMilesPerHour(array);                        
        case MetersPerHour:
            return metersPerSecToMetersPerHour(array);                        
        case Knots:
            return metersPerSecToKnots(array);
        default:
        }
        throw new UnsupportedOperationException("Implement this convertion for ("+destUnits+")");
    }
    public static float[][] convertMetersPerSecond(Units destUnits, float[][] grid) {
        switch(destUnits) {
        case MilesPerHour:
            return metersPerSecToMilesPerHour(grid);                        
        case MetersPerHour:
            return metersPerSecToMetersPerHour(grid);                        
        case Knots:
            return metersPerSecToKnots(grid);
        default:
        }
        throw new UnsupportedOperationException("Implement this convertion for ("+destUnits+")");
    }
    public static double[][] convertMetersPerSecond(Units destUnits, double[][] grid) {
        switch(destUnits) {
        case MilesPerHour:
            return metersPerSecToMilesPerHour(grid);                        
        case MetersPerHour:
            return metersPerSecToMetersPerHour(grid);                        
        case Knots:
            return metersPerSecToKnots(grid);
        default:
        }
        throw new UnsupportedOperationException("Implement this convertion for ("+destUnits+")");
    }
    
    ////////////////////////////////////// convert MetersPerSecond /////////////////////////////////    
    ////////////////////////////////////// convert MilesPerHour ////////////////////////////////////////    

    public static float convertMilesPerHour(Units destUnits, float value) {
        switch(destUnits) {
        case MetersPerSec:
            return milesPerHourToMetersPerSec(value);                        
        case MetersPerHour:
            return milesPerHourToMetersPerHour(value);    
        case Knots:
            return milesPerHourToKnots(value);
        default:
        }
        throw new UnsupportedOperationException("Implement this convertion for ("+destUnits+")");
    }
    
    public static double convertMilesPerHour(Units destUnits, double value) {
        switch(destUnits) {
        case MetersPerSec:
            return milesPerHourToMetersPerSec(value);                        
        case MetersPerHour:
            return milesPerHourToMetersPerHour(value);                        
        case Knots:
            return milesPerHourToKnots(value);
        default:
        }
        throw new UnsupportedOperationException("Implement this convertion for ("+destUnits+")");
    }

    public static float[] convertMilesPerHour(Units destUnits, float[] array) {
        switch(destUnits) {
        case MetersPerSec:
            return milesPerHourToMetersPerSec(array);                        
        case MetersPerHour:
            return milesPerHourToMetersPerHour(array);                        
        case Knots:
            return milesPerHourToKnots(array);
        default:
        }
        throw new UnsupportedOperationException("Implement this convertion for ("+destUnits+")");
    }
    
    public static double[] convertMilesPerHour(Units destUnits, double[] array) {
        switch(destUnits) {
        case MetersPerSec:
            return milesPerHourToMetersPerSec(array);                        
        case MetersPerHour:
            return milesPerHourToMetersPerHour(array);                        
        case Knots:
            return milesPerHourToKnots(array);
        default:
        }
        throw new UnsupportedOperationException("Implement this convertion for ("+destUnits+")");
    }
    public static float[][] convertMilesPerHour(Units destUnits, float[][] grid) {
        switch(destUnits) {
        case MetersPerSec:
            return milesPerHourToMetersPerSec(grid);                        
        case MetersPerHour:
            return milesPerHourToMetersPerHour(grid);                        
        case Knots:
            return milesPerHourToKnots(grid);
        default:
        }
        throw new UnsupportedOperationException("Implement this convertion for ("+destUnits+")");
    }
    public static double[][] convertMilesPerHour(Units destUnits, double[][] grid) {
        switch(destUnits) {
        case MetersPerSec:
            return milesPerHourToMetersPerSec(grid);                        
        case MetersPerHour:
            return milesPerHourToMetersPerHour(grid);                        
        case Knots:
            return milesPerHourToKnots(grid);
        default:
        }
        throw new UnsupportedOperationException("Implement this convertion for ("+destUnits+")");
    }
    
    ////////////////////////////////////// convert MilesPerHour //////////////////////////////////////    
    ////////////////////////////////////// convert Fahrenheit ///////////////////////////////////////////

    public static float fahrenheitToKelvin(float value) {
        return (float)((value - 32) * fiveNinth + 273.15);
    }
    public static double fahrenheitToKelvin(double value) {
        return (value - 32) * fiveNinth + 273.15;
    }
    public static float[] fahrenheitToKelvin(float[] array) {
        for(int i=array.length-1; i>=0; i--) {
            array[i] = (float)((array[i] - 32) * fiveNinth + 273.15);
        }
        return array;
    }    
    public static double[] fahrenheitToKelvin(double[] array) {
        for(int i=array.length-1; i>=0; i--) {
            array[i] = (array[i] - 32) * fiveNinth + 273.15;
        }
        return array;
    }
    public static float[][] fahrenheitToKelvin(float[][] grid) {
        int d1=grid.length, d2=grid[0].length;
        for(int i=0; i<d1; i++) {
            for(int j=0; j<d2; j++) {
                grid[i][j] = (float)((grid[i][j] - 32) * fiveNinth + 273.15);
            }
        }
        return grid;
    }    
    public static double[][] fahrenheitToKelvin(double[][] grid) {
        int d1=grid.length, d2=grid[0].length;
        for(int i=0; i<d1; i++) {
            for(int j=0; j<d2; j++) {
                grid[i][j] = (grid[i][j] - 32) * fiveNinth + 273.15;
            }
        }
        return grid;
    }
    
    ////////////////////////////////////// convert Fahrenheit ///////////////////////////////////////////
    ////////////////////////////////////// convert Kelvin /////////////////////////////////////////////////

    public static float kelvinToFahrenheit(float value) {
        return (float)((value - 273.15) * nineFifth + 32);
    }
    public static double kelvinToFahrenheit(double value) {
        return (value - 273.15) * nineFifth + 32;
    }
    public static float[] kelvinToFahrenheit(float[] array) {
        for(int i=array.length-1; i>=0; i--) {
            array[i] = (float)((array[i] - 273.15) * nineFifth + 32);
        }
        return array;
    }    
    public static double[] kelvinToFahrenheit(double[] array) {
        for(int i=array.length-1; i>=0; i--) {
            array[i] = (array[i] - 273.15) * nineFifth + 32;
        }
        return array;
    }
    public static float[][] kelvinToFahrenheit(float[][] grid) {
        int d1=grid.length, d2=grid[0].length;
        for(int i=0; i<d1; i++) {
            for(int j=0; j<d2; j++) {
                grid[i][j] = (float)((grid[i][j] - 273.15) * nineFifth + 32);
            }
        }
        return grid;
    }    
    public static double[][] kelvinToFahrenheit(double[][] grid) {
        int d1=grid.length, d2=grid[0].length;
        for(int i=0; i<d1; i++) {
            for(int j=0; j<d2; j++) {
                grid[i][j] = (grid[i][j] - 273.15) * nineFifth + 32;
            }
        }
        return grid;
    }

    public static float kelvinToCelcius(float value) {
        return (float)(value - 273.15);
    }
    public static double kelvinToCelcius(double value) {
        return value - 273.15;
    }
    public static float[]kelvinToCelcius(float[] array) {
        for(int i=array.length-1; i>=0; i--) {
            array[i] = (float)(array[i] - 273.15);
        }
        return array;
    }
    public static double[] kelvinToCelcius(double[] array) {
        for(int i=array.length-1; i>=0; i--) {
            array[i] = array[i] - 273.15;
        }
        return array;
   }
    public static float[][] kelvinToCelcius(float[][] grid) {
        int d1=grid.length, d2=grid[0].length;
        for(int i=0; i<d1; i++) {
            for(int j=0; j<d2; j++) {
                grid[i][j] = (float)(grid[i][j] - 273.15);
            }
        }
        return grid;
    }    
    public static double[][] kelvinToCelcius(double[][] grid) {
        int d1=grid.length, d2=grid[0].length;
        for(int i=0; i<d1; i++) {
            for(int j=0; j<d2; j++) {
                grid[i][j] = (grid[i][j] - 273.15);
            }
        }
        return grid;
    }

    ////////////////////////////////////// convert Kelvin /////////////////////////////////////////////////
    ////////////////////////////////////// convert Celcius /////////////////////////////////////////////////
    
     public static float celciusToFahrenheit(float value) {
        return (float)(value * nineFifth + 32);
    }
    public static double celciusToFahrenheit(double value) {
        return value * nineFifth + 32;
    }
    public static float[] celciusToFahrenheit(float[] array) {
        for(int i=array.length-1; i>=0; i--) {
                array[i] = (float)(array[i] * nineFifth + 32);
        }
        return array;
    }    
    public static double[] celciusToFahrenheit(double[] array) {
         for(int i=array.length-1; i>=0; i--) {
                array[i] = array[i] * nineFifth + 32;
        }
        return array;
    }
    public static float[][] celciusToFahrenheit(float[][] grid) {
        int d1=grid.length, d2=grid[0].length;
        for(int i=0; i<d1; i++) {
            for(int j=0; j<d2; j++) {
                grid[i][j] = (float)(grid[i][j] * nineFifth + 32);
            }
        }
        return grid;
    }    
    public static double[][] celciusToFahrenheit(double[][] grid) {
        int d1=grid.length, d2=grid[0].length;
        for(int i=0; i<d1; i++) {
            for(int j=0; j<d2; j++) {
                grid[i][j] = (grid[i][j] * nineFifth + 32);
            }
        }
        return grid;
    }

    ////////////////////////////////////// convert Celcius ///////////////////////////////////////////////
    ////////////////////////////////////// convert Pascals ///////////////////////////////////////////////

    public static float pascalsToMilliBars(float value) {
        return (float)(value / 100.0);
    }
    public static double pascalsToMilliBars(double value) {
        return (value / 100.0);
    }
    public static float[] pascalsToMilliBars(float[] array) {
        for(int i=array.length-1; i>=0; i--) {
                array[i] = (float)(array[i] / 100.0);
        }
        return array;
    }    
    public static double[] pascalsToMilliBars(double[] array) {
         for(int i=array.length-1; i>=0; i--) {
                array[i] = array[i] / 100.0;
        }
        return array;
    }
    public static float[][] pascalsToMilliBars(float[][] grid) {
        int d1=grid.length, d2=grid[0].length;
        for(int i=0; i<d1; i++) {
            for(int j=0; j<d2; j++) {
                grid[i][j] = (float)(grid[i][j] / 100.0);
            }
        }
        return grid;
    }    
    public static double[][] pascalsToMilliBars(double[][] grid) {
        int d1=grid.length, d2=grid[0].length;
        for(int i=0; i<d1; i++) {
            for(int j=0; j<d2; j++) {
                grid[i][j] = (grid[i][j] / 100.0);
            }
        }
        return grid;
    }
    
   public static float pascalsToInchesOfMercury(float value) {
        return (float)(value / 3386.4);
    }
    public static double pascalsToInchesOfMercury(double value) {
        return (value / 3386.4);
    }
    public static float[] pascalsToInchesOfMercury(float[] array) {
        for(int i=array.length-1; i>=0; i--) {
                array[i] = (float)(array[i] / 3386.4);
        }
        return array;
    }    
    public static double[] pascalsToInchesOfMercury(double[] array) {
         for(int i=array.length-1; i>=0; i--) {
                array[i] = array[i] / 3386.4;
        }
        return array;
    }
    public static float[][] pascalsToInchesOfMercury(float[][] grid) {
        int d1=grid.length, d2=grid[0].length;
        for(int i=0; i<d1; i++) {
            for(int j=0; j<d2; j++) {
                grid[i][j] = (float)(grid[i][j] / 3386.4);
            }
        }
        return grid;
    }    
    public static double[][] pascalsToInchesOfMercury(double[][] grid) {
        int d1=grid.length, d2=grid[0].length;
        for(int i=0; i<d1; i++) {
            for(int j=0; j<d2; j++) {
                grid[i][j] = (grid[i][j] / 3386.4);
            }
        }
        return grid;
    }
    
    ////////////////////////////////////// convert Pascals ///////////////////////////////////////////////
    ////////////////////////////////////// convert MetersPerSec ///////////////////////////////////////
   
    public static float metersPerSecToMilesPerHour(float value) {
        return (float)(value * 2.23693629);
    }
    public static double metersPerSecToMilesPerHour(double value) {
        return (value * 2.23693629);
    }
    public static float[] metersPerSecToMilesPerHour(float[] array) {
         for(int i=array.length-1; i>=0; i--) {
            array[i] = (float)((array[i] * 2.23693629));
        }
        return array;
    }    
    public static double[] metersPerSecToMilesPerHour(double[] array) {
         for(int i=array.length-1; i>=0; i--) {
            array[i] = (array[i] * 2.23693629);
        }
        return array;
    }
    public static float[][] metersPerSecToMilesPerHour(float[][] grid) {
        int d1=grid.length, d2=grid[0].length;
        for(int i=0; i<d1; i++) {
            for(int j=0; j<d2; j++) {
                grid[i][j] = (float)((grid[i][j] * 2.23693629));
            }
        }
        return grid;
    }    
    public static double[][] metersPerSecToMilesPerHour(double[][] grid) {
        int d1=grid.length, d2=grid[0].length;
        for(int i=0; i<d1; i++) {
            for(int j=0; j<d2; j++) {
                grid[i][j] = (grid[i][j] * 2.23693629);
            }
        }
        return grid;
    }
    
    public static float metersPerSecToMetersPerHour(float value) {
        return (float)(value * 3600.0);
    }
    public static double metersPerSecToMetersPerHour(double value) {
        return (value * 3600.0);
    }
    public static float[] metersPerSecToMetersPerHour(float[] array) {
         for(int i=array.length-1; i>=0; i--) {
            array[i] = (float)((array[i] * 3600.0));
        }
        return array;
    }    
    public static double[] metersPerSecToMetersPerHour(double[] array) {
         for(int i=array.length-1; i>=0; i--) {
            array[i] = (array[i] * 3600.0);
        }
        return array;
    }
    public static float[][] metersPerSecToMetersPerHour(float[][] grid) {
        int d1=grid.length, d2=grid[0].length;
        for(int i=0; i<d1; i++) {
            for(int j=0; j<d2; j++) {
                grid[i][j] = (float)((grid[i][j] * 3600.0));
            }
        }
        return grid;
    }    
    public static double[][] metersPerSecToMetersPerHour(double[][] grid) {
        int d1=grid.length, d2=grid[0].length;
        for(int i=0; i<d1; i++) {
            for(int j=0; j<d2; j++) {
                grid[i][j] = (grid[i][j] * 3600.0);
            }
        }
        return grid;
    }
    
    public static float metersPerSecToKnots(float value) {
        return (float)(value * 1.94384449);
    }
    public static double metersPerSecToKnots(double value) {
        return (value * 1.94384449);
    }
    public static float[] metersPerSecToKnots(float[] array) {
         for(int i=array.length-1; i>=0; i--) {
            array[i] = (float)((array[i] * 1.94384449));
        }
        return array;
    }    
    public static double[] metersPerSecToKnots(double[] array) {
         for(int i=array.length-1; i>=0; i--) {
            array[i] = (array[i] * 1.94384449);
        }
        return array;
    }
    public static float[][] metersPerSecToKnots(float[][] grid) {
        int d1=grid.length, d2=grid[0].length;
        for(int i=0; i<d1; i++) {
            for(int j=0; j<d2; j++) {
                grid[i][j] = (float)((grid[i][j] * 1.94384449));
            }
        }
        return grid;
    }    
    public static double[][] metersPerSecToKnots(double[][] grid) {
        int d1=grid.length, d2=grid[0].length;
        for(int i=0; i<d1; i++) {
            for(int j=0; j<d2; j++) {
                grid[i][j] = (grid[i][j] * 1.94384449);
            }
        }
        return grid;
    }
    
    ////////////////////////////////////// convert MetersPerSec ///////////////////////////////////////
    ////////////////////////////////////// convert MilesPerHour ////////////////////////////////////////
   
    public static float milesPerHourToMetersPerSec(float value) {
        return (float)(value * 0.44704);
    }
    public static double milesPerHourToMetersPerSec(double value) {
        return (value * 0.44704);
    }
    public static float[] milesPerHourToMetersPerSec(float[] array) {
         for(int i=array.length-1; i>=0; i--) {
            array[i] = (float)((array[i] * 0.44704));
        }
        return array;
    }    
    public static double[] milesPerHourToMetersPerSec(double[] array) {
         for(int i=array.length-1; i>=0; i--) {
            array[i] = (array[i] * 0.44704);
        }
        return array;
    }
    public static float[][] milesPerHourToMetersPerSec(float[][] grid) {
        int d1=grid.length, d2=grid[0].length;
        for(int i=0; i<d1; i++) {
            for(int j=0; j<d2; j++) {
                grid[i][j] = (float)((grid[i][j] * 0.44704));
            }
        }
        return grid;
    }    
    public static double[][] milesPerHourToMetersPerSec(double[][] grid) {
        int d1=grid.length, d2=grid[0].length;
        for(int i=0; i<d1; i++) {
            for(int j=0; j<d2; j++) {
                grid[i][j] = (grid[i][j] * 0.44704);
            }
        }
        return grid;
    }
    
    public static float milesPerHourToMetersPerHour(float value) {
        return (float)(value * 1609.344);
    }
    public static double milesPerHourToMetersPerHour(double value) {
        return (value * 1609.344);
    }
    public static float[] milesPerHourToMetersPerHour(float[] array) {
         for(int i=array.length-1; i>=0; i--) {
            array[i] = (float)((array[i] * 1609.344));
        }
        return array;
    }    
    public static double[] milesPerHourToMetersPerHour(double[] array) {
         for(int i=array.length-1; i>=0; i--) {
            array[i] = (array[i] * 1609.344);
        }
        return array;
    }
    public static float[][] milesPerHourToMetersPerHour(float[][] grid) {
        int d1=grid.length, d2=grid[0].length;
        for(int i=0; i<d1; i++) {
            for(int j=0; j<d2; j++) {
                grid[i][j] = (float)((grid[i][j] * 1609.344));
            }
        }
        return grid;
    }    
    public static double[][] milesPerHourToMetersPerHour(double[][] grid) {
        int d1=grid.length, d2=grid[0].length;
        for(int i=0; i<d1; i++) {
            for(int j=0; j<d2; j++) {
                grid[i][j] = (grid[i][j] * 1609.344);
            }
        }
        return grid;
    }
    
    public static float milesPerHourToKnots(float value) {
        return (float)(value * 0.868976242);
    }
    public static double milesPerHourToKnots(double value) {
        return (value * 0.868976242);
    }
    public static float[] milesPerHourToKnots(float[] array) {
         for(int i=array.length-1; i>=0; i--) {
            array[i] = (float)((array[i] * 0.868976242));
        }
        return array;
    }    
    public static double[] milesPerHourToKnots(double[] array) {
         for(int i=array.length-1; i>=0; i--) {
            array[i] = (array[i] * 0.868976242);
        }
        return array;
    }
    public static float[][] milesPerHourToKnots(float[][] grid) {
        int d1=grid.length, d2=grid[0].length;
        for(int i=0; i<d1; i++) {
            for(int j=0; j<d2; j++) {
                grid[i][j] = (float)((grid[i][j] * 0.868976242));
            }
        }
        return grid;
    }    
    public static double[][] milesPerHourToKnots(double[][] grid) {
        int d1=grid.length, d2=grid[0].length;
        for(int i=0; i<d1; i++) {
            for(int j=0; j<d2; j++) {
                grid[i][j] = (grid[i][j] * 0.868976242);
            }
        }
        return grid;
    }
    
    ////////////////////////////////////// convert MilesPerHour ////////////////////////////////////////
    ////////////////////////////////////// convert Knots ////////////////////////////////////////////////////
   
    public static float knotsToMetersPerSec(float value) {
        return (float)(value * 0.514444445);
    }
    public static double knotsToMetersPerSec(double value) {
        return (value * 0.514444445);
    }
    public static float[] knotsToMetersPerSec(float[] array) {
         for(int i=array.length-1; i>=0; i--) {
            array[i] = (float)((array[i] * 0.514444445));
        }
        return array;
    }    
    public static double[] knotsToMetersPerSec(double[] array) {
         for(int i=array.length-1; i>=0; i--) {
            array[i] = (array[i] * 0.514444445);
        }
        return array;
    }
    public static float[][] knotsToMetersPerSec(float[][] grid) {
        int d1=grid.length, d2=grid[0].length;
        for(int i=0; i<d1; i++) {
            for(int j=0; j<d2; j++) {
                grid[i][j] = (float)((grid[i][j] * 0.514444445));
            }
        }
        return grid;
    }    
    public static double[][] knotsToMetersPerSec(double[][] grid) {
        int d1=grid.length, d2=grid[0].length;
        for(int i=0; i<d1; i++) {
            for(int j=0; j<d2; j++) {
                grid[i][j] = (grid[i][j] * 0.514444445);
            }
        }
        return grid;
    }
    
    public static float knotsToMetersPerHour(float value) {
        return (float)(value * 1852.0);
    }
    public static double knotsToMetersPerHour(double value) {
        return (value * 1852.0);
    }
    public static float[] knotsToMetersPerHour(float[] array) {
         for(int i=array.length-1; i>=0; i--) {
            array[i] = (float)((array[i] * 1852.0));
        }
        return array;
    }    
    public static double[] knotsToMetersPerHour(double[] array) {
         for(int i=array.length-1; i>=0; i--) {
            array[i] = (array[i] * 1852.0);
        }
        return array;
    }
    public static float[][] knotsToMetersPerHour(float[][] grid) {
        int d1=grid.length, d2=grid[0].length;
        for(int i=0; i<d1; i++) {
            for(int j=0; j<d2; j++) {
                grid[i][j] = (float)((grid[i][j] * 1852.0));
            }
        }
        return grid;
    }    
    public static double[][] knotsToMetersPerHour(double[][] grid) {
        int d1=grid.length, d2=grid[0].length;
        for(int i=0; i<d1; i++) {
            for(int j=0; j<d2; j++) {
                grid[i][j] = (grid[i][j] * 1852.0);
            }
        }
        return grid;
    }
    
    public static float knotsToMilesPerHour(float value) {
        return (float)(value * 1.150779448);
    }
    public static double knotsToMilesPerHour(double value) {
        return (value * 1.150779448);
    }
    public static float[] knotsToMilesPerHour(float[] array) {
         for(int i=array.length-1; i>=0; i--) {
            array[i] = (float)((array[i] * 1.150779448));
        }
        return array;
    }    
    public static double[] knotsToMilesPerHour(double[] array) {
         for(int i=array.length-1; i>=0; i--) {
            array[i] = (array[i] * 1.150779448);
        }
        return array;
    }
    public static float[][] knotsToMilesPerHour(float[][] grid) {
        int d1=grid.length, d2=grid[0].length;
        for(int i=0; i<d1; i++) {
            for(int j=0; j<d2; j++) {
                grid[i][j] = (float)((grid[i][j] * 1.150779448));
            }
        }
        return grid;
    }    
    public static double[][] knotsToMilesPerHour(double[][] grid) {
        int d1=grid.length, d2=grid[0].length;
        for(int i=0; i<d1; i++) {
            for(int j=0; j<d2; j++) {
                grid[i][j] = (grid[i][j] * 1.150779448);
            }
        }
        return grid;
    }
    
    ////////////////////////////////////// convert Knots ////////////////////////////////////////////////////
    ////////////////////////////////////// convert Feet //////////////////////////////////////////////////////

    public static float feetToInches(float feet) {
        return (float)(feet*12.0);
    }
    public static double feetToInches(double feet) {
        return feet*12.0;
    }
    public static float[] feetToInches(float[] array) {
        for(int i=array.length-1; i>=0; i--) {
            array[i] = (float)(array[i]*12.0);
        }
        return array;
    }
    public static double[] feetToInches(double[] array) {
        for(int i=array.length-1; i>=0; i--) {
            array[i] = array[i]*12.0;
        }
        return array;
    }
    public static float[][] feetToInches(float[][] grid) {
        int d1=grid.length, d2=grid[0].length;
        for(int i=0; i<d1; i++) {
            for(int j=0; j<d2; j++) {
                grid[i][j] = (float)(grid[i][j]*12.0);
            }
        }
        return grid;
    }
    public static float feetToMiles(float feet) {
        return (float)(feet/5280.0);
    }
    public static double feetToMiles(double feet) {
        return feet/5280.0;
    }
    public static float[] feetToMiles(float[] array) {
        for(int i=array.length-1; i>=0; i--) {
            array[i] = (float)(array[i]/5280.0);
        }
        return array;
    }
    public static double[] feetToMiles(double[] array) {
        for(int i=array.length-1; i>=0; i--) {
            array[i] = array[i]/5280.0;
        }
        return array;
    }
    public static float[][] feetToMiles(float[][] grid) {
        int d1=grid.length, d2=grid[0].length;
        for(int i=0; i<d1; i++) {
            for(int j=0; j<d2; j++) {
                grid[i][j] = (float)(grid[i][j]/5280.0);
            }
        }
        return grid;
    }  
    public static float feetToMeters(float feet) {
        return (float)(feet/0.3048);
    }
    public static double feetToMeters(double feet) {
        return feet/0.3048;
    }
    public static float[] feetToMeters(float[] array) {
        for(int i=array.length-1; i>=0; i--) {
            array[i] = (float)(array[i]/0.3048);
        }
        return array;
    }
    public static double[] feetToMeters(double[] array) {
        for(int i=array.length-1; i>=0; i--) {
            array[i] = array[i]/0.3048;
        }
        return array;
    }
    public static float[][] feetToMeters(float[][] grid) {
        int d1=grid.length, d2=grid[0].length;
        for(int i=0; i<d1; i++) {
            for(int j=0; j<d2; j++) {
                grid[i][j] = (float)(grid[i][j]/0.3048);
            }
        }
        return grid;
    }  
    public static float feetToKgPerM2(float feet) {
        throw new UnsupportedOperationException("Implement this convertion");
    }
    public static double feetToKgPerM2(double feet) {
        throw new UnsupportedOperationException("Implement this convertion");
    }
    public static float[] feetToKgPerM2(float[] array) {
        throw new UnsupportedOperationException("Implement this convertion");
    }
    public static double[] feetToKgPerM2(double[] array) {
        throw new UnsupportedOperationException("Implement this convertion");
    }
    public static float[][] feetToKgPerM2(float[][] grid) {
        throw new UnsupportedOperationException("Implement this convertion");
    }  
    
    public static float metersToInches(float meter) {
        return (float)(meter * 39.37007874);
    }
    public static double metersToInches(double meter) {
        return meter * 39.37007874;
    }
    public static float[] metersToInches(float[] array) {
        for(int i=array.length-1; i>=0; i--) {
            array[i] = (float)(array[i] * 39.37007874);
        }
        return array;
    }
    public static double[] metersToInches(double[] array) {
        for(int i=array.length-1; i>=0; i--) {
            array[i] = array[i] * 39.37007874;
        }
        return array;
    }
    public static float[][] metersToInches(float[][] grid) {
        int d1=grid.length, d2=grid[0].length;
        for(int i=0; i<d1; i++) {
            for(int j=0; j<d2; j++) {
                grid[i][j] = (float)(grid[i][j] * 39.37007874);
            }
        }
        return grid;
    }
    public static double[][] metersToInches(double[][] grid) {
        int d1=grid.length, d2=grid[0].length;
        for(int i=0; i<d1; i++) {
            for(int j=0; j<d2; j++) {
                grid[i][j] = grid[i][j] * 39.37007874;
            }
        }
        return grid;
    }
    
    public static float metersToFeet(float meter) {
        return (float)(meter * 0.3048);
    }
    public static double metersToFeet(double meter) {
        return meter * 0.3048;
    }
    public static float[] metersToFeet(float[] array) {
        for(int i=array.length-1; i>=0; i--) {
            array[i] = (float)(array[i] * 0.3048);
        }
        return array;
    }
    public static double[] metersToFeet(double[] array) {
        for(int i=array.length-1; i>=0; i--) {
            array[i] = array[i] * 0.3048;
        }
        return array;
    }
    public static float[][] metersToFeet(float[][] grid) {
        int d1=grid.length, d2=grid[0].length;
        for(int i=0; i<d1; i++) {
            for(int j=0; j<d2; j++) {
                grid[i][j] = (float)(grid[i][j] * 0.3048);
            }
        }
        return grid;
    }
    public static double[][] metersToFeet(double[][] grid) {
        int d1=grid.length, d2=grid[0].length;
        for(int i=0; i<d1; i++) {
            for(int j=0; j<d2; j++) {
                grid[i][j] = grid[i][j] * 0.3048;
            }
        }
        return grid;
    }
    
    public static float metersToMiles(float meter) {
        return (float)(meter / 1609.344);
    }
    public static double metersToMiles(double meter) {
        return (meter / 1609.344);
    }
    public static float[] metersToMiles(float[] array) {
        for(int i=array.length-1; i>=0; i--) {
            array[i] = (float)(array[i] / 1609.344);
        }
        return array;
    }
    public static double[] metersToMiles(double[] array) {
        for(int i=array.length-1; i>=0; i--) {
            array[i] = (array[i] / 1609.344);   
        }
        return array;
    }
    public static float[][] metersToMiles(float[][] grid) {
        int d1=grid.length, d2=grid[0].length;
        for(int i=0; i<d1; i++) {
            for(int j=0; j<d2; j++) {
                grid[i][j] = (float)(grid[i][j] / 1609.344);
            }
        }
        return grid;
    }
    public static double[][] metersToMiles(double[][] grid) {
        int d1=grid.length, d2=grid[0].length;
        for(int i=0; i<d1; i++) {
            for(int j=0; j<d2; j++) {
                grid[i][j] = (grid[i][j] / 1609.344);
            }
        }
        return grid;
    }
    
    //// miles to -- /////
    public static float milesToInches(float mile) {
        return (float)(mile*63360);
    }
    public static double milesToInches(double mile) {
        return mile*63360;
    }    
    public static float[] milesToInches(float[] array) {
        for(int i=array.length-1; i>=0; i--) {
            array[i] = (float)(array[i]*63360);
        }
        return array;
    }
    public static double[] milesToInches(double[] array) {
        for(int i=array.length-1; i>=0; i--) {
            array[i] = array[i]*63360;
        }
        return array;
    }    
        public static float[][] milesToInches(float[][] grid) {
        int d1=grid.length, d2=grid[0].length;
        for(int i=0; i<d1; i++) {
            for(int j=0; j<d2; j++) {
                grid[i][j] = (float)(grid[i][j] * 63360);
            }
        }
        return grid;
    }
    public static double[][] milesToInches(double[][] grid) {
        int d1=grid.length, d2=grid[0].length;
        for(int i=0; i<d1; i++) {
            for(int j=0; j<d2; j++) {
                grid[i][j] = (grid[i][j] * 63360);
            }
        }
        return grid;
    }
        public static float milesToFeet(float mile) {
        return (float)(mile*5280);
    }
    public static double milesToFeet(double mile) {
        return mile*5280;
    }    
    public static float[] milesToFeet(float[] array) {
        for(int i=array.length-1; i>=0; i--) {
            array[i] = (float)(array[i]*5280);
        }
        return array;
    }
    public static double[] milesToFeet(double[] array) {
        for(int i=array.length-1; i>=0; i--) {
            array[i] = array[i]*5280;
        }
        return array;
    }    
        public static float[][] milesToFeet(float[][] grid) {
        int d1=grid.length, d2=grid[0].length;
        for(int i=0; i<d1; i++) {
            for(int j=0; j<d2; j++) {
                grid[i][j] = (float)(grid[i][j] * 5280);
            }
        }
        return grid;
    }
    public static double[][] milesToFeet(double[][] grid) {
        int d1=grid.length, d2=grid[0].length;
        for(int i=0; i<d1; i++) {
            for(int j=0; j<d2; j++) {
                grid[i][j] = grid[i][j] * 5280;
            }
        }
        return grid;
    }
    public static float milesToMeters(float mile) {
        return (float)(mile*1609.344);
    }
    public static double milesToMeters(double mile) {
        return mile*1609.344;
    }    
    public static float[] milesToMeters(float[] array) {
        for(int i=array.length-1; i>=0; i--) {
            array[i] = (float)(array[i]*1609.344);
        }
        return array;
    }
    public static double[] milesToMeters(double[] array) {
        for(int i=array.length-1; i>=0; i--) {
            array[i] = array[i]*1609.344;
        }
        return array;
    }    
        public static float[][] milesToMeters(float[][] grid) {
        int d1=grid.length, d2=grid[0].length;
        for(int i=0; i<d1; i++) {
            for(int j=0; j<d2; j++) {
                grid[i][j] = (float)(grid[i][j] * 1609.344);
            }
        }
        return grid;
    }
    public static double[][] milesToMeters(double[][] grid) {
        int d1=grid.length, d2=grid[0].length;
        for(int i=0; i<d1; i++) {
            for(int j=0; j<d2; j++) {
                grid[i][j] = (grid[i][j] * 1609.344);
            }
        }
        return grid;
    }
    
    //// inches to -- /////
    public static float inchesToFeet(float inches) {
        return (float)(inches/12.0);
    }
    public static double inchesToFeet(double inches) {
        return inches/12.0;
    }
    public static float inchesToMeters(float inches) {
        return (float)(inches/39.37);
    }
    public static double inchesToMeters(double inches) {
        return inches/39.37;
    }
    public static float inchesToMiles(float inches) {
        return (float)(inches/63360.0);
    }
    public static double inchesToMiles(double inches) {
        return inches/63360.0;
    }
    public static float inchesToKgPerM2(float inches) {
        return (float)(inches/0.03937);
    }
    public static double inchesToKgPerM2(double inches) {
        return inches/0.03937;
    }
    //// inches to -- /////
    
    //// kg/m^2 to -- ///// 
    public static float kgPerM2ToInches(float kgPerM2) {
        return (float)(kgPerM2 * 0.03937);
    }
    public static double kgPerM2ToInches(double kgPerM2) {
        return kgPerM2 * 0.03937;
    }
    public static float[] kgPerM2ToInches(float[] array) {
        for(int i=array.length-1; i>=0; i--) {
                array[i] *= 0.03937;
        }
        return array;
    }
    public static double[] kgPerM2ToInches(double[] array) {
        for(int i=array.length-1; i>=0; i--) {
            array[i] *= 0.03937;
        }
        return array;
    }
    public static float[][] kgPerM2ToInches(float[][] grid) {
        int d1=grid.length, d2=grid[0].length;
        for(int i=0; i<d1; i++) {
            for(int j=0; j<d2; j++) {
                grid[i][j] *= 0.03937;
            }
        }
        return grid;
    }
    public static double[][] kgPerM2ToInches(double[][] grid) {
        int d1=grid.length, d2=grid[0].length;
        for(int i=0; i<d1; i++) {
            for(int j=0; j<d2; j++) {
                grid[i][j] *= 0.03937;
            }
        }
        return grid;
    }
}
