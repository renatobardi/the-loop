using System.Diagnostics;

class Bad {
    static void Main() {
        string cmd = GetUserInput();
        
        // csharp-injection-003: ProcessStartInfo with UseShellExecute=true
        ProcessStartInfo psi = new ProcessStartInfo(cmd) { UseShellExecute = true };
        Process.Start(psi);
    }
}
