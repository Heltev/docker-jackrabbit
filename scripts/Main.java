import java.nio.file.Files;
import java.nio.file.Paths;
import java.nio.charset.Charset;
import java.nio.charset.StandardCharsets;
import java.io.IOException;

import org.apache.jackrabbit.api.JackrabbitSession;
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

        // last/default password
        String lastPassword;
        String lastPasswordFile = "/etc/gluu/conf/.jackrabbit_admin_password.last";

        try {
            lastPassword = readFile(lastPasswordFile);
            if (lastPassword.trim().isEmpty()) {
                System.out.println("Unable to get last password; fallback to default password");
                // fallback to Jackrabbit adminID where password equals uid
                lastPassword = username;
            }
        } catch (IOException exc) {
            // fallback to Jackrabbit adminID where password equals uid
            System.out.println("Unable to get last password due to IO error; fallback to default password");
            lastPassword = username;
        }

        // new password
        String password;
        String passwordFile = System.getenv("GLUU_JACKRABBIT_ADMIN_PASSWORD_FILE");

        if (passwordFile == null || passwordFile.trim().isEmpty()) {
            passwordFile = "/etc/gluu/conf/jackrabbit_admin_password";
        }

        try {
            password = readFile(passwordFile);
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
            Session session = repository.login(new SimpleCredentials(username, lastPassword.toCharArray()));

            UserManager userManager = ((JackrabbitSession) session).getUserManager();
            User authorizable = (User) userManager.getAuthorizable(username);

            authorizable.changePassword(password);
            try {
                writeFile(lastPasswordFile, password);
            } catch (IOException exc) {
                exc.printStackTrace();
            }

            session.save();
            if (session != null && session.isLive()) {
                session.logout();
            }
        } catch (RepositoryException e) {
            e.printStackTrace();
        }
    }

    static String readFile(String path) throws IOException {
        byte[] encoded = Files.readAllBytes(Paths.get(path));
        return new String(encoded, StandardCharsets.US_ASCII).trim();
    }

    static void writeFile(String path, String content) throws IOException {
        byte[] encoded = content.getBytes();
        Files.write(Paths.get(path), encoded);
    }
}
