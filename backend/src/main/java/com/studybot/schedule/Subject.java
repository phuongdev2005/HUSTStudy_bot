package com.studybot.schedule;

import jakarta.persistence.*;
import lombok.*;
import com.studybot.user.User;

/**
 * Entity môn học.
 * Một môn có thể có nhiều buổi học trong tuần (ClassSession).
 */
@Entity
@Table(name = "subjects")
@Getter @Setter
@NoArgsConstructor @AllArgsConstructor
@Builder
public class Subject {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id", nullable = false)
    private User user;

    @Column(name = "name", nullable = false, length = 200)
    private String name;              // Tên môn học

    @Column(name = "code", length = 20)
    private String code;              // Mã môn (vd: IT3080)

    @Column(name = "teacher", length = 200)
    private String teacher;           // Tên giảng viên

    @Column(name = "credits")
    private Integer credits;          // Số tín chỉ

    @Builder.Default
    @Column(name = "is_active", nullable = false)
    private Boolean isActive = true;
}
