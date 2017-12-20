SELECT *
FROM (
       SELECT
         subject_id,
         hadm_id,
         age,
         gender,
         category,
         text,
         row_number()
         OVER (
           PARTITION BY subject_id, hadm_id, age, gender, category
           ) AS rn
       FROM (
              SELECT
                pt.subject_id                          AS subject_id,
                adm.hadm_id                            AS hadm_id,
                date_part('year', age(admittime, dob)) AS age,
                gender                                 AS gender,
                category                               AS category,
                text                                   AS text
              FROM
                (
                  SELECT *
                  FROM admissions
                  ORDER BY subject_id, hadm_id
                  LIMIT 1000
                ) AS adm
                INNER JOIN patients AS pt
                  ON pt.subject_id = adm.subject_id
                INNER JOIN noteevents AS ne
                  ON ne.subject_id = adm.subject_id
                     AND ne.hadm_id = adm.hadm_id
              WHERE category = 'Discharge summary'
            ) AS S
     ) AS S
WHERE rn = 1