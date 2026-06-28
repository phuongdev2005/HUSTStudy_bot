package com.studybot.sheets;

import com.google.api.client.googleapis.javanet.GoogleNetHttpTransport;
import com.google.api.client.http.HttpRequest;
import com.google.api.client.http.HttpRequestInitializer;
import com.google.api.client.json.gson.GsonFactory;
import com.google.api.services.sheets.v4.Sheets;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.io.IOException;
import java.security.GeneralSecurityException;

/**
 * Cấu hình Google Sheets API client dùng API Key.
 *
 * Yêu cầu:
 *   - Biến môi trường GOOGLE_API_KEY chứa Google Sheets API Key
 *   - Sheet phải được set "Anyone with the link can view" (Public)
 *   - Bật Google Sheets API tại Google Cloud Console
 *
 * Cách tạo API Key:
 *   1. Vào https://console.cloud.google.com/
 *   2. APIs & Services → Library → "Google Sheets API" → Enable
 *   3. APIs & Services → Credentials → Create Credentials → API Key
 *   4. (Tùy chọn) Restrict key: chỉ cho Google Sheets API
 */
@Configuration
@Slf4j
public class SheetsConfig {

    @Value("${google.sheets.api-key:}")
    private String apiKey;

    @Value("${google.sheets.application-name:HUSTStudy Bot}")
    private String applicationName;

    /**
     * Tạo Sheets API client được authenticate bằng API Key.
     * Bean này được inject vào SheetsService dưới tên "sheetsClient".
     *
     * Nếu chưa có API Key → log warning và trả null.
     * SheetsService sẽ trả lỗi thân thiện khi được gọi.
     */
    @Bean(name = "sheetsClient")
    public Sheets sheetsClient() throws IOException, GeneralSecurityException {
        if (apiKey == null || apiKey.isBlank()) {
            log.warn("⚠️  GOOGLE_API_KEY chưa được cấu hình – Google Sheets API sẽ không khả dụng. " +
                     "Thêm GOOGLE_API_KEY vào file .env để bật tính năng này.");
            return null;
        }

        try {
            // API Key được truyền như một query parameter tự động
            // bằng cách gọi .setKey(apiKey) trên request thông qua HttpRequestInitializer
            HttpRequestInitializer requestInitializer = new HttpRequestInitializer() {
                @Override
                public void initialize(HttpRequest request) throws IOException {
                    // Không cần OAuth – API Key được xử lý bởi Sheets.Builder.setGoogleClientRequestInitializer
                }
            };

            return new Sheets.Builder(
                    GoogleNetHttpTransport.newTrustedTransport(),
                    GsonFactory.getDefaultInstance(),
                    requestInitializer)
                    .setApplicationName(applicationName)
                    .setGoogleClientRequestInitializer(request -> request.put("key", apiKey))
                    .build();

        } catch (Exception e) {
            log.error("❌ Lỗi khởi tạo Google Sheets client: {}", e.getMessage(), e);
            return null;
        }
    }
}
