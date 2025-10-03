package org.example;

import org.apache.xmlrpc.webserver.WebServer;
import org.apache.xmlrpc.server.XmlRpcServer;
import org.apache.xmlrpc.server.PropertyHandlerMapping;
import org.apache.xmlrpc.XmlRpcException;
import org.apache.xmlrpc.client.XmlRpcClient;
import org.apache.xmlrpc.client.XmlRpcClientConfigImpl;
import org.apache.log4j.BasicConfigurator;

import java.net.InetAddress;
import java.net.URL;

public class App {

  public static class ClienteHandler {
    public void apagar() {
      System.out.println("Servidor llego a 1000 en el contador, apagando cliente...");
      System.exit(0);
    }
  }

  public static void contar(XmlRpcClient client, int timeout) throws XmlRpcException, InterruptedException {
    while (true) {
      Object response = client.execute("contador", new Object[] {});
      System.out.println("Respuesta del servidor: " + response);
      Thread.sleep(timeout);
    }
  }

  public static void main(String[] args) {
    try {
      if (args.length == 0) {
        System.err.println("Debes ingresar un timeout para el cliente");
        System.exit(-1);
      }
      int timeout = Integer.parseInt(args[0]);

      BasicConfigurator.configure();
      XmlRpcClientConfigImpl config = new XmlRpcClientConfigImpl();
      config.setServerURL(new URL("http://localhost:8080"));
      config.setEnabledForExtensions(true);
      XmlRpcClient client = new XmlRpcClient();
      client.setConfig(config);

      WebServer webServer = new WebServer(9090, InetAddress.getByName("0.0.0.0"));
      XmlRpcServer xmlRpcServer = webServer.getXmlRpcServer();
      PropertyHandlerMapping phm = new PropertyHandlerMapping();
      phm.addHandler("cliente", ClienteHandler.class);
      xmlRpcServer.setHandlerMapping(phm);

      webServer.start();
      new Thread(() -> {
        try {
          contar(client, timeout);
        } catch (Exception e) {
          e.printStackTrace();
        }
      }).start();

    } catch (Exception e) {
      e.printStackTrace();
    }
  }
}
