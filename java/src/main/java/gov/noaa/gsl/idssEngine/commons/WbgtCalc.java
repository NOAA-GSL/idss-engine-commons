/*******************************************************************************
 * Copyright (c) 2020 Regents of the University of Colorado. All rights reserved.
 *
 * Contributors:
 *     Geary Layne
 *******************************************************************************/
package gov.noaa.gsl.idssEngine.commons;

import org.joda.time.DateTime;
import org.joda.time.Days;

import gov.noaa.gsd.fiqas.cartography.Projection;
import gov.noaa.gsd.fiqas.util.time.DateTimeFactory;

public class WbgtCalc {
    public static void main(String[] args) {
        System.out.println("Start WbgtCalc....");
        DateTime dt = DateTimeFactory.newInstance("2010/9/9 10");
        double lat = 36;
        double lon = -95;

        WbgtCalc wbgtCalc = new WbgtCalc(dt);
        double zenith = wbgtCalc.computeZenith(lat, lon);
        System.out.println("zenith (deg): "+Math.toDegrees(zenith));
        System.out.println("Finish WbgtCalc");
    }
    
    private final double hourOfDay, eqOfTimeMin, sunDeclinDeg;
    private final DateTime jan12000 = DateTimeFactory.newInstance("2000/1/1");

    public WbgtCalc(DateTime dt) {
        hourOfDay = dt.getMinuteOfDay()/1440.0;

        //double julianDay =  Days.daysBetween(jan12000, dt).getDays() + 2451545.5 - B5/24.0;
        final double julianDay =  Days.daysBetween(jan12000, dt).getDays() + 2451544.5 + hourOfDay;
        
        final double julianCentury = (julianDay-2451545.0)/36525.0;
        
        final double geomMeanLongSunDeg = (280.46646+julianCentury*(36000.76983 + julianCentury*0.0003032)) % 360;
        
        final double geomMeanAnomSunDeg = 357.52911+julianCentury*(35999.05029 - 0.0001537*julianCentury);
        
        final double eccentEarthOrbit = 0.016708634-julianCentury*(0.000042037+0.0000001267*julianCentury);
        
        final double meanObliqEclipticDeg = 23+(26+((21.448-julianCentury*(46.815+julianCentury*(0.00059-julianCentury*0.001813))))/60)/60;
        
        final double obliqCorrRad =Math.toRadians(meanObliqEclipticDeg+0.00256*Math.cos(Math.toRadians(125.04-1934.136*julianCentury)));
        
        final double varY =Math.tan(obliqCorrRad/2.0)*Math.tan(obliqCorrRad/2.0);
        
        eqOfTimeMin = 4.0*Math.toDegrees(varY*Math.sin(2.0*Math.toRadians(geomMeanLongSunDeg))-2.0*eccentEarthOrbit*Math.sin(Math.toRadians(geomMeanAnomSunDeg))+4*eccentEarthOrbit*varY*Math.sin(Math.toRadians(geomMeanAnomSunDeg))*Math.cos(2*Math.toRadians(geomMeanLongSunDeg))-0.5*varY*varY*Math.sin(4*Math.toRadians(geomMeanLongSunDeg))-1.25*eccentEarthOrbit*eccentEarthOrbit*Math.sin(2*Math.toRadians(geomMeanAnomSunDeg)));
        
        final double sunEqOfCtr =Math.sin(Math.toRadians(geomMeanAnomSunDeg))*(1.914602-julianCentury*(0.004817+0.000014*julianCentury))+Math.sin(Math.toRadians(2*geomMeanAnomSunDeg))*(0.019993-0.000101*julianCentury)+Math.sin(Math.toRadians(3*geomMeanAnomSunDeg))*0.000289;
        
        final double sunTrueLongDeg = geomMeanLongSunDeg+sunEqOfCtr;
        
        final double sunAppDeg = sunTrueLongDeg-0.00569-0.00478*Math.sin(Math.toRadians(125.04-1934.136*julianCentury));
        
        sunDeclinDeg = Math.asin(Math.sin(obliqCorrRad)*Math.sin(Math.toRadians(sunAppDeg)));
    }
    
    public double computeZenith(double lat, double lon) {
        //double AB2 = (E2*1440+V2+4*B4-60*B5) % 1440; // B5 is GMT offset
        final double trueSolarTimeMin = (hourOfDay*1440+eqOfTimeMin+4*lon) % 1440;
        
        final double hourAngleRad = Math.toRadians(trueSolarTimeMin/4.0<0 ? trueSolarTimeMin/4.0+180.0 : trueSolarTimeMin/4.0-180.0);
        
        final double latRad = Math.toRadians(lat);
        double zenith=(Math.acos(Math.sin(latRad)*Math.sin(sunDeclinDeg)+Math.cos(latRad)*Math.cos(sunDeclinDeg)*Math.cos(hourAngleRad)));
    
        return zenith;
    }
    
    public float[][] getWbgt(Projection proj, float[][] tGrid, float[][] rhGrid, float[][] dpGrid, float[][] wsGrid, float[][] pGrid, float[][] siGrid, float[][] dbrGrid, float[][] drGrid) {
        int d1 = proj.getIntendedWidth();
        int d2 = proj.getIntendedHeight();
        float[][] wbgtGrid = new float[d1][d2];
        for(int i=0; i<d1; i++) {
            for(int j=0; j<d2; j++) {
                final double[] latlon = proj.mapXY(i, j);
                wbgtGrid[i][j] = (float)getWbgt(tGrid[i][j], rhGrid[i][j], dpGrid[i][j], wsGrid[i][j], pGrid[i][j], siGrid[i][j], dbrGrid[i][j], drGrid[i][j], computeZenith(latlon[0], latlon[1]));
            }
        }
        return wbgtGrid;
    }

    //ambient temp, relative humidity, dew point temp, wind speed (meters/hour), barometric pressure, zenith angle, solar irradiance, direct beam radiation from the sun, diffuse radiation from the sun
    public static double getWbgt(double t, double rh, double dp, double ws, double p, double si, double dbr, double dr, double z) {
        
        final double sumRadiation = dbr+dr;
        dbr /= sumRadiation;
        dr /= sumRadiation;
 
        // atmospheric vaper pressure
        final double avp = Math.exp((17.67*(dp-t))/(dp+243.5)) * (1.0007 + 0.00000346 * p) * 6.112 * Math.exp((17.502*t)/(240.97+t));
        
        final double emissivity = 0.575*Math.pow(avp, 1./7.);

        final double C = (0.315 * Math.pow(ws, 0.58)) / (0.000000053865);
        
        final double sigma = 0.0000000567;
        final double B = si * (dbr / (4.0*sigma*Math.cos(z)) + (1.2* dr)/(sigma)) + emissivity*Math.pow(t, 4);
            
        // wet bulb temp
        double Tw = t * Math.atan(0.151977 * Math.pow(rh + 8.313659, 0.5)) + Math.atan(t + rh) -
                                    Math.atan(rh - 1.676331) + 0.00391838 * Math.pow(rh, 1.5) * Math.atan(0.023101 * rh) - 4.686035;

        final double Tg = (B+C*t+7680000) / (C+256000);
        
        double ans = 0.7 * Tw + 0.2 * Tg + 0.1 * t;
        
        return ans;
    }
}
