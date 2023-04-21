/*********************************************************************************
  * Copyright (c) 2021 Regents of the University of Colorado. All rights reserved.
 *
 * Contributors:
 *     Geary Layne
*********************************************************************************/
package gov.noaa.gsl.idssEngine.commons;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.concurrent.TimeoutException;

import org.json.JSONObject;

import com.rabbitmq.client.Connection;

public class Logger {

    public enum Level {
        DEBUG, INFO, WARN, ERROR, STATUS; //must be ordered from least to most
        
        public boolean notBelow(Level level) {
            if(level == null) return true;
            return this.compareTo(level) >= 0;
        }
    };

    private final Rabbitmq statusRp;
    private final String service;
    private final Level level;
    private Sid sid = Sid.Empty;
    
    public Logger(String service) {
        this(service, (Level)null, null, null);
    }
    
    public Logger(String service, Level level) {
        this(service, level, null, null);
    }

    public Logger(String service, Level level, Connection connection) {
        this(service, level, connection, null);
    }
    
    public Logger(String service, JSONObject configObj) {
        this(service, (Level)null, null, configObj);
    }

    public Logger(String service, Connection connection, JSONObject configObj) {
        this(service, (Level)null, connection, configObj);
    }

    public Logger(String service, Level level, JSONObject configObj) {
        this(service, level, null, configObj);
    }
    
    public Logger(String service, String level, Connection connection, JSONObject configObj) {        
        this(service, Level.valueOf(level), connection, configObj);
    }
    
    public Logger(String service, Level level, Connection connection, JSONObject configObj) {        
        if(level == null) {
            if(configObj == null) {
                level = Level.ERROR;
            } else {
                try {
                    if(configObj.has("logLevel")) level = Level.valueOf(configObj.getString("logLevel")); 
                } catch(Exception e) {
                    warn("Failed to read log level json config file, using default level: "+Level.ERROR);
                    level = Level.ERROR;
                }
            }
        }
                 
        this.service = service;
        if(level.equals(Level.STATUS)) {
            warn("Highest level allowed is ERROR, using ERROR instead of "+level);
            level = Level.ERROR;
        }
        this.level = level;
        
        if(configObj == null) {
            this.statusRp = null;
            warn("No config file was provided, thus STATUS messages will not to sent via RabbitMQ");
        } else {
            try {
                this.statusRp = new Rabbitmq(connection, "status", configObj);
            } catch(Exception e) {
                throw new IllegalArgumentException(e);
            }
        }
    }
    
    public Sid setSid(Sid sid) {
        Sid old_sid = this.sid;
        this.sid = sid;
        return old_sid;
    }
    public Sid clearSid() {
        return setSid(Sid.Empty);
    }
        
    public void debug(String message) {
        debug(sid, service, message);
    }
    public void debug(Sid sid, String message) {
        debug(sid, service, message);
    }
    public void debug(String service, String message) {
        debug(sid, service, message);
    }
    public void debug(Sid sid, String service, String message) {
        if(level.equals(Level.DEBUG)) {
            System.out.println(Level.DEBUG+": "+formatMessage(sid, service, message));
        }
    }
    
    public void info(String message) {
        info(sid, service, message);
    }    
    public void info(Sid sid, String message) {
        info(sid, service, message);
    }
    public void info(String service, String message) {
        info(sid, service, message);
    }
    public void info(Sid sid, String service, String message) {
        if(Level.INFO.notBelow(level)) {
            System.out.println(Level.INFO+": "+formatMessage(sid, service, message));
        }
    }

    public void warn(String message) {
        warn(sid, service, message);
    }
    public void warn(Sid sid, String message) {
        warn(sid, service, message);
    }
    public void warn(String service, String message) {
        warn(sid, service, message);
    }
    public void warn(Sid sid, String service, String message) {
        if(Level.WARN.notBelow(level)) {
            System.out.println(Level.WARN+": "+formatMessage(sid, service, message));
        }
    }
    
    public void error(String message) {
        error(sid, service, message, null, true);
    }
    public void error(Sid sid, String message) {
        error(sid, service, message, null, true);
    }
    public void error(String service, String message) {
        error(sid, service, message, null, true);
    }
    public void error(Sid sid, String service, String message) {
        error(sid, service, message, null, true);
    }
    public void error(String message, Exception e) {
        error(sid, service, message, e, true);
    }
    public void error(Sid sid, String message, Exception e) {
        error(sid, service, message, e, true);
    }
    public void error(String service, String message, Exception e) {
        error(sid, service, message, e, true);
    }
    public void error(Sid sid, String service, String message, Exception e) {
        error(sid, service, message, e, true);
    }
    public void error(String message, Exception e, boolean sendToQueue) {
        error(sid, service, message, e, sendToQueue);
    }
    public void error(Sid sid, String message, Exception e, boolean sendToQueue) {
        error(sid, service, message, e, sendToQueue);
    }
    public void error(Sid sid, String service, String message, Exception exception, boolean sendToQueue) {
        String formatStr = formatMessage(sid, service, message);
        if(exception != null) {
            final StringBuilder builder = new StringBuilder(formatStr);
            builder.append("\n\t"+exception.toString());
            for(StackTraceElement ste : exception.getStackTrace()) {
                builder.append("\n\t\t");
                builder.append(ste.toString());
            }
            formatStr = builder.toString();
        }
        System.err.println(Level.ERROR+": "+formatStr);
    }
    
    public void status(int numComplete, int totalSteps) {
        status(sid, service, numComplete, totalSteps);
    }
    public void status(Sid sid, int numComplete, int totalSteps) {
        status(sid, service, numComplete, totalSteps);
    }
    public void status(String service, int numComplete, int totalSteps) {
        status(sid, service, numComplete, totalSteps);
    }
    public void status(Sid sid, String service, int numComplete, int totalSteps) {
        String formatStr = formatMessage(sid, service, numComplete, totalSteps);
        System.out.println(Level.STATUS+": "+formatStr);
        if(statusRp!=null) { 
            try {
                statusRp.basicPublish(Level.STATUS.toString(), null,  formatStr.getBytes(StandardCharsets.UTF_8));
                debug("Status set to rabbitMQ: ");
            } catch(IOException e) {
                error(sid, service, "Unable to publish status to queue", e, false);
            }   
        }
    }
    
    private String formatMessage(Sid sid, String service, int numComplete, int totalSteps) {
        return String.format("%s:%s:%02d:%02d:%s; %d/%d", 
                                                 sid.key, sid.originator, sid.issueDt.getHourOfDay(), sid.issueDt.getMinuteOfHour(), service, numComplete, totalSteps);
    }
    private String formatMessage(Sid sid, String service, String message) {
        return String.format("%s:%s:%02d:%02d:%s; %s", 
                                                 sid.key, sid.originator, sid.issueDt.getHourOfDay(), sid.issueDt.getMinuteOfHour(), service, message);
    }

}
