-- 1. Сколько правил загружено?
SELECT COUNT(*) AS rules_count FROM road_fines;

-- 2. Наибольшие минимальные штрафы
SELECT article, violation, fine_min_azn, fine_max_azn
FROM road_fines
ORDER BY fine_min_azn DESC NULLS LAST
LIMIT 10;

-- 3. Распределение правил по штрафным баллам
SELECT penalty_points, COUNT(*) AS rules_count
FROM road_fines
GROUP BY penalty_points
ORDER BY penalty_points NULLS LAST;

-- 4. Строки с неполным диапазоном штрафа
SELECT article, violation, fine_min_azn, fine_max_azn
FROM road_fines
WHERE fine_min_azn IS NULL OR fine_max_azn IS NULL;
