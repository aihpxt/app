package com.aiphxt.repository;

import com.aiphxt.model.School;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface SchoolRepository extends JpaRepository<School, Long> {

    List<School> findByCity(String city);

    List<School> findByPrefecture(String prefecture);

    List<School> findByLevel(String level);

    School findByName(String name);

}