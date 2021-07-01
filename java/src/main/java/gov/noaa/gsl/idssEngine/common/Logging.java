/*********************************************************************************
  * Copyright (c) 2021 Regents of the University of Colorado. All rights reserved.
 *
 * Contributors:
 *     Geary Layne
*********************************************************************************/

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.HashMap;
import java.util.Iterator;
import java.util.Map;
import java.util.concurrent.TimeoutException;

import org.apache.commons.cli.CommandLine;
import org.apache.commons.cli.CommandLineParser;
import org.apache.commons.cli.DefaultParser;
import org.apache.commons.cli.HelpFormatter;
import org.apache.commons.cli.Option;
import org.apache.commons.cli.Options;
import org.apache.commons.cli.ParseException;
import org.json.JSONArray;
import org.json.JSONObject;

import com.rabbitmq.client.Channel;
import com.rabbitmq.client.Connection;
import com.rabbitmq.client.ConnectionFactory;

import gov.noaa.gsd.fiqas.cartography.Projection;
import gov.noaa.gsd.fiqas.util.config.ConfigureFile;
import gov.noaa.gsl.idssEngine.common.ProductType;
import gov.noaa.gsl.idssEngine.dataMan.DataManAccess;


public class Logging {

    public static void main(String[] args) {       
        
          System.out.println("Start "+Logging.getName()+"...");
          
      
        // create options
        Options options = new Options();
        
        // add options   
        Option cOpt = Option.builder("c")
                .longOpt("config-file")
                .desc("the configuration json filename (required)")
                .hasArg()
                .argName("complete path to file")
                .required()
                .build();
        options.addOption(cOpt);        
        
        // parse args
        CommandLineParser parser = new DefaultParser();
        CommandLine cmd = null;

        try {
            cmd = parser.parse(options, args);
            
            if(cmd.hasOption('c')) {
               String configFileName = cmd.getOptionValue("c");
System.out.println("config file: "+configFileName);
               ConfigureFile.setFileName(configFileName);
           }
            
        } catch(ParseException e) {
            HelpFormatter formatter = new HelpFormatter();
            formatter.printHelp(DataManAccess.class.getSimpleName(), options );
            System.exit(0);
        }   
        
        Logging logging = new Logging(configFileName);

        System.out.println("Finish "+Logging.getName());
    }

    public final String DEBUG = "DEBUG: ";
    public final String INFO = "INFO: ";
    public final String WARN = "WARN: ";
    public final String ERROR = "ERROR: ";
    private final String logExchName;
    private final String logExchType;
    private final Connection connection;
    private final Channel channel;
        
    public Logging(String configFileName) {
        String rabMqUser;
        String rabMqPwd;
        String rabMqVhost;
        String rabMqHost;
        int rabMqPortNum;

        JSONObject configObj = ConfigureFile.getJsonObj();
        
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
        
        connection = factory.newConnection();
        channel = connection.createChannel();
        
        channel.exchangeDeclare(logExchName, logExchType);
    }
    
    public void close() throws IOException {
        connection.close();
    }
    
    public void debug(String uuid, String source, DateTime time String service, String message) {
        String formatStr = String.format("%s:%s:%02d:%02d:%s;%s", uuid, source, time.getHourOfDay(), time.getMinOfHour(), service, message);
        System.out.println(DEBUG+formatStr);
        channel.basicPublish(log, DEBUG, null, formatStr.getBytes(StandardCharsets.UTF_8));
    }
    
    public void info(String uuid, String source, DateTime time String service, String message) {
        String formatStr = String.format("%s:%s:%02d:%02d:%s;%s", uuid, source, time.getHourOfDay(), time.getMinOfHour(), service, message);
        System.out.println(INFO+formatStr);
        channel.basicPublish(log, INFO, null, formatStr.getBytes(StandardCharsets.UTF_8));
    }

    public void info(String uuid, String source, DateTime time String service, String message) {
        String formatStr = String.format("%s:%s:%02d:%02d:%s;%s", uuid, source, time.getHourOfDay(), time.getMinOfHour(), service, message);
        System.out.println(WARN+formatStr);
        channel.basicPublish(log, WARN, null, formatStr.getBytes(StandardCharsets.UTF_8));
    }

    public void info(String uuid, String source, DateTime time String service, String message) {
        String formatStr = String.format("%s:%s:%02d:%02d:%s;%s", uuid, source, time.getHourOfDay(), time.getMinOfHour(), service, message);
        System.err.println(ERROR+formatStr);
        channel.basicPublish(log, ERROR, null, formatStr.getBytes(StandardCharsets.UTF_8));
    }

}
