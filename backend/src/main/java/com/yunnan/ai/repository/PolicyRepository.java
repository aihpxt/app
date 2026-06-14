package com.yunnan.ai.repository;

import com.yunnan.ai.model.Policy;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface PolicyRepository extends JpaRepository<Policy, Long> {
    
    Page<Policy> findByStatus(Integer status, Pageable pageable);
    
    Page<Policy> findByCityAndStatus(String city, Integer status, Pageable pageable);
    
    Page<Policy> findByCategoryAndStatus(String category, Integer status, Pageable pageable);
    
    @Query("SELECT p FROM Policy p WHERE p.status = :status AND " +
           "(p.title LIKE %:keyword% OR p.content LIKE %:keyword%)")
    Page<Policy> searchByKeyword(@Param("keyword") String keyword, 
                                  @Param("status") Integer status, 
                                  Pageable pageable);
    
    List<Policy> findByStatusOrderByPublishDateDesc(Integer status);
    
    List<Policy> findByCityOrderByPublishDateDesc(String city);
}
