package com.studybot.expense;

import com.studybot.user.User;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface ExpenseCategoryRepository extends JpaRepository<ExpenseCategory, Integer> {

    /** Lấy danh mục mặc định hệ thống (user_id = null) */
    @Query("SELECT c FROM ExpenseCategory c WHERE c.user IS NULL AND c.isActive = true ORDER BY c.sortOrder")
    List<ExpenseCategory> findDefaultCategories();

    /** Lấy tất cả danh mục user thấy (hệ thống + riêng của user) */
    @Query("SELECT c FROM ExpenseCategory c WHERE (c.user IS NULL OR c.user = :user) AND c.isActive = true ORDER BY c.sortOrder")
    List<ExpenseCategory> findAllForUser(@Param("user") User user);

    /** Lấy tất cả danh mục riêng của user */
    @Query("SELECT c FROM ExpenseCategory c WHERE c.user = :user AND c.isActive = true ORDER BY c.sortOrder")
    List<ExpenseCategory> findByUserAndIsActiveTrue(@Param("user") User user);

    /** Lấy toàn bộ danh mục của user kể cả đã xóa */
    @Query("SELECT c FROM ExpenseCategory c WHERE c.user = :user")
    List<ExpenseCategory> findByUser(@Param("user") User user);

    /** Tìm danh mục riêng theo tên */
    @Query("SELECT c FROM ExpenseCategory c WHERE c.user = :user AND LOWER(c.name) = LOWER(:name) AND c.isActive = true")
    List<ExpenseCategory> findByUserAndNameAndIsActiveTrue(@Param("user") User user, @Param("name") String name);

    /** Tìm danh mục riêng theo từ khóa */
    @Query("SELECT c FROM ExpenseCategory c WHERE c.user = :user AND LOWER(c.name) LIKE LOWER(CONCAT('%', :keyword, '%')) AND c.isActive = true")
    List<ExpenseCategory> searchByNameForUser(@Param("keyword") String keyword, @Param("user") User user);

    /** Tìm danh mục mặc định theo tên (dùng khi auto-categorize) */
    @Query("SELECT c FROM ExpenseCategory c WHERE c.user IS NULL AND LOWER(c.name) = LOWER(:name)")
    Optional<ExpenseCategory> findDefaultByName(@Param("name") String name);

    /** Tìm danh mục có từ khóa trong tên */
    @Query("SELECT c FROM ExpenseCategory c WHERE c.user IS NULL AND LOWER(c.name) LIKE LOWER(CONCAT('%', :keyword, '%'))")
    List<ExpenseCategory> searchByName(@Param("keyword") String keyword);
}
