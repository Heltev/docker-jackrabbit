import java.nio.file.Files;
import java.nio.file.Paths;
import java.nio.charset.Charset;
import java.nio.charset.StandardCharsets;
import java.io.IOException;

import org.apache.jackrabbit.api.JackrabbitSession;
import org.apache.jackrabbit.api.security.user.Authorizable;
import org.apache.jackrabbit.api.security.user.User;
import org.apache.jackrabbit.api.security.user.UserManager;
import org.apache.jackrabbit.core.TransientRepository;

import javax.jcr.Repository;
import javax.jcr.RepositoryException;
import javax.jcr.Session;
import javax.jcr.SimpleCredentials;
import java.io.File;

public class Main {
    public static void main(String[] args) {
        String username = System.getenv("GLUU_JACKRABBIT_ADMIN_ID");

        if (username == null || username.trim().isEmpty()) {
            username = "admin";
        }

        String password;
        String passwordFile = System.getenv("GLUU_JACKRABBIT_ADMIN_PASSWORD_FILE");

        // default password file
        if (passwordFile == null || passwordFile.trim().isEmpty()) {
            passwordFile = "/etc/gluu/conf/jackrabbit_admin_password";
        }

        try {
            password = readFile(passwordFile, StandardCharsets.US_ASCII);
            if (password.trim().isEmpty()) {
                // fallback to Jackrabbit adminID where password equals uid
                password = username;
            }
        } catch (IOException exc) {
            // fallback to Jackrabbit adminID where password equals uid
            password = username;
        }

        Repository repository = new TransientRepository(new File("/opt/jackrabbit"));
        try {
            Session session = repository.login(new SimpleCredentials(username, username.toCharArray()));

            UserManager userManager = ((JackrabbitSession) session).getUserManager();
            Authorizable authorizable = userManager.getAuthorizable(username);

            ((User) authorizable).changePassword(password);

            session.save();
            session.logout();
        } catch (RepositoryException e) {
            e.printStackTrace();
        }

    }

    static String readFile(String path, Charset encoding) throws IOException {
        byte[] encoded = Files.readAllBytes(Paths.get(path));
        return new String(encoded, encoding).trim();
    }
}
