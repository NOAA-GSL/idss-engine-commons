/*******************************************************************************
 * Copyright (c) 2020 Regents of the University of Colorado. All rights reserved.
 *
 * Contributors:
 *     Geary Layne
 *******************************************************************************/
package gov.noaa.gsl.idssEngine.common.imsMessage;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.UUID;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;
import org.locationtech.jts.geom.Coordinate;
import org.locationtech.jts.geom.Geometry;
import org.locationtech.jts.geom.GeometryFactory;
import org.locationtech.jts.geom.MultiPolygon;
import org.locationtech.jts.geom.Polygon;

import gov.noaa.gsl.idssEngine.common.aspect.Condition;
import gov.noaa.gsl.idssEngine.common.aspect.Field;
import gov.noaa.gsl.idssEngine.common.aspect.Model;
import gov.noaa.gsl.idssEngine.common.aspect.Units;
import gov.noaa.gsl.idssEngine.common.aspect.WxType;

public class ImsEventReader {
    
    public static void main(String[] args) throws IOException, JSONException {
        System.out.println("Start ImsEventReader...");
        
        String fileName = "/input-dir/iris_sample.json";
        ImsEvent[] imsEvents = ImsEventReader.fromJsonFile(fileName);
        for(ImsEvent ie : imsEvents)
            for(ImsThreshold it : ie.thresholdSets[0].thresholds) System.out.println(it);
        
        System.out.println("Finish ImsEventReader");
    }
    
    public static ImsEvent[] fromJsonFile(String fileName) throws IOException, JSONException {
        byte[] encoded = Files.readAllBytes(Paths.get(fileName));
        String jsonString = new String(encoded, StandardCharsets.UTF_8);
        return fromJsonString(jsonString);
    }
    
    public static ImsEvent[] fromJsonString(String jsonString) throws JSONException {
        try {
            JSONObject rootObj = new JSONObject(jsonString);
            return new ImsEvent[] {fromJsonObj(rootObj)};
        } catch(JSONException e) {
//if(true) throw new RuntimeException(e.getMessage());
            JSONArray arrayObj = new JSONArray(jsonString);
            return fromJsonArray(arrayObj);
        }
    }

    public static ImsEvent[] fromJsonArray(JSONArray arrayObj) throws JSONException {
        int len = arrayObj.length();
            ImsEvent[] events = new ImsEvent[len];
            for(int i=0; i<len; i++) {
                events[i] = fromJsonObj(arrayObj.getJSONObject(i));
            } 
            return events;
    }

     public static ImsEvent fromJsonObj(JSONObject rootObj) throws JSONException {
         JSONObject rootObjCpy = new JSONObject(rootObj.toMap());
         
         ImsThresholdSet[] thresholdSets = getThresholdSets(rootObjCpy.getJSONArray("thresholdSets"));
         rootObjCpy.remove("thresholdSets");
         
         ImsLocation location = getLocation(rootObjCpy.getJSONObject("location"));    
         rootObjCpy.remove("location");
         
         long[] validTimes = getValidTimes(rootObjCpy.getJSONObject("timing").getJSONArray("validTimes"));
         rootObjCpy.remove("timing");
         
         return new ImsEvent(rootObjCpy.toMap(), validTimes, thresholdSets, location);
     }

    private static ImsThresholdSet[] getThresholdSets(JSONArray jsonArray) throws JSONException {
        int len = jsonArray.length();
        ImsThresholdSet[] thresholdSets = new ImsThresholdSet[len];
        for(int i=0; i<len; i++) {
            thresholdSets[i] = getThresholdSet(jsonArray.getJSONObject(i));
        }
        return thresholdSets;
    }

    private static ImsThresholdSet getThresholdSet(JSONObject jsonObject) throws JSONException {       
        JSONObject jsonObjCpy = new JSONObject(jsonObject.toMap());
        
        boolean useFcst = jsonObjCpy.getBoolean("useForecast");
        jsonObjCpy.remove("useForecast");

        boolean useObs = jsonObjCpy.getBoolean("useObservations");
        jsonObjCpy.remove("useObservations");

        double duration = jsonObjCpy.getDouble("duration");
        jsonObjCpy.remove("duration");

        double arealPct = jsonObjCpy.getDouble("arealPercentage");
        jsonObjCpy.remove("arealPercentage");

        Set<Model> models = null;
        if(jsonObjCpy.has("models")) {
            JSONArray modelArray = jsonObjCpy.getJSONArray("models");
            jsonObjCpy.remove("models");
            int numModels = modelArray.length();
            models = new HashSet<>();
            for(int i=0; i<numModels; i++) {
                models.add(Model.get(modelArray.getString(i)));
            }
        }
        
        ImsThreshold[] thresholds = getThresholds(jsonObjCpy.getJSONArray("thresholds"));
        jsonObjCpy.remove("thresholds");
        
        return new ImsThresholdSet(useFcst, useObs, duration, arealPct, models, jsonObjCpy.toMap(), thresholds);
    }

    private static ImsThreshold[] getThresholds(JSONArray jsonArray) throws JSONException {
        int len = jsonArray.length();
        ImsThreshold[] thresholds = new ImsThreshold[len];
        for(int i=0; i<len; i++) {
            thresholds[i] = getThreshold(jsonArray.getJSONObject(i));
        }
        return thresholds;
    }

    private static ImsThreshold getThreshold(JSONObject jsonObject) throws JSONException {
        
//              "weatherElement":{
//                  "description":"1 HR SNOWFALL",
//                  "units":"INCHES",
//                  "isProbabilityBased":false
//               },

        JSONObject wxElmtObj = jsonObject.getJSONObject("weatherElement");
        Field element = Field.get(wxElmtObj.getString("description"));
        Units units = Units.get(wxElmtObj.getString("units"));
//        Units units = Field.getUnits(element);
        boolean isProb = wxElmtObj.getBoolean("isProbabilityBased");
        
        Condition condition = Condition.get(jsonObject.getString("condition"));
        double value = jsonObject.getDouble("value");
        double secondaryValue = Double.NaN;
        double prob = Double.NaN;

        if(isProb) prob = jsonObject.getDouble("probability");
        if(condition==Condition.BETWEEN) 
            secondaryValue = jsonObject.getDouble("secondaryValue");
        
        UUID id = null;     
        try {
            id = UUID.fromString(jsonObject.getString("id"));
        } catch (JSONException e) {}

//        WxType wxType = WxType.NONE;
//        try {
//            wxType = WxType.get(jsonObject.getString("wxType"));
//        } catch (JSONException e) {}
//        try {
//            model = Model.get(jsonObject.getString("model"));
//        } catch (JSONException e) {}

        return new ImsThreshold(id, element, units, condition, value, secondaryValue, isProb, prob); //, wxType, model);
    }

//    private static ImsLocation[] getLocations(JSONArray jsonArray) throws JSONException {
//        int len = jsonArray.length();
//        ImsLocation[] locations = new ImsLocation[len];
//        for(int i=0; i<len; i++) locations[i] = getLocation(jsonArray.getJSONObject(i));
//        return locations;
//    }

    private static ImsLocation getLocation(JSONObject jsonObject) throws JSONException {
System.out.println(jsonObject);
        Geometry geometry = getGeometry(jsonObject.getString("geometry"));
//        Geometry bufferedGeometry = getGeometry(jsonObject.getString("bufferedGeometry"));
        Geometry bufferedGeometry = null;
        JSONArray obsArray = null;
        try {
            obsArray = jsonObject.getJSONArray("observationSites");
        } catch(JSONException e) {}
        String[] observationSites = null;
        if(obsArray!=null) observationSites = getObservationSites(obsArray);
        int buffer = jsonObject.getInt("buffer");

        if(bufferedGeometry==null) {
            if(buffer==0) bufferedGeometry = geometry;
            else bufferedGeometry = geometry.buffer(buffer);
        }
         UUID id = UUID.fromString(jsonObject.getString("id"));
         String name = jsonObject.getString("name");

System.out.println("geometry: "+geometry); 
System.out.println("buffer: "+buffer); 
System.out.println("bufferedGeometry: "+bufferedGeometry); 
//if(true) throw new RuntimeException("Trace back");

        return new ImsLocation(id, name, geometry, buffer, bufferedGeometry, observationSites);
    }

    private static Geometry getGeometry(String geometryString) throws JSONException {
        int idx = geometryString.indexOf(' ');
        String type = geometryString.substring(0, idx);
        Coordinate[][] coords = getCoordinates(geometryString.substring(idx+1));
        GeometryFactory gf = new GeometryFactory();
        switch(type) {
//        case "Polygon":
//            return gf.createPolygon(coords[0]);
        case "POINT":
            return gf.createPoint(coords[0][0]);
        case "LINESTRING":
            return gf.createLineString(coords[0]);
        case "POLYGON":
            return gf.createPolygon(coords[0]);
        case "MULTIPOLYGON":
            int len = coords.length;
            Polygon[] polys = new Polygon[len];
            for(int i=0; i<len; i++) polys[i] = gf.createPolygon(coords[i]);
            MultiPolygon mPoly =  gf.createMultiPolygon(polys);
            return mPoly;
        }
        throw new JSONException("Unable to parse geometry");
    }

    private static Coordinate[][] getCoordinates(String coordsString) throws JSONException {
        String[] coordStrs = coordsString.split("[()]");
        List<Coordinate[]> coordlist = new ArrayList<>();
        
        for(String coordStr : coordStrs) {
            if(!coordStr.isEmpty()) {
                coordlist.add(getCoordinate(coordStr));
            }
        }
        return coordlist.toArray(new Coordinate[coordlist.size()][]);    
    }
    
    private static Coordinate[] getCoordinate(String coordsString) {
System.out.println("COORDS: "+coordsString);
        String[] coords = coordsString.split(", ");
        List<Coordinate> coordlist = new ArrayList<Coordinate>();
        for(String coord : coords) {
            String[] lonLat = coord.split(" ");
            double lon = Double.parseDouble(lonLat[0]);
            double lat = Double.parseDouble(lonLat[1]);
            coordlist.add(new Coordinate(lon, lat));
        } 
        return coordlist.toArray(new Coordinate[coordlist.size()]);    
    }

    private static String[] getObservationSites(JSONArray jsonArray) throws JSONException {
        int len = jsonArray.length();
        String[] obsSites = new String[len];
        for(int i=0; i<len; i++) obsSites[i] = jsonArray.getString(i);
        return obsSites;
    }

    private static long[] getValidTimes(JSONArray jsonArray) throws JSONException {
        int len = jsonArray.length();
        long[] validTimes = new long[len];
        for(int i=0; i<len; i++) validTimes[i] = jsonArray.getLong(i);
        
       return validTimes;
    }
}
