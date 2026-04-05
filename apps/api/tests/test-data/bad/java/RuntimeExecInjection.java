import java.io.IOException;

public class RuntimeExecInjection {
    public void badShellExecution(String userInput) throws IOException {
        // BAD: Shell injection via Runtime.exec()
        Runtime.getRuntime().exec("rm -rf " + userInput);
    }

    public void badCommandExecution(String cmd) throws IOException {
        // BAD: Vulnerable to command injection
        Runtime runtime = Runtime.getRuntime();
        runtime.exec("/bin/bash -c " + cmd);
    }
}
