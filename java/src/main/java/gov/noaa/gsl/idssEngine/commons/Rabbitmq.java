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
import com.rabbitmq.client.Consumer;

public class Rabbitmq {
    
    static public class ConnectionParams {
        public final String rabMqVhost;
        public final String rabMqHost;
        public final String rabMqPortNum;
        public final String rabMqUser;
        public final String rabMqPwd;
        
        static public ConnectionParams fromRabbitmqObj(JSONObject rabbitmqObj) {
            String vHost = rabbitmqObj.has("virtualHost") ? rabbitmqObj.getString("virtualHost") : null;
            String hostName = rabbitmqObj.has("hostName") ? rabbitmqObj.getString("hostName") : null;
            String portNum = rabbitmqObj.has("portNumber") ? Integer.toString(rabbitmqObj.getInt("portNumber")) : null;
            String userName = rabbitmqObj.has("userName") ? rabbitmqObj.getString("userName") : null;
            String password = rabbitmqObj.has("password") ? rabbitmqObj.getString("password") : null;
            return new ConnectionParams(vHost, hostName, portNum, userName, password);
        }
        public ConnectionParams(String rabMqVhost, String rabMqHost, String rabMqPortNum, 
                                                           String rabMqUser,  String rabMqPwd) {
            this.rabMqVhost=rabMqVhost; this.rabMqHost=rabMqHost; this.rabMqPortNum=rabMqPortNum;
            this.rabMqUser=rabMqUser; this.rabMqPwd=rabMqPwd;
        }
    }
    
    static public class Topology {
        public final String exchName, exchType, exchRoutingKey;
        public final String queueName, queueRoutingKey;
        public final boolean queueDurable, queueExclusive, queueAutoDelete;

        public Topology(String topologyKey, JSONObject rabbitmqObj) {
            this(rabbitmqObj.getJSONObject(topologyKey));
        }
        public Topology(JSONObject topologyObj) {
            this(topologyObj.has("exchangeName") ? topologyObj.getString("exchangeName") : null,
                     topologyObj.has("exchangeType") ? topologyObj.getString("exchangeType") : null,
                     topologyObj.has("exchangeRoutingKey") ? topologyObj.getString("exchangeRoutingKey") : null,
                     topologyObj.has("queueName") ?  topologyObj.getString("queueName") : null,
                     topologyObj.has("queueRoutingKey") ? topologyObj.getString("queueRoutingKey") : null,
                     topologyObj.has("queueDurable") ? Boolean.parseBoolean(topologyObj.getString("queueDurable")) : false,
                     topologyObj.has("queueExclusive") ? Boolean.parseBoolean(topologyObj.getString("queueExclusive")) : false,
                     topologyObj.has("queueAutoDelete") ? Boolean.parseBoolean(topologyObj.getString("queueAutoDelete")) : false);
        }
        public Topology(String exchName, String exchType, String exchRoutingKey, String queueName, String queueRoutingKey, 
                                        boolean queueDurable, boolean queueExclusive, boolean queueAutoDelete) {
            this.exchName=exchName; this.exchType=exchType; this.exchRoutingKey=exchRoutingKey;
            this.queueName=queueName; this.queueRoutingKey=queueRoutingKey;
            this.queueDurable=queueDurable; this.queueExclusive=queueExclusive; this.queueAutoDelete=queueAutoDelete;
        }
    }
    
    public static Connection getConnection(String connName, JSONObject rabbitmqOb) {
        ConnectionParams connParams = ConnectionParams.fromRabbitmqObj(rabbitmqOb);
        return getConnection(connName, connParams);
    }
    public static Connection getConnection(String connName, ConnectionParams connParams) {
        return getConnection(connName,
                                                   connParams.rabMqVhost, connParams.rabMqHost, connParams.rabMqPortNum, 
                                                   connParams.rabMqUser,  connParams.rabMqPwd);
    }
    public static Connection getConnection(String connName, 
                                                                                    String rabMqVhost, String rabMqHost, String rabMqPortNum, 
                                                                                    String rabMqUser,  String rabMqPwd) {
        return getConnection(connName, rabMqVhost, rabMqHost, Integer.parseInt(rabMqPortNum), rabMqUser, rabMqPwd);
    }
    public static Connection getConnection(String connName, 
                                                                                    String rabMqVhost, String rabMqHost, int rabMqPortNum, 
                                                                                    String rabMqUser,  String rabMqPwd) {
        int numAttempts = 5;
        int attemptWait = 5500;
        ConnectionFactory factory = new ConnectionFactory();
        factory.setUsername(rabMqUser);
        factory.setPassword(rabMqPwd);
        factory.setVirtualHost(rabMqVhost);
        factory.setHost(rabMqHost);
        factory.setPort(rabMqPortNum);
        factory.setTopologyRecoveryEnabled(true);
        factory.setAutomaticRecoveryEnabled(true);
        
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

    private Channel topoChannel;
    private Channel channel;
    private Topology topology;
    private int numAttempts = 3;
    private int attemptWait = 5500;
    private boolean autoAck = false;
    private boolean multiTag = false;
    private boolean requeue = false;
    
    public Rabbitmq(Connection connection, String topologyKey, JSONObject rabbitmqObj) throws IOException, TimeoutException {
        this(connection, new Topology(getJsonObj(topologyKey, rabbitmqObj)));
    }
    
    public Rabbitmq(Connection connection, Topology topology)  throws IOException, TimeoutException {                                             
       this.topology = topology;
       
       // build topology
       topoChannel = connection.createChannel();
       if(topology.exchName!=null) {
            topoChannel.exchangeDeclare(topology.exchName, topology.exchType);
       }
       if(topology.queueName!=null) {
            topoChannel.queueDeclare(topology.queueName, topology.queueDurable, topology.queueExclusive, topology.queueAutoDelete, null);
            topoChannel.queueBind(topology.queueName, topology.exchName, topology.queueRoutingKey);           
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
    
    public Channel getChannel() {
        return channel;
    }
    
    public String getExchName() {
        return topology.exchName;
    }
    public String getExchType() {
        return topology.exchType;
    }
    public String getExchRoutingKey() {
        return topology.exchRoutingKey;
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
               channel.basicPublish(topology.exchName, routingKey, props, body);
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
               channel.basicConsume(topology.queueName, autoAck, consumerTag, callback);
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
