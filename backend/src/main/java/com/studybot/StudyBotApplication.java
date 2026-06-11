package com.studybot;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableScheduling;

@SpringBootApplication
@EnableScheduling
public class StudyBotApplication {
    public static void main(String[] args) {
        SpringApplication.run(StudyBotApplication.class, args);
    }
}
