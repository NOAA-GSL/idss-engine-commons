/*********************************************************************************
  * Copyright (c) 2022 Regents of the University of Colorado. All rights reserved.
 *
 * Contributors:
 *     Geary Layne
*********************************************************************************/
package gov.noaa.gsl.idssEngine.commons;

import java.io.IOException;
import java.util.concurrent.TimeoutException;

import org.json.JSONObject;

import com.rabbitmq.client.AMQP.BasicProperties;
import com.rabbitmq.client.Channel;
import com.rabbitmq.client.Connection;
import com.rabbitmq.client.ConnectionFactory;

public class RabbitmqPublish {
    
    private final ConnectionFactory factory;
    private final String exchName;
    private final String exchType;
    private int numAttempts = 3;
    private Connection connection;
    private Channel channel;
    
    public RabbitmqPublish(String key, JSONObject configObj) throws IOException, TimeoutException {
        this(getConfigArgs(key, configObj));
    }
    public RabbitmqPublish(String[] configArgs) throws IOException, TimeoutException {
        this(configArgs[0], configArgs[1], Integer.parseInt(configArgs[2]), configArgs[3], configArgs[4], configArgs[5], configArgs[6]);
    }
    public RabbitmqPublish(String rabMqVhost, String rabMqHost, int rabMqPortNum, String rabMqUser, String rabMqPwd,
                                                   String exchName, String exchType) throws IOException, TimeoutException {
        factory = new ConnectionFactory();
        factory.setUsername(rabMqUser);
        factory.setPassword(rabMqPwd);
        factory.setVirtualHost(rabMqVhost);
        factory.setHost(rabMqHost);
        factory.setPort(rabMqPortNum);

        this.exchName = exchName;
        this.exchType = exchType;
        
        getRabbitMqChannel();
    }
    
    private static String[] getConfigArgs(String key, JSONObject configObj) {
        return getConfigArgs(new String[] {key}, configObj);
    }
    private static String[] getConfigArgs(String[] keys, JSONObject configObj) {
         JSONObject rmqObj = configObj;

         for(String key : keys) {
             rmqObj = rmqObj.getJSONObject(key);
         }
         
         String[] configArgs = new String[7];
//         try {
            configArgs[0] = rmqObj.getString("virtualHost"); 
//         } catch(Exception e) {
//             error(service, "Config file must specify virtualHost", e);
//         }
         
//         try {
             configArgs[1] = rmqObj.getString("hostName"); 
//         } catch(Exception e) {
//             error(service, "Config file must specify hostName", e);
//         }
         
//         try {
             configArgs[2] = Integer.toString(rmqObj.getInt("portNumber")); 
//         } catch(Exception e) {
//             error(service, "Config file must specify portNumber", e);
//         }

//         try {
             configArgs[3] = rmqObj.getString("userName"); 
//         } catch(Exception e) {
//             error(service, "Config file must specify userName", e);
//         }
         
//         try {
            configArgs[4] = rmqObj.getString("password"); 
//         } catch(Exception e) {
//             error(service, "Config file must specify password", e);
//         }
         
//         try {
             configArgs[5] = rmqObj.getString("statusExchangeName"); 
//         } catch(Exception e) {
//             error(service, "Config file must specify statusExchangeName", e);
//         }
       
//        try {
             configArgs[6] = rmqObj.getString("statusExchangeType"); 
//         } catch(Exception e) {
//             error(service, "Config file must specify statusExchangeType", e);
//         }
        return configArgs;
    }
    
    private void getRabbitMqChannel() throws IOException, TimeoutException {
        try {
            if(channel!=null)
                channel.close();
            channel = connection.createChannel();
            channel.exchangeDeclare(exchName, exchType);
        } catch(Exception e) {
            getRabbitMqConnection();
            channel = connection.createChannel();
            channel.exchangeDeclare(exchName, exchType);
        }
    }
    
    private void getRabbitMqConnection()  throws IOException, TimeoutException {
        if(connection!=null)
            connection.close();
        connection = factory.newConnection();
    }
    
    public void close() throws IOException, TimeoutException {
        try {
            channel.close();
        } finally {
            connection.close();
        }
    }
    
   public boolean basicPublish(String routingKey, BasicProperties props, byte[] body) throws IOException, TimeoutException {
       boolean likelySuccess = false;
       for(int attempt=0; attempt<numAttempts; attempt++) {
           try {
               channel.basicPublish(exchName, routingKey, props, body);
               likelySuccess = true;
               break;
            } catch(IOException e) {
                getRabbitMqChannel();
            }
        }
       return likelySuccess;
   }
   
}
