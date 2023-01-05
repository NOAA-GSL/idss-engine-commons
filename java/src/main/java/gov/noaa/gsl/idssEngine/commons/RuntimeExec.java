/*********************************************************************************
  * Copyright (c) 2022 Regents of the University of Colorado. All rights reserved.
 *
 * Contributors:
 *     Geary Layne
*********************************************************************************/
package gov.noaa.gsl.idssEngine.commons;

import java.io.BufferedReader;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.List;

public class RuntimeExec {

    public static class ReadStream implements Runnable {
        final String name;
        final InputStream is;
        final List<String> response;
        Exception exception = null;
        Thread thread;      
        public ReadStream(String name, InputStream is) {
            this(name, is, false);
        }
        public ReadStream(String name, InputStream is, boolean storeResponse) {
            this.name = name;
            this.is = is;
            if(storeResponse)
                response = new ArrayList<>();
            else 
                response = null;
        }       
        public void start () {
            thread = new Thread (this);
            thread.start ();
        }       
        public void run () {
            try {
                InputStreamReader isr = new InputStreamReader (is);
                BufferedReader br = new BufferedReader (isr);   
                if(response!=null) {
                    response.clear();
                    while (true) {
                        String s = br.readLine ();
                        if (s == null) break;
                        response.add(s);
                    }
                } else {
                    while (true) {
                        String s = br.readLine ();
                        if (s == null) break;
//                        System.out.println ("[" + name + "] " + s);
                    }
                }
                is.close ();    
            } catch (Exception e) {
                exception = e;  
            }
        }
        
        public List<String> getResponse() {
            return response;
        }
        public Exception getExceptions()  {
            return exception;
        }
    }
    
    public static int run(String[] cmd, List<String> errorResponse) throws Exception {
        return run(cmd, errorResponse, null);
    }
    public static int run(String[] cmd, List<String> errorResponse, List<String> inputResponse) throws Exception {
        Process p = null;
        try {
            p = Runtime.getRuntime().exec(cmd) ;  
            ReadStream s1 = new ReadStream("stdin", p.getInputStream(), inputResponse!=null);
            ReadStream s2 = new ReadStream("stderr", p.getErrorStream(), errorResponse!=null);
            s1.start ();
            s2.start ();
           int  result = p.waitFor();        
            if(inputResponse!=null) inputResponse.addAll(s1.response); 
            if(errorResponse!=null) errorResponse.addAll(s2.response); 
            if(s1.exception!=null) throw s1.exception;
            if(s2.exception!=null) throw s2.exception;
            return result;
        } finally {
            if(p != null)
                p.destroy();
        }
    }
}
