import org.apache.hadoop.security.UserGroupInformation;
import java.io.IOException;
import java.security.PrivilegedExceptionAction;
import org.apache.pig.ExecType;
import org.apache.pig.PigServer;

public class PigDoAs {

    public PigDoAs() {}

    public static void main(String[] args) throws Exception {
        final String script = args[0];
        final String realuser = args[1];
        UserGroupInformation ugi = UserGroupInformation.createProxyUser(realuser, UserGroupInformation.getLoginUser());
        ugi.doAs(new PrivilegedExceptionAction<Void>() {
            @Override
            public Void run() throws Exception {

                PigServer pigServer = new PigServer(ExecType.MAPREDUCE);

                try {
                    pigServer.setBatchOn();
                    pigServer.registerScript(script);
                    pigServer.executeBatch();
                    pigServer.shutdown();
                } catch (IOException ex) {
                    ex.printStackTrace();
                }

                return null;
            }
        });
    }
}
