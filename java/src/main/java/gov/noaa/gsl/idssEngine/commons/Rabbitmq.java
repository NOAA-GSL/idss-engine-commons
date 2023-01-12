/*********************************************************************************
  * Copyright (c) 2022 Regents of the University of Colorado. All rights reserved.
 *
 * Contributors:
 *     Geary Layne
*********************************************************************************/
package gov.noaa.gsl.idssEngine.commons;

import java.io.IOException;
import java.util.Arrays;
import java.util.concurrent.TimeoutException;

import org.json.JSONObject;

import com.rabbitmq.client.AMQP.BasicProperties;
import com.rabbitmq.client.Channel;
import com.rabbitmq.client.Connection;
import com.rabbitmq.client.ConnectionFactory;
import com.rabbitmq.client.Consumer;

public class Rabbitmq {
    
    private final String exchName, exchType, exchRoutingKey;
    private final String queueName, queueRoutingKey;
    private final boolean queueDurable, queueExclusive, queueAutoDelete;
    private Connection connection;
    private Channel channel;
    private int numAttempts = 3;
    private int attemptWait = 5500;
    private boolean autoAck = false;
    private boolean multiTag = false;
    private boolean requeue = false;
    
    public Rabbitmq(String rabbitmqObjKey, String topologyKey, JSONObject configObj) throws IOException, TimeoutException {
        this(topologyKey, getJsonObj(rabbitmqObjKey, configObj));
    }

    public Rabbitmq(String topologyKey, JSONObject rabbitmqObj) throws IOException, TimeoutException {
        this(topologyKey, getRabbitmqArgs(rabbitmqObj), getTopologyArgs(getJsonObj(topologyKey, rabbitmqObj)));
    }
    
    public Rabbitmq(String connName, String[] configArgs, String[] topologyArgs) throws NumberFormatException, IOException, TimeoutException {
        this(connName,
                 configArgs[0], configArgs[1], Integer.parseInt(configArgs[2]), configArgs[3], configArgs[4], 
                 topologyArgs[0], topologyArgs[1], topologyArgs[2], topologyArgs[3], 
                 topologyArgs[4], topologyArgs[5], topologyArgs[6], topologyArgs[7]);
    }
    
//    public Rabbitmq(String rabMqVhost, String rabMqHost, int rabMqPortNum, String rabMqUser, String rabMqPwd,
//                                     String exchName, String exchType, String exchRoutingKey, String queueName, String queueRoutingKey, 
//                                     String queueDurable, String queueExclusive, String queueAutoDelete)  throws IOException, TimeoutException {
//        this(null, rabMqVhost, rabMqHost, rabMqPortNum, rabMqUser, rabMqPwd, exchName, exchType, exchRoutingKey,
//                 queueName, queueRoutingKey, queueDurable, queueExclusive, queueAutoDelete);
//    }

    public Rabbitmq(String connName, String rabMqVhost, String rabMqHost, int rabMqPortNum, String rabMqUser, String rabMqPwd,
                                     String exchName, String exchType, String exchRoutingKey, String queueName, String queueRoutingKey, 
                                     String queueDurable, String queueExclusive, String queueAutoDelete)  throws IOException, TimeoutException {
                                                   
        ConnectionFactory factory = new ConnectionFactory();
        factory.setUsername(rabMqUser);
        factory.setPassword(rabMqPwd);
        factory.setVirtualHost(rabMqVhost);
        factory.setHost(rabMqHost);
        factory.setPort(rabMqPortNum);
        
        connection = getConnection(factory, connName);
        
       this.exchName = exchName;
       this.exchType = exchType;
       this.exchRoutingKey = exchRoutingKey;
       this.queueName = queueName;
       this.queueRoutingKey = queueRoutingKey;
       this.queueDurable = Boolean.parseBoolean(queueDurable);
       this.queueExclusive = Boolean.parseBoolean(queueExclusive);
       this.queueAutoDelete = Boolean.parseBoolean(queueAutoDelete);

       // build topology
       Channel topoCannal = connection.createChannel();
       if(exchName!=null) {
            topoCannal.exchangeDeclare(this.exchName, this.exchType);
       }
       if(queueName!=null) {
            topoCannal.queueDeclare(queueName, this.queueDurable, this.queueExclusive, this.queueAutoDelete, null);
            topoCannal.queueBind(queueName, exchName, this.queueRoutingKey);           
       }
            
        channel = connection.createChannel();
    }

    private static JSONObject getJsonObj(String key, JSONObject jsonObj) {
        return getJsonObj(new String[] {key}, jsonObj);
    }
    
    private static JSONObject getJsonObj(String[] keys, JSONObject jsonObj) {
         for(String key : keys) {
             jsonObj = jsonObj.getJSONObject(key);
         }
         return jsonObj;
    }

    private static String[] getRabbitmqArgs(JSONObject rabbitmqObj) {
         
         String[] configArgs = new String[5];
//         try {
            configArgs[0] = rabbitmqObj.getString("virtualHost"); 
//         } catch(Exception e) {
//             error(service, "Config file must specify virtualHost", e);
//         }
         
//         try {
             configArgs[1] = rabbitmqObj.getString("hostName"); 
//         } catch(Exception e) {
//             error(service, "Config file must specify hostName", e);
//         }
         
//         try {
             configArgs[2] = Integer.toString(rabbitmqObj.getInt("portNumber")); 
//         } catch(Exception e) {
//             error(service, "Config file must specify portNumber", e);
//         }

//         try {
             configArgs[3] = rabbitmqObj.getString("userName"); 
//         } catch(Exception e) {
//             error(service, "Config file must specify userName", e);
//         }
         
//         try {
            configArgs[4] = rabbitmqObj.getString("password"); 
//         } catch(Exception e) {
//             error(service, "Config file must specify password", e);
//         }

        return configArgs;
    }

    private static String[] getTopologyArgs(JSONObject topologyObj) {
        
         String[] configArgs = {null, null, null, null, null, null, null, null};
         
         try {
             configArgs[0] = topologyObj.getString("exchangeName"); 
         } catch (Exception e) {}
         try {
             configArgs[1] = topologyObj.getString("exchangeType"); 
         } catch (Exception e) {}
         try {
             configArgs[2] = topologyObj.getString("exchangeRoutingKey"); 
         } catch (Exception e) {}
         try {
             configArgs[3] = topologyObj.getString("queueName"); 
         } catch (Exception e) {}
         try {
             configArgs[4] = topologyObj.getString("queueRoutingKey"); 
         } catch (Exception e) {}
         try {
             configArgs[5] = topologyObj.getString("queueDurable"); 
         } catch (Exception e) {}
         try {
             configArgs[6] = topologyObj.getString("queueExclusive"); 
         } catch (Exception e) {}
         try {
             configArgs[7] = topologyObj.getString("queueAutoDelete"); 
         } catch (Exception e) {}
         
        return configArgs;
    }
    
    private Connection getConnection(ConnectionFactory factory, String connName) {
        Connection connection = null;
        for(int i=0; i<numAttempts; i++) {
            try {
                if(connName==null)
                    connection = factory.newConnection();
                else
                    connection = factory.newConnection(connName);
                return connection;
            }  catch (Exception e) {
                e.printStackTrace();
                try {
                    Thread.sleep(attemptWait);
                } catch( InterruptedException e1 ) {}
            }
        }
        throw new RuntimeException("Unable to create a RabbitMq Connection");
    }
    
    public Channel getChannel() {
        return channel;
    }
    
    public String getExchName() {
        return exchName;
    }
    public String getExchType() {
        return exchType;
    }
    public String getExchRoutingKey() {
        return exchRoutingKey;
    }

    public boolean setAutoAck(boolean autoAck) {
        this.autoAck = autoAck;
        return true;
    }
    public boolean setMultiTag(boolean multiTag) {
        this.multiTag = multiTag;
        return true;
    }
    public boolean setRequeue(boolean requeue) {
        this.requeue = requeue;
        return true;
    }
    public boolean setNumAttempts(int num) {
        this.numAttempts = num;
        return true;
    }
    public boolean setAttemptWait(int waitInMillis) {
        this.attemptWait = waitInMillis;
        return true;
    }
    
    public boolean setPrefetchCount(int cnt) {
        for(int i=0; i<numAttempts; i++) {
            try {
                channel.basicQos(cnt);
                return true;
            }  catch (Exception  e) {
                try {
                    Thread.sleep(attemptWait);
                } catch( InterruptedException e1 ) {}
            }
        }
        return false;
    }
    
   public void basicPublish(String routingKey, BasicProperties props, byte[] body) throws IOException {
       IOException exception = null;
       for(int attempt=0; attempt<numAttempts; attempt++) {
           try {
               channel.basicPublish(exchName, routingKey, props, body);
               break;
            } catch(IOException e) {
                exception = e;
                try {
                    Thread.sleep(attemptWait);
                } catch( InterruptedException e1 ) {}
            }
        }
       if(exception != null) throw exception;
   }
   
   public void basicConsume(String consumerTag, Consumer callback) throws IOException {
       IOException exception = null;
       for(int attempt=0; attempt<numAttempts; attempt++) {
           try {
               channel.basicConsume(queueName, autoAck, consumerTag, callback);
               break;
            } catch(IOException e) {
                exception = e;
                try {
                    Thread.sleep(attemptWait);
                } catch( InterruptedException e1 ) {}
            }
        }
       if(exception != null) throw exception;
   }
   
   public void basicAck(long deliveryTag) throws IOException {
       IOException exception = null;
       for(int attempt=0; attempt<numAttempts; attempt++) {
           try {
               channel.basicAck(deliveryTag, multiTag);
               break;
            } catch(IOException e) {
                exception = e;
                try {
                    Thread.sleep(attemptWait);
                } catch( InterruptedException e1 ) {}
            }
        }
       if(exception != null) throw exception;
   }

   public void basicNack(long deliveryTag) throws IOException {
       IOException exception = null;
       for(int attempt=0; attempt<numAttempts; attempt++) {
           try {
               channel.basicNack(deliveryTag, multiTag, requeue);
               break;
            } catch(IOException e) {
                exception = e;
                try {
                    Thread.sleep(attemptWait);
                } catch( InterruptedException e1 ) {}
            }
        }
       if(exception != null) throw exception;
   }
   
}
