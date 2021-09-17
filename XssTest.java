import java.io.IOException;
import java.io.OutputStream;
import java.io.InputStream;
import java.net.InetSocketAddress;
import java.util.Scanner;
import java.util.Map;
import java.util.HashMap;

import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpHandler;
import com.sun.net.httpserver.HttpServer;

public class XssTest {

	public static void main(String args[]) throws Exception {
		System.out.println("Starting HTTP Server.");
		HttpServer server = HttpServer.create(new InetSocketAddress("0.0.0.0", 8001), 0);
		server.createContext("/xss", new TestHandler());
		server.setExecutor(null);
		server.start();

    }

    public static Map<String, String> queryToMap(String query) {
        Map<String, String> result = new HashMap<>();
        for (String param : query.split("&")) {
            String[] entry = param.split("=");
            if (entry.length > 1) {
                result.put(entry[0], entry[1]);
            }else{
                result.put(entry[0], "");
            }
        }
        return result;
    }

	static class TestHandler implements HttpHandler {
        @Override
        public void handle(HttpExchange t) throws IOException {
            String a = t.getRequestURI().getQuery().substring(2,t.getRequestURI().getQuery().length());
            System.out.println( a );

			t.sendResponseHeaders(200, 0);
            OutputStream os = t.getResponseBody();
            //os.write(response.getBytes());
            os.write("<html><head><script>".getBytes());
            os.write("xss=false;".getBytes());
            os.write("function vuln(value) { xss=value; }".getBytes());
            os.write("function alert(value) { xss=true; }".getBytes());
            os.write("</script></head><body>".getBytes());
            os.write( a.getBytes() );
            os.write( ("<a href=" + a + ">link</a>").getBytes() );
            os.write( ("<img src=" + a + ">").getBytes() );
            os.write("<script>".getBytes());
            os.write("for (let elem of document.body.getElementsByTagName(\"*\")) { var events=getEventListeners(elem); Object.values(events).forEach(function(e) {e[0].listener()} ) }".getBytes() );
            os.write("</script></body></html>".getBytes());
            os.close();
        }
    }
}
