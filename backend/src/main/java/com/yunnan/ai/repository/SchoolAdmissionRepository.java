package com.yunnan.ai.repository;

import com.yunnan.ai.model.SchoolAdmission;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface SchoolAdmissionRepository extends JpaRepository<SchoolAdmission, Long> {
    
    List<SchoolAdmission> findBySchoolIdOrderByYearDesc(Long schoolId);
    
    Optional<SchoolAdmission> findBySchoolIdAndYear(Long schoolId, Integer year);
    
    @Query("SELECT sa FROM SchoolAdmission sa WHERE sa.schoolId = :schoolId ORDER BY sa.year DESC LIMIT 1")
    Optional<SchoolAdmission> findLatestBySchoolId(@Param("schoolId") Long schoolId);
    
    @Query("SELECT sa FROM SchoolAdmission sa WHERE sa.schoolId IN :schoolIds AND sa.year = :year")
    List<SchoolAdmission> findBySchoolIdsAndYear(@Param("schoolIds") List<Long> schoolIds, 
                                                   @Param("year") Integer year);
    
    List<SchoolAdmission> findByYearOrderByMinScoreDesc(Integer year);
}
