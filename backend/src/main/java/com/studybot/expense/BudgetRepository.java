package com.studybot.expense;

import com.studybot.user.User;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface BudgetRepository extends JpaRepository<Budget, Long> {

    /** Lấy tất cả budget của user trong tháng */
    List<Budget> findByUserAndMonthAndYear(User user, int month, int year);

    /** Lấy budget cụ thể theo danh mục + tháng */
    Optional<Budget> findByUserAndCategoryAndMonthAndYear(
            User user, ExpenseCategory category, int month, int year);

    /** Lấy các budget cần check cảnh báo (chưa gửi 80% hoặc 100%) */
    @Query("SELECT b FROM Budget b WHERE b.user = :user AND b.month = :month AND b.year = :year " +
           "AND (b.isNotified80 = false OR b.isNotified100 = false)")
    List<Budget> findUnnotifiedBudgets(
            @Param("user")  User user,
            @Param("month") int month,
            @Param("year")  int year);
}
