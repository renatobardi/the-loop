public class HardcodedCredentialCsharp {
    // BAD: Hardcoded API key
    private const string ApiKey = "sk_live_abcdefghijklmnopqrst";

    private string password = "Admin@123456";

    public void BadHttpClientSetup() {
        // BAD: TLS validation disabled
        var handler = new System.Net.Http.HttpClientHandler {
            ServerCertificateCustomValidationCallback = (msg, cert, chain, errors) => true
        };
    }
}
