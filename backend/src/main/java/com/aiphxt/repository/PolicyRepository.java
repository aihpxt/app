package com.aiphxt.repository;

import com.aiphxt.model.Policy;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface PolicyRepository extends JpaRepository<Policy, Long> {

    List<Policy> findByCategory(String category);

    List<Policy> findByPublishDate(String publishDate);

    List<Policy> findBySource(String source);

}