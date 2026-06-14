package com.yunnan.ai.repository;

import com.yunnan.ai.model.StudentInfo;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface StudentInfoRepository extends JpaRepository<StudentInfo, Long> {
    
    Optional<StudentInfo> findByUserId(Long userId);
    
    Optional<StudentInfo> findByExamId(String examId);
    
    boolean existsByExamId(String examId);
    
    Optional<StudentInfo> findByIdCard(String idCard);
}