/*********************************************************************************
  * Copyright (c) 2021 Regents of the University of Colorado. All rights reserved.
 *
 * Contributors:
 *     Geary Layne
*********************************************************************************/
package gov.noaa.gsl.idssEngine.commons;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.concurrent.TimeoutException;

import org.joda.time.DateTime;
import org.json.JSONObject;

import com.rabbitmq.client.Channel;
import com.rabbitmq.client.Connection;
import com.rabbitmq.client.ConnectionFactory;

public class Logger {

    public final String DEBUG = "DEBUG: ";
    public final String INFO = "INFO: ";
    public final String WARN = "WARN: ";
    public final String ERROR = "ERROR: ";
    private final String logExchName;
    private final String logExchType;
    private final Connection connection;
    private final Channel channel;
        
    public Logger(String configFileName) {
        String rabMqUser;
        String rabMqPwd;
        String rabMqVhost;
        String rabMqHost;
        int rabMqPortNum;

        JSONObject configObj = null;
        try {
            final byte[] encoded = Files.readAllBytes(Paths.get(configFileName));
            final String jsonString = new String(encoded, StandardCharsets.UTF_8);
            configObj = new JSONObject(jsonString);
        } catch (Exception e) {
            throw new RuntimeException(String.format("Unable to read cofiguration file (%s)", configFileName));
        }    
        
         JSONObject mqObj = null;
         if(configObj.has("rabbitMQ")) 
             mqObj = configObj.getJSONObject("rabbitMQ"); 
        else throw new RuntimeException("Config file must specify a RabbitMQ object");
          
         if(mqObj.has("userName")) rabMqUser = mqObj.getString("userName"); 
        else throw new RuntimeException("Config file must specify userName");

         if(mqObj.has("password")) rabMqPwd = mqObj.getString("password"); 
        else throw new RuntimeException("Config file must specify password");

         if(mqObj.has("virtualHost")) rabMqVhost = mqObj.getString("virtualHost"); 
        else throw new RuntimeException("Config file must specify virtualHost");

         if(mqObj.has("hostName")) rabMqHost = mqObj.getString("hostName"); 
        else throw new RuntimeException("Config file must specify hostName");

         if(mqObj.has("portNumber")) rabMqPortNum = mqObj.getInt("portNumber"); 
        else throw new RuntimeException("Config file must specify portNumber");

         if(mqObj.has("logExchangeName")) this.logExchName = mqObj.getString("logExchangeName"); 
        else throw new RuntimeException("Config file must specify logExchangeName");
       
         if(mqObj.has("logExchangeType")) this.logExchType = mqObj.getString("logExchangeType"); 
        else throw new RuntimeException("Config file must specify logExchangeType");

System.out.println("user: "+rabMqUser);
System.out.println("pass: "+rabMqPwd);
System.out.println("vHost: "+rabMqVhost);
System.out.println("host: "+rabMqHost);
System.out.println("portNum: "+rabMqPortNum);

        ConnectionFactory factory = new ConnectionFactory();
        factory.setUsername(rabMqUser);
        factory.setPassword(rabMqPwd);
        factory.setVirtualHost(rabMqVhost);
        factory.setHost(rabMqHost);
        factory.setPort(rabMqPortNum);
        
        try {
            connection = factory.newConnection();
            channel = connection.createChannel();
            
            channel.exchangeDeclare(logExchName, logExchType);
        } catch( IOException | TimeoutException e ) {
            throw new RuntimeException("Uanble to make rabbitMQ connection or create channel", e);
        } 
    }
    
    public void close() throws IOException {
        connection.close();
    }
    
    public void debug(Sid sid, String service, String message) {
        String formatStr = String.format("%s:%s:%02d:%02d:%s;%s", 
                                                                            sid.key, sid.originator, sid.issueDt.getHourOfDay(), sid.issueDt.getMinuteOfHour(), 
                                                                            service, message);
        System.out.println(DEBUG+": "+formatStr);
        try {
            channel.basicPublish(logExchName, DEBUG, null, formatStr.getBytes(StandardCharsets.UTF_8));
        } catch( IOException e ) {
            throw new RuntimeException("Uanble to publish to rabbitMQ", e);  
        }
    }
    
    public void info(Sid sid, String service, String message) {
        String formatStr = String.format("%s:%s:%02d:%02d:%s;%s", 
                                                                            sid.key, sid.originator, sid.issueDt.getHourOfDay(), sid.issueDt.getMinuteOfHour(), 
                                                                            service, message);
        System.out.println(INFO+": "+formatStr);
        try {
            channel.basicPublish(logExchName, INFO, null, formatStr.getBytes(StandardCharsets.UTF_8));
        } catch( IOException e ) {
            throw new RuntimeException("Uanble to publish to rabbitMQ", e);   
        }
    }

    public void warn(Sid sid, String service, String message) {
        String formatStr = String.format("%s:%s:%02d:%02d:%s;%s", 
                                                                            sid.key, sid.originator, sid.issueDt.getHourOfDay(), sid.issueDt.getMinuteOfHour(), 
                                                                            service, message);
        System.out.println(WARN+": "+formatStr);
        try {
            channel.basicPublish(logExchName, WARN, null, formatStr.getBytes(StandardCharsets.UTF_8));
        } catch( IOException e ) {
            throw new RuntimeException("Uanble to publish to rabbitMQ", e); 
        }
    }

    public void error(Sid sid, String service, String message) {
        String formatStr = String.format("%s:%s:%02d:%02d:%s;%s", 
                                                                            sid.key, sid.originator, sid.issueDt.getHourOfDay(), sid.issueDt.getMinuteOfHour(), 
                                                                            service, message);
        System.err.println(ERROR+": "+formatStr);
        try {
            channel.basicPublish(logExchName, ERROR, null, formatStr.getBytes(StandardCharsets.UTF_8));
        } catch( IOException e ) {
            throw new RuntimeException("Uanble to publish to rabbitMQ", e); 
        }
    }

}
