using System.Runtime.Serialization.Formatters.Binary;
using System.IO;

class Bad {
    static void Main() {
        byte[] data = GetUntrustedData();
        
        // csharp-security-003: BinaryFormatter deserialization
        BinaryFormatter formatter = new BinaryFormatter();
        using (MemoryStream ms = new MemoryStream(data)) {
            object obj = formatter.Deserialize(ms);
        }
    }
}
