import java.security.*;

public class CryptoWeakHash {
    public void badHashWithMd5(String data) throws NoSuchAlgorithmException {
        // BAD: MD5 is cryptographically weak
        MessageDigest digest = MessageDigest.getInstance("MD5");
        digest.update(data.getBytes());
        byte[] hash = digest.digest();
    }

    public void badHashWithSha1(String data) throws NoSuchAlgorithmException {
        // BAD: SHA-1 is deprecated
        MessageDigest digest = MessageDigest.getInstance("SHA1");
        digest.update(data.getBytes());
        byte[] hash = digest.digest();
    }
}
