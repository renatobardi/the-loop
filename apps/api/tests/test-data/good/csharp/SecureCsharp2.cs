using System.Diagnostics;
using System.Text.Json;

class Secure {
    static void Main() {
        string input = GetUserInput();
        
        // Secure: Use proper escaping and no shell execution
        ProcessStartInfo psi = new ProcessStartInfo {
            FileName = "/bin/bash",
            Arguments = $"-c 'echo {EscapeShellArg(input)}'",
            UseShellExecute = false,
            RedirectStandardOutput = true
        };
        Process.Start(psi);
        
        // Secure: Use JSON deserialization instead of BinaryFormatter
        string jsonData = GetTrustedJson();
        var options = new JsonSerializerOptions();
        object obj = JsonSerializer.Deserialize<MyObject>(jsonData, options);
    }
    
    static string EscapeShellArg(string arg) {
        return "'" + arg.Replace("'", "'\\''") + "'";
    }
}
