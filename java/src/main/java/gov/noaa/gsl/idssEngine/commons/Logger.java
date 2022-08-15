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

import com.rabbitmq.client.Channel;
import com.rabbitmq.client.Connection;
import com.rabbitmq.client.ConnectionFactory;

public class Logger {

    public enum Level {
        DEBUG, INFO, WARN, ERROR; //must be ordered from least to most
        
        public boolean below(Level level) {
            return this.compareTo(level) > 0;
        }
    };

    private final Connection connection;
    private final Channel channel;
    private final String exchName;
    private final String service;
    private final Level level;
    private Sid sid = Sid.Empty
    private boolean closed = true;
    
    public Logger(Connection connection, Channel channel, String exchName, String service, Level level) {
        this.connection = connection;
        this.channel = channel;
        this.exchName = exchName;
        this.service = service;
        this.level = level;
        if(connection!=null) closed = false;
    }
    
    public Logger(Connection connection, String exchName, String exchType, String service, Level level) throws ExceptionInInitializerError {
        this(connection, initRabbitMqChannel(connection, exchName, exchType), exchName, service, level);
    }
    
    public Logger(String rabMqVhost, String rabMqHost, int rabMqPortNum, String rabMqUser, String rabMqPwd, 
                                  String exchName, String exchType, String service, Level level) throws ExceptionInInitializerError {
        this.connection = initRabbitMqConnection(rabMqVhost, rabMqHost, rabMqPortNum, rabMqUser, rabMqPwd);
        this.channel = initRabbitMqChannel(connection, exchName, exchType);
        this.exchName = exchName;
        this.service = service;
        this.level = level;
        if(connection!=null) closed = false;
        
        if(level.equals(Level.DEBUG)) {
            debug("user: "+rabMqUser);
            debug("pass: "+rabMqPwd);
            debug("vHost: "+rabMqVhost);
            debug("host: "+rabMqHost);
            debug("portNum: "+rabMqPortNum);
        }
    }
    
    public Logger(JSONObject configObj, String service) {
        String exchName = null;
        String exchType = null;
        String rabMqUser = null;
        String rabMqPwd = null;
        String rabMqVhost = null;
        String rabMqHost = null;
        int rabMqPortNum = 0;
        Level level = null;
        
         JSONObject mqObj = null;
         try {
             mqObj = configObj.getJSONObject("rabbitMQ"); 
         } catch(Exception e) {
             error(service, "Config file must specify a rabbitMQ object", e);
         }
         
         try {
             rabMqUser = mqObj.getString("userName"); 
         } catch(Exception e) {
             error(service, "Config file must specify userName", e);
         }
         
         try {
            rabMqPwd = mqObj.getString("password"); 
         } catch(Exception e) {
             error(service, "Config file must specify password", e);
         }
         
         try {
            rabMqVhost = mqObj.getString("virtualHost"); 
         } catch(Exception e) {
             error(service, "Config file must specify virtualHost", e);
         }
         
         try {
             rabMqHost = mqObj.getString("hostName"); 
         } catch(Exception e) {
             error(service, "Config file must specify hostName", e);
         }
         
         try {
             rabMqPortNum = mqObj.getInt("portNumber"); 
         } catch(Exception e) {
             error(service, "Config file must specify portNumber", e);
         }

         try {
             exchName = mqObj.getString("logExchangeName"); 
         } catch(Exception e) {
             error(service, "Config file must specify logExchangeName", e);
         }
       
        try {
             exchType = mqObj.getString("logExchangeType"); 
         } catch(Exception e) {
             error(service, "Config file must specify logExchangeType", e);
         }
        
        try {
             level = Level.valueOf(mqObj.getString("logLevel")); 
         } catch(Exception e) {
             level = Level.INFO;
         }
        
        this.connection = initRabbitMqConnection(rabMqVhost, rabMqHost, rabMqPortNum, rabMqUser, rabMqPwd);
        this.channel = initRabbitMqChannel(connection, exchName, exchType);
        this.exchName = exchName;
        this.service = service;
        this.level = level;
        if(connection!=null) closed = false;
        
        if(level.equals(Level.DEBUG)) {
            debug("user: "+rabMqUser);
            debug("pass: "+rabMqPwd);
            debug("vHost: "+rabMqVhost);
            debug("host: "+rabMqHost);
            debug("portNum: "+rabMqPortNum);
        }
    }
    
    public static Channel initRabbitMqChannel(Connection connection, String exchName, String exchType) throws ExceptionInInitializerError {
        Channel channel = null;
        try {
            channel = connection.createChannel();
            channel.exchangeDeclare(exchName, exchType);
        } catch(IOException e) {
            throw new ExceptionInInitializerError("Unable to connect Logger to queue");
        } 
        return channel;
    }
    
    public static Connection initRabbitMqConnection(String rabMqVhost, String rabMqHost, int rabMqPortNum,
                                                                                                          String rabMqUser, String rabMqPwd)  throws ExceptionInInitializerError{

        ConnectionFactory factory = new ConnectionFactory();
        factory.setUsername(rabMqUser);
        factory.setPassword(rabMqPwd);
        factory.setVirtualHost(rabMqVhost);
        factory.setHost(rabMqHost);
        factory.setPort(rabMqPortNum);
        
        Connection connection = null;
        try {
            connection = factory.newConnection();
        } catch( IOException | TimeoutException e ) {
            throw new ExceptionInInitializerError("Unable to connect Logger to queue, with: "+
                                                                                     rabMqUser+", "+
                                                                                     rabMqPwd+", "+
                                                                                     rabMqVhost+", "+
                                                                                     rabMqHost+", "+
                                                                                     rabMqPortNum);
        } 
        return connection;
    }

    public void finalize() {
        if(!closed)
            try {
                close();
            } catch( IOException e ) {
                error("Unable to close connection", e);
            }
    }
    
    public void close() throws IOException {
        connection.close();
        closed = true;
    }
    
    public void setSid(Sid sid) {
        Sid old_sid = this.sid;
        this.sid = sid;
        return old_sid;
    }
    public void clearSid() {
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
            String formatStr = String.format("%s:%s:%02d:%02d:%s; %s", 
                                                                                sid.key, sid.originator, sid.issueDt.getHourOfDay(), sid.issueDt.getMinuteOfHour(), 
                                                                                service, message);
            System.out.println(Level.DEBUG+": "+formatStr);
            try {
                channel.basicPublish(exchName, Level.DEBUG.toString(), null, formatStr.getBytes(StandardCharsets.UTF_8));
            } catch(IOException e) {
                error(sid, service, "Unable to publish log to queue", e, false);
            }
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
        if(!level.below(Level.INFO)) {
            String formatStr = String.format("%s:%s:%02d:%02d:%s; %s", 
                                                                                sid.key, sid.originator, sid.issueDt.getHourOfDay(), sid.issueDt.getMinuteOfHour(), 
                                                                                service, message);
            System.out.println(Level.INFO+": "+formatStr);
            try {
                channel.basicPublish(exchName, Level.INFO.toString(), null, formatStr.getBytes(StandardCharsets.UTF_8));
            } catch(IOException e) {
                error(sid, service, "Unable to publish log to queue", e, false);
            }
        }
    }

    public void warn(String message) {
        warn(sid, service, message);
    }
    public void warn(Sid sid, String message) {
        warn(sid, service, message);
    }
    public void warn(String service, String message) {
        warn(sid, service, message)
    }
    public void warn(Sid sid, String service, String message) {
        if(!level.below(Level.WARN)) {
            String formatStr = String.format("%s:%s:%02d:%02d:%s; %s", 
                                                                                sid.key, sid.originator, sid.issueDt.getHourOfDay(), sid.issueDt.getMinuteOfHour(), 
                                                                                service, message);
            System.out.println(Level.WARN+": "+formatStr);
            try {
                channel.basicPublish(exchName, Level.WARN.toString(), null, formatStr.getBytes(StandardCharsets.UTF_8));
            } catch(IOException e) {
                error(sid, service, "Unable to publish log to queue", e, false);
            }   
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
        error(Sid.Empty, service, message, e, true);
    }
    public void error(Sid sid, String message, Exception e) {
        error(sid, service, message, e, true);
    }
    public void error(String service, String message, Exception e) {
        error(Sid.Empty, service, message, e, true);
    }
    public void error(Sid sid, String service, String message, Exception e) {
        error(sid, service, message, e, true);
    }
    public void error(String message, Exception e, boolean sendToQueue) {
        error(Sid.Empty, service, message, e, sendToQueue);
    }
    public void error(Sid sid, String message, Exception e, boolean sendToQueue) {
        error(sid, service, message, e, sendToQueue);
    }
    public void error(Sid sid, String service, String message, Exception exception, boolean sendToQueue) {
        String formatStr = String.format("%s:%s:%02d:%02d:%s; %s", 
                                                                            sid.key, sid.originator, sid.issueDt.getHourOfDay(), sid.issueDt.getMinuteOfHour(), 
                                                                            service, message);
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
        try {
            channel.basicPublish(exchName, Level.ERROR.toString(), null, formatStr.getBytes(StandardCharsets.UTF_8));
        } catch(IOException e) {
            error(sid, service, "Unable to publish log to queue", e, false);
        }
        System.exit(1);
    }
}
