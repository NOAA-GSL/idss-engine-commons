/*******************************************************************************
 * Copyright (c) 2020 Regents of the University of Colorado. All rights reserved.
 *
 * Contributors:
 *     Geary Layne
 *******************************************************************************/
package gov.noaa.gsl.idssEngine.commons;

import gov.noaa.gsl.idssEngine.commons.aspect.Units;

public class UnitsConvertion {
    
    private static final  double nineFifth = 9.0/5.0;
    private static final double fiveNinth = 5.0/9.0;

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
        case Pascals:
            return convertPascals(destUnits, value);
        default:
        }
        throw new UnsupportedOperationException("Units covertion for ("+srcUnits+") not currently supported");
    }
    
    public static float[][] convert(Units srcUnits, Units destUnits, float[][] grid) {
        if(srcUnits == destUnits) return grid;
        switch(srcUnits) {
        case Inches:
            return convertInches(destUnits, grid);                        
//        case Feet:
//            return convertFeet(destUnits, grid);            
//        case Miles:
//            return convertMiles(destUnits, grid);
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
//        case Feet:
//            return convertFeet(destUnits, grid);            
//        case Miles:
//            return convertMiles(destUnits, grid);
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
         case Pascals:
            return convertPascals(destUnits, grid);
       default:
        }
        throw new UnsupportedOperationException("Units covertion for ("+srcUnits+") not currently supported");
    }
    
    ////////////////////////////////////// convert Inches ///////////////////////////////////////////////
    private static float convertInches(Units destUnits, float value) {
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
    private static double convertInches(Units destUnits, double value) {
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

    private static float[][] convertInches(Units destUnits, float[][] grid) {
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
    private static double[][] convertInches(Units destUnits, double[][] grid) {
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
    
    private static float convertFeet(Units destUnits, float value) {
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
    private static double convertFeet(Units destUnits, double value) {
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
    
    ////////////////////////////////////// convert Feet //////////////////////////////////////////////////
    ////////////////////////////////////// convert Meters ///////////////////////////////////////////////
    
    private static float convertMeters(Units destUnits, float value) {
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
    private static double convertMeters(Units destUnits, double value) {
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

    private static float[][] convertMeters(Units destUnits, float[][] grid) {
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
    private static double[][] convertMeters(Units destUnits, double[][] grid) {
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

    
    private static float convertMiles(Units destUnits, float value) {
        throw new UnsupportedOperationException("Implement this convertion");
    }
    private static double convertMiles(Units destUnits, double value) {
        throw new UnsupportedOperationException("Implement this convertion");
    }

    ////////////////////////////////////// convert Miles /////////////////////////////////////////////////
    ////////////////////////////////////// convert KgPerM2 ////////////////////////////////////////////

    private static float convertKgPerM2(Units destUnits, float value) {
        switch(destUnits) {
        case Inches:
            return kgPerM2ToInches(value);                          
        case KgPerM2:
            return value;
        default:
        }
        throw new UnsupportedOperationException("Units covertion from kgPerM2 to ("+destUnits+") not currently supported");

    }
    private static double convertKgPerM2(Units destUnits, double value) {
        throw new UnsupportedOperationException("Implement this convertion");
    }

    private static float[][] convertKgPerM2(Units destUnits, float[][] grid) {
        switch(destUnits) {
        case Inches:
            return kgPerM2ToInches(grid);                          
        case KgPerM2:
            return grid;
        default:
        }
        throw new UnsupportedOperationException("Units covertion from kgPerM2 to ("+destUnits+") not currently supported");

    }
    private static double[][] convertKgPerM2(Units destUnits, double[][] grid) {
        throw new UnsupportedOperationException("Implement this convertion");
    }    

    ////////////////////////////////////// convert KgPerM2 ////////////////////////////////////////////
    ////////////////////////////////////// convert Fahrenheit ///////////////////////////////////////////

    private static float convertFahrenheit(Units destUnits, float value) {
        switch(destUnits) {
        case Kelvin:
            return fahrenheitToKelvin(value);                        
        default:
        }
        throw new UnsupportedOperationException("Implement this convertion for ("+destUnits+")");
    }
    
    private static double convertFahrenheit(Units destUnits, double value) {
        switch(destUnits) {
        case Kelvin:
            return fahrenheitToKelvin(value);                        
        default:
        }
        throw new UnsupportedOperationException("Implement this convertion for ("+destUnits+")");
    }

    private static float[][] convertFahrenheit(Units destUnits, float[][] grid) {
        switch(destUnits) {
        case Kelvin:
            return fahrenheitToKelvin(grid);                        
        default:
        }
        throw new UnsupportedOperationException("Implement this convertion for ("+destUnits+")");
    }
    private static double[][] convertFahrenheit(Units destUnits, double[][] grid) {
        switch(destUnits) {
        case Kelvin:
            return fahrenheitToKelvin(grid);                        
        default:
        }
        throw new UnsupportedOperationException("Implement this convertion for ("+destUnits+")");
    }
    
    ////////////////////////////////////// convert Fahrenheit //////////////////////////////////////////
    ////////////////////////////////////// convert Kelvin ////////////////////////////////////////////////

    private static float convertKelvin(Units destUnits, float value) {
        switch(destUnits) {
        case Fahrenheit:
            return kelvinToFahrenheit(value);                        
        case Celcius:
            return kelvinToCelcius(value);                        
        default:
        }
        throw new UnsupportedOperationException("Implement this convertion for ("+destUnits+")");
    }
    
    private static double convertKelvin(Units destUnits, double value) {
        switch(destUnits) {
        case Fahrenheit:
            return kelvinToFahrenheit(value);                        
        case Celcius:
            return kelvinToCelcius(value);                        
        default:
        }
        throw new UnsupportedOperationException("Implement this convertion for ("+destUnits+")");
    }

    private static float[][] convertKelvin(Units destUnits, float[][] grid) {
        switch(destUnits) {
        case Fahrenheit:
            return kelvinToFahrenheit(grid);                        
        case Celcius:
            return kelvinToCelcius(grid);                        
        default:
        }
        throw new UnsupportedOperationException("Implement this convertion for ("+destUnits+")");
    }
    private static double[][] convertKelvin(Units destUnits, double[][] grid) {
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

    private static float convertCelcius(Units destUnits, float value) {
        switch(destUnits) {
        case Fahrenheit:
            return celciusToFahrenheit(value);                            
        default:
        }
        throw new UnsupportedOperationException("Implement this convertion for ("+destUnits+")");
    }
    
    private static double convertCelcius(Units destUnits, double value) {
        switch(destUnits) {
        case Fahrenheit:
            return celciusToFahrenheit(value);                     
        default:
        }
        throw new UnsupportedOperationException("Implement this convertion for ("+destUnits+")");
    }

    private static float[][] convertCelcius(Units destUnits, float[][] grid) {
        switch(destUnits) {
        case Fahrenheit:
            return celciusToFahrenheit(grid);                        
        default:
        }
        throw new UnsupportedOperationException("Implement this convertion for ("+destUnits+")");
    }
    private static double[][] convertCelcius(Units destUnits, double[][] grid) {
        switch(destUnits) {
        case Fahrenheit:
            return celciusToFahrenheit(grid);                                             
        default:
        }
        throw new UnsupportedOperationException("Implement this convertion for ("+destUnits+")");
    }
    
    ////////////////////////////////////// convert Celcius //////////////////////////////////////////////
    ////////////////////////////////////// convert Pascals ////////////////////////////////////////////// 

    private static float convertPascals(Units destUnits, float value) {
        switch(destUnits) {
        case MilliBars:
            return pascalsToMilliBars(value);        
        case InchesOfMercury:
            return pascalsToInchesOfMercury(value);
        default:
        }
        throw new UnsupportedOperationException("Implement this convertion for ("+destUnits+")");
    }
    
    private static double convertPascals(Units destUnits, double value) {
        switch(destUnits) {
        case MilliBars:
            return pascalsToMilliBars(value);                        
        case InchesOfMercury:
            return pascalsToInchesOfMercury(value);
        default:
        }
        throw new UnsupportedOperationException("Implement this convertion for ("+destUnits+")");
    }

    private static float[][] convertPascals(Units destUnits, float[][] grid) {
        switch(destUnits) {
        case MilliBars:
            return pascalsToMilliBars(grid);                        
        case InchesOfMercury:
            return pascalsToInchesOfMercury(grid);
        default:
        }
        throw new UnsupportedOperationException("Implement this convertion for ("+destUnits+")");
    }
    private static double[][] convertPascals(Units destUnits, double[][] grid) {
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

    private static float convertMetersPerSecond(Units destUnits, float value) {
        switch(destUnits) {
        case MilesPerHour:
            return metersPerSecToMilesPerHour(value);                        
        case MetersPerHour:
            return metersPerSecToMetersPerHour(value);                        
        default:
        }
        throw new UnsupportedOperationException("Implement this convertion for ("+destUnits+")");
    }
    
    private static double convertMetersPerSecond(Units destUnits, double value) {
        switch(destUnits) {
        case MilesPerHour:
            return metersPerSecToMilesPerHour(value);                        
        case MetersPerHour:
            return metersPerSecToMetersPerHour(value);                        
        default:
        }
        throw new UnsupportedOperationException("Implement this convertion for ("+destUnits+")");
    }

    private static float[][] convertMetersPerSecond(Units destUnits, float[][] grid) {
        switch(destUnits) {
        case MilesPerHour:
            return metersPerSecToMilesPerHour(grid);                        
        case MetersPerHour:
            return metersPerSecToMetersPerHour(grid);                        
        default:
        }
        throw new UnsupportedOperationException("Implement this convertion for ("+destUnits+")");
    }
    private static double[][] convertMetersPerSecond(Units destUnits, double[][] grid) {
        switch(destUnits) {
        case MilesPerHour:
            return metersPerSecToMilesPerHour(grid);                        
        case MetersPerHour:
            return metersPerSecToMetersPerHour(grid);                        
        default:
        }
        throw new UnsupportedOperationException("Implement this convertion for ("+destUnits+")");
    }
    
    ////////////////////////////////////// convert MetersPerSecond /////////////////////////////////    
    ////////////////////////////////////// convert Fahrenheit ///////////////////////////////////////////

    public static float fahrenheitToKelvin(float value) {
        return (float)((value - 32) * fiveNinth + 273.15);
    }
    public static double fahrenheitToKelvin(double value) {
        return (value - 32) * fiveNinth + 273.15;
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
    ////////////////////////////////////// convert MetersPerSec ///////////////////////////////////////
    ////////////////////////////////////// convert Feet ///////////////////////////////////////////////////

    public static float feetToInches(float feet) {
        return (float)(feet*12.0);
    }
    public static double feetToInches(double feet) {
        return feet*12.0;
    }
    public static float feetToMiles(float feet) {
        return (float)(feet/5280.0);
    }
    public static double feetToMiles(double feet) {
        return feet/5280.0;
    }
    public static float feetToMeters(float feet) {
        return (float)(feet/0.3048);
    }
    public static double feetToMeters(double feet) {
        return feet/0.3048;
    }
    public static float feetToKgPerM2(float feet) {
        throw new UnsupportedOperationException("Implement this convertion");
    }
    public static double feetToKgPerM2(double feet) {
        throw new UnsupportedOperationException("Implement this convertion");
    }
    
    public static float metersToInches(float meter) {
        return (float)(meter * 39.37007874);
    }
    public static double metersToInches(double meter) {
        return meter * 39.37007874;
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
    
    public static float milesToMeters(float mile) {
        return (float)(mile*1609.344);
    }
    public static double milesToMeters(double mile) {
        return mile*1609.344;
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
