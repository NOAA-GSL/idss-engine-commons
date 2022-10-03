/*******************************************************************************
 * Copyright (c) 2020 Regents of the University of Colorado. All rights reserved.
 *
 * Contributors:
 *     Geary Layne
 *******************************************************************************/
package gov.noaa.gsl.idssEngine.commons.aspect;

import java.util.HashMap;
import java.util.Map;

public enum Relational {
    
    // new Condition type must be added to lookup map
    EQUAL,
    GREATERTHAN,
    GREATERTHANOREQUAL,
    LESSTHAN,
    LESSTHANOREQUAL,
    BETWEEN;

    
    public static Relational get(String relationalString) {
        Relational relational = map.get(relationalString);
        if(relational == null)  
            relational = valueOf(relationalString);
         if(relational == null)  
            throw new IllegalArgumentException("Invalid condition string ("+relationalString+")");
        return relational;
    }
    
    // Declaring the static lookup map 
    private static Map<String, Relational> map; 
  
    // Instantiating the static map, must be on entry per IrisCondition type
    static
    { 
        map = new HashMap<>(); 
        map.put("equal", EQUAL); 
        map.put("Equal", EQUAL); 
        map.put("EQ", EQUAL); 
        map.put("equal to", EQUAL); 
        map.put("Equal to", EQUAL); 
        map.put("EQUALTO", EQUAL); 
        map.put("EQUAL TO", EQUAL); 
        map.put("EQ", EQUAL); 
        
        map.put("greaterthan", GREATERTHAN); 
        map.put("Greaterthan", GREATERTHAN); 
//        map.put("GREATERTHAN", GREATERTHAN); 
        map.put("greater than", GREATERTHAN); 
        map.put("Greater than", GREATERTHAN); 
        map.put("Greater Than", GREATERTHAN); 
        map.put("GREATER THAN", GREATERTHAN); 
       map.put("more than", GREATERTHAN); 
        map.put("More Than", GREATERTHAN); 
        map.put("MORE THAN", GREATERTHAN); 
        map.put("GT", GREATERTHAN); 
        
        map.put("greaterthanorequal", GREATERTHANOREQUAL); 
        map.put("Greaterthanorequal", GREATERTHANOREQUAL); 
//        map.put("GREATERTHANOREQUAL", GREATERTHANOREQUAL); 
        map.put("greater than or equal", GREATERTHANOREQUAL); 
        map.put("Greater than or equal", GREATERTHANOREQUAL); 
        map.put("Greater Than Or Equal", GREATERTHANOREQUAL); 
        map.put("GREATER THAN OR EQUAL", GREATERTHANOREQUAL); 
        map.put("greaterthanorequalto", GREATERTHANOREQUAL); 
        map.put("Greaterthanorequalto", GREATERTHANOREQUAL); 
        map.put("GREATERTHANOREQUALTO", GREATERTHANOREQUAL); 
        map.put("greater than or equal to", GREATERTHANOREQUAL); 
        map.put("Greater than or equal to", GREATERTHANOREQUAL); 
        map.put("Greater Than Or Equal To", GREATERTHANOREQUAL); 
        map.put("GREATER THAN OR EQUAL TO", GREATERTHANOREQUAL); 
        map.put("GTE", GREATERTHANOREQUAL); 
        
        map.put("lessthan", LESSTHAN); 
        map.put("Lessthan", LESSTHAN); 
//        map.put("LESSTHAN", LESSTHAN); 
        map.put("less than", LESSTHAN); 
        map.put("Less than", LESSTHAN); 
        map.put("Less Than", LESSTHAN); 
        map.put("LESS THAN", LESSTHAN); 
        map.put("LT", LESSTHAN); 
        
        map.put("lessthanorequal", LESSTHANOREQUAL); 
        map.put("Lessthanorequal", LESSTHANOREQUAL); 
//        map.put("LESSTHANOREQUAL", LESSTHANOREQUAL); 
        map.put("less than or equal", LESSTHANOREQUAL); 
        map.put("Less Than Or Equal", LESSTHANOREQUAL); 
        map.put("LESS THAN OR EQUAL", LESSTHANOREQUAL); 
        map.put("lessthanorequalto", LESSTHANOREQUAL); 
        map.put("Lessthanorequalto", LESSTHANOREQUAL); 
        map.put("LESSTHANOREQUALTO", LESSTHANOREQUAL); 
        map.put("less than or equal to", LESSTHANOREQUAL); 
        map.put("Less Than Or Equal To", LESSTHANOREQUAL); 
        map.put("LESS THAN OR EQUAL TO", LESSTHANOREQUAL); 
        map.put("LTE", LESSTHANOREQUAL); 
        
        map.put("between", BETWEEN); 
        map.put("Between", BETWEEN); 
//        map.put("BETWEEN", BETWEEN); 
        map.put("BT", BETWEEN); 
    }

    public String toShortString() {
        return toShortString(this);
    } 
    
    public static String toShortString(Relational relational) {
        switch(relational) {
        case EQUAL: return "EQ";
        case GREATERTHAN: return "GT";
        case GREATERTHANOREQUAL: return "GTE";
        case LESSTHAN: return "LT";
        case LESSTHANOREQUAL: return "LTE";
        case BETWEEN: return "BT";
        }
        return null;
    } 

}

