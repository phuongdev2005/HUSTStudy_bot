package com.studybot.expense;

import com.studybot.user.User;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;

@Repository
public interface ExpenseRepository extends JpaRepository<Expense, Long> {

    /** Lịch sử giao dịch trong khoảng thời gian, mới nhất trước */
    @Query("SELECT e FROM Expense e WHERE e.user = :user " +
           "AND e.transactionAt BETWEEN :from AND :to " +
           "ORDER BY e.transactionAt DESC")
    List<Expense> findByUserAndPeriod(
            @Param("user") User user,
            @Param("from") LocalDateTime from,
            @Param("to")   LocalDateTime to);

    /** Tổng chi theo danh mục trong tháng */
    @Query("SELECT e.category.id, SUM(e.amount) FROM Expense e " +
           "WHERE e.user = :user AND e.type = 'EXPENSE' " +
           "AND MONTH(e.transactionAt) = :month AND YEAR(e.transactionAt) = :year " +
           "GROUP BY e.category.id")
    List<Object[]> sumByCategory(
            @Param("user")  User user,
            @Param("month") int month,
            @Param("year")  int year);

    /** Tổng thu/chi tháng */
    @Query("SELECT SUM(e.amount) FROM Expense e " +
           "WHERE e.user = :user AND e.type = :type " +
           "AND MONTH(e.transactionAt) = :month AND YEAR(e.transactionAt) = :year")
    BigDecimal sumByType(
            @Param("user")  User user,
            @Param("type")  Expense.ExpenseType type,
            @Param("month") int month,
            @Param("year")  int year);

    /** N giao dịch gần nhất */
    @Query("SELECT e FROM Expense e WHERE e.user = :user ORDER BY e.transactionAt DESC LIMIT :limit")
    List<Expense> findRecentByUser(@Param("user") User user, @Param("limit") int limit);

    /** Xóa tất cả giao dịch của user (dùng admin/reset) */
    void deleteAllByUser(User user);
}
