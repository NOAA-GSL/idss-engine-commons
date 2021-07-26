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
        Relational ie = map.get(relationalString);
        if(ie == null)  
            throw new IllegalArgumentException("Invalid condition string ("+relationalString+")");
        return ie;
    }
    
    // Declaring the static lookup map 
    private static Map<String, Relational> map; 
  
    // Instantiating the static map, must be on entry per IrisCondition type
    static
    { 
        map = new HashMap<>(); 
        map.put("equal", EQUAL); 
        map.put("Equal", EQUAL); 
        map.put("EQUAL", EQUAL); 
        
        map.put("greaterthan", GREATERTHAN); 
        map.put("Greaterthan", GREATERTHAN); 
        map.put("GREATERTHAN", GREATERTHAN); 
        map.put("greater than", GREATERTHAN); 
        map.put("Greater Than", GREATERTHAN); 
        map.put("GREATER THAN", GREATERTHAN); 
        
        map.put("greaterthanorequal", GREATERTHANOREQUAL); 
        map.put("Greaterthanorequal", GREATERTHANOREQUAL); 
        map.put("GREATERTHANOREQUAL", GREATERTHANOREQUAL); 
        map.put("greater than or equal", GREATERTHANOREQUAL); 
        map.put("Greater Than Or Equal", GREATERTHANOREQUAL); 
        map.put("GREATER THAN OR EQUAL", GREATERTHANOREQUAL); 
        map.put("greaterthanorequalto", GREATERTHANOREQUAL); 
        map.put("Greaterthanorequalto", GREATERTHANOREQUAL); 
        map.put("GREATERTHANOREQUALTO", GREATERTHANOREQUAL); 
        map.put("greater than or equal to", GREATERTHANOREQUAL); 
        map.put("Greater Than Or Equal To", GREATERTHANOREQUAL); 
        map.put("GREATER THAN OR EQUAL TO", GREATERTHANOREQUAL); 
        
        map.put("lessthan", LESSTHAN); 
        map.put("Lessthan", LESSTHAN); 
        map.put("LESSTHAN", LESSTHAN); 
        map.put("less than", LESSTHAN); 
        map.put("Less Than", LESSTHAN); 
        map.put("LESS THAN", LESSTHAN); 
        
        map.put("lessthanorequal", LESSTHANOREQUAL); 
        map.put("Lessthanorequal", LESSTHANOREQUAL); 
        map.put("LESSTHANOREQUAL", LESSTHANOREQUAL); 
        map.put("less than or equal", LESSTHANOREQUAL); 
        map.put("Less Than Or Equal", LESSTHANOREQUAL); 
        map.put("LESS THAN OR EQUAL", LESSTHANOREQUAL); 
        map.put("lessthanorequalto", LESSTHANOREQUAL); 
        map.put("Lessthanorequalto", LESSTHANOREQUAL); 
        map.put("LESSTHANOREQUALTO", LESSTHANOREQUAL); 
        map.put("less than or equal to", LESSTHANOREQUAL); 
        map.put("Less Than Or Equal To", LESSTHANOREQUAL); 
        map.put("LESS THAN OR EQUAL TO", LESSTHANOREQUAL); 
        
        map.put("between", BETWEEN); 
        map.put("Between", BETWEEN); 
        map.put("BETWEEN", BETWEEN); 
    }

    public String toShortString() {
        switch(this) {
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

