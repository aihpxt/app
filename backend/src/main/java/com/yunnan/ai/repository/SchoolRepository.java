package com.yunnan.ai.repository;

import com.yunnan.ai.model.School;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.JpaSpecificationExecutor;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface SchoolRepository extends JpaRepository<School, Long>, JpaSpecificationExecutor<School> {

    Optional<School> findByName(String name);

    List<School> findByCity(String city);

    List<School> findByDistrict(String district);

    List<School> findByType(Integer type);

    List<School> findByCityAndType(String city, Integer type);

    @Query("SELECT s FROM School s WHERE s.name LIKE %:keyword% OR s.city LIKE %:keyword%")
    List<School> searchByKeyword(@Param("keyword") String keyword);

    List<School> findByIsKey(Integer isKey);
}
