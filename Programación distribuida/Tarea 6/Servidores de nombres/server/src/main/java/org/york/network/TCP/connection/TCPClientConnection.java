package org.york.network.TCP.connection;

import java.net.InetAddress;
import java.net.SocketException;
import java.net.UnknownHostException;

public class TCPClientConnection extends TCPConnection{

  TCPClientConnection(int port, String addr) throws SocketException, UnknownHostException{
    super(port, InetAddress.getByName(addr));
  }

  @Override
  protected boolean connect() {
    // 3-way handshake por parte del cliente
    
    return true;
  }

  @Override
  public boolean close() {
    // 4-way handshake por parte del cliente
    

    return true;
  }

}
