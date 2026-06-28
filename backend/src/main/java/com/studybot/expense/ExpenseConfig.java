package com.studybot.expense;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.client.RestTemplate;

/**
 * Cấu hình beans dùng cho module Expense (HTTP client).
 * ObjectMapper được lấy từ JacksonConfig (@Primary) — không define lại ở đây.
 */
@Configuration
public class ExpenseConfig {

    /**
     * RestTemplate dùng để gọi các HTTP API bên ngoài.
     */
    @Bean
    public RestTemplate restTemplate() {
        return new RestTemplate();
    }
}
