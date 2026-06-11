package com.studybot;

import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.ActiveProfiles;

@SpringBootTest
@ActiveProfiles("test")
class StudyBotApplicationTests {

    @Test
    void contextLoads() {
        // Kiểm tra Spring context khởi động thành công (bao gồm Flyway migration)
    }
}
