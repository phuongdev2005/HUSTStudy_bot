package com.studybot.sheets;

import com.google.api.client.googleapis.javanet.GoogleNetHttpTransport;
import com.google.api.client.json.gson.GsonFactory;
import com.google.api.services.sheets.v4.Sheets;
import com.google.api.services.sheets.v4.SheetsScopes;
import com.google.auth.http.HttpCredentialsAdapter;
import com.google.auth.oauth2.GoogleCredentials;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.core.io.ResourceLoader;

import java.io.IOException;
import java.io.InputStream;
import java.security.GeneralSecurityException;
import java.util.List;

/**
 * Cấu hình Google Sheets API client dùng Service Account.
 *
 * Yêu cầu:
 *   - File google-credentials.json đặt trong src/main/resources/
 *   - Service Account cần có quyền đọc sheet (user share sheet với email SA)
 *   - Hoặc sheet set "Anyone with link can view" → SA đọc được không cần share
 */
@Configuration
@Slf4j
public class SheetsConfig {

    @Value("${google.sheets.credentials-path:classpath:google-credentials.json}")
    private String credentialsPath;

    @Value("${google.sheets.application-name:HUSTStudy Bot}")
    private String applicationName;

    private final ResourceLoader resourceLoader;

    public SheetsConfig(ResourceLoader resourceLoader) {
        this.resourceLoader = resourceLoader;
    }

    /**
     * Tạo Sheets API client được authenticate bằng Service Account.
     * Bean này được inject vào SheetsService.
     */
    @Bean
    public Sheets sheetsService() throws IOException, GeneralSecurityException {
        try {
            InputStream credStream = resourceLoader
                    .getResource(credentialsPath)
                    .getInputStream();

            GoogleCredentials credentials = GoogleCredentials
                    .fromStream(credStream)
                    .createScoped(List.of(SheetsScopes.SPREADSHEETS_READONLY));

            return new Sheets.Builder(
                    GoogleNetHttpTransport.newTrustedTransport(),
                    GsonFactory.getDefaultInstance(),
                    new HttpCredentialsAdapter(credentials))
                    .setApplicationName(applicationName)
                    .build();

        } catch (Exception e) {
            // Nếu chưa có credentials file → log warning nhưng không crash app
            // SheetsService sẽ trả lỗi khi được gọi
            log.warn("⚠️  Không tìm thấy google-credentials.json – Google Sheets API sẽ không khả dụng. " +
                     "Đặt file credentials vào src/main/resources/ để bật tính năng này.");
            return null;
        }
    }
}
