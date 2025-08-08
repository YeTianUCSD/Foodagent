/* =========================================================
 *  Database: AI4food_db
 *  DDL for participant-centred multi-modal dataset
 *  (c) 2025
 * ========================================================= */

-- 0. 建库
CREATE DATABASE IF NOT EXISTS `AI4food_db`
  DEFAULT CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE `AI4food_db`;

/* ---------------------------------------------------------
 * 1. 核心表
 * --------------------------------------------------------- */
DROP TABLE IF EXISTS `participants`;   -- 若存在则先删除表 participants

/* =====================================================
 *  TABLE: participants
 *  Auto-generated annotations; edit freely if需要更细描述
 ===================================================== */
CREATE TABLE `participants` (
  `id`                     VARCHAR(20)  NOT NULL,   -- Id
  `group`                  INT,   -- Group
  `age`                    INT,   -- Age
  `sex`                    ENUM('Male','Female','Other') DEFAULT NULL,   -- Sex
  `usual_weight_kg`        DECIMAL(5,2),   -- Usual Weight Kg
  `weight_5years_kg`       DECIMAL(5,2),   -- Weight 5years Kg
  `height_cm`              DECIMAL(5,2),   -- Height Cm
  `intervention_diet_kcal` SMALLINT UNSIGNED,   -- Intervention Diet Kcal
  `finished_intervention`  TINYINT(1),   -- Finished Intervention
  PRIMARY KEY (`id`)   -- 主键
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

/* ---------------------------------------------------------
 * 2. DS1 – Anthropometric measurements
 * --------------------------------------------------------- */
DROP TABLE IF EXISTS `anthropometrics`;   -- 若存在则先删除表 anthropometrics

/* =====================================================
 *  TABLE: anthropometrics
 *  Auto-generated annotations; edit freely if需要更细描述
 ===================================================== */
CREATE TABLE `anthropometrics` (
  `id`                 VARCHAR(20) NOT NULL,   -- Id
  `visit`              TINYINT UNSIGNED NOT NULL,   -- Visit
  `period`             VARCHAR(20),   -- Period
  `current_weight_kg`  DECIMAL(5,2),   -- Current Weight Kg
  `bmi_kg_m2`          DECIMAL(5,2),   -- Bmi Kg M2
  `fat_mass_perc`      DECIMAL(5,2),   -- Fat Mass Perc
  `muscle_mass_perc`   DECIMAL(5,2),   -- Muscle Mass Perc
  `visceral_fat_level` DECIMAL(4,1),   -- Visceral Fat Level
  `basal_metabolism`   SMALLINT UNSIGNED,   -- Basal Metabolism
  `waist_cm`           DECIMAL(5,2),   -- Waist Cm
  `hip_cm`             DECIMAL(5,2),   -- Hip Cm
  PRIMARY KEY (`id`,`visit`),   -- 主键
  CONSTRAINT `fk_anthro_participant`
    FOREIGN KEY (`id`) REFERENCES `participants` (`id`)   -- 外键约束
      ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

/* ---------------------------------------------------------
 * 3. DS2 – Health & Lifestyle
 * --------------------------------------------------------- */
DROP TABLE IF EXISTS `health`;   -- 若存在则先删除表 health

/* =====================================================
 *  TABLE: health
 *  Auto-generated annotations; edit freely if需要更细描述
 ===================================================== */
CREATE TABLE `health` (
  `id`                  VARCHAR(20) NOT NULL,   -- Id
  `oral_contraceptive`  TINYINT(1),   -- Oral Contraceptive
  `ring_contraceptive`  TINYINT(1),   -- Ring Contraceptive
  `antidepressants`     TINYINT(1),   -- Antidepressants
  `antiacids`           TINYINT(1),   -- Antiacids
  `antihistamines`      TINYINT(1),   -- Antihistamines
  `antiinflamatory`     TINYINT(1),   -- Antiinflamatory
  `iron`                TINYINT(1),   -- Iron
  `calcium`             TINYINT(1),   -- Calcium
  `antihypertensives`   TINYINT(1),   -- Antihypertensives
  `thyroid_hormone`     TINYINT(1),   -- Thyroid Hormone
  `antibiotics`         TINYINT(1),   -- Antibiotics
  `other_medication`    TINYINT(1),   -- Other Medication
  `no_medication`       TINYINT(1),   -- No Medication
  `hyperthyroidism`     TINYINT(1),   -- Hyperthyroidism
  `hypothyroidism`      TINYINT(1),   -- Hypothyroidism
  `hypercholesterolemia`TINYINT(1),   -- Hypercholesterolemia Tinyint(1),
  `triglyceridemia`     TINYINT(1),   -- Triglyceridemia
  `hypertension`        TINYINT(1),   -- Hypertension
  `depression`          TINYINT(1),   -- Depression
  `diabetes`            TINYINT(1),   -- Diabetes
  `lactose_intolerance` TINYINT(1),   -- Lactose Intolerance
  `other_illness`       TINYINT(1),   -- Other Illness
  `no_illness`          TINYINT(1),   -- No Illness
  `menopause`           TINYINT(1),   -- Menopause
  PRIMARY KEY (`id`),   -- 主键
  FOREIGN KEY (`id`) REFERENCES `participants` (`id`)   -- 外键约束
    ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS `lifestyle`;   -- 若存在则先删除表 lifestyle

/* =====================================================
 *  TABLE: lifestyle
 *  Auto-generated annotations; edit freely if需要更细描述
 ===================================================== */
CREATE TABLE `lifestyle` (
  `id`                      VARCHAR(20) NOT NULL,   -- Id
  `appetite`                BIGINT,   -- Appetite
  `daily_meals`             VARCHAR(20),   -- Daily Meals
  `meals_weekdays_out`      DECIMAL(6,2),   -- Meals Weekdays Out
  `meals_weekdays_home`     DECIMAL(6,2),   -- Meals Weekdays Home
  `meals_weekend_out`       DECIMAL(6,2),   -- Meals Weekend Out
  `meals_weekend_home`      DECIMAL(6,2),   -- Meals Weekend Home
  `defecation`              VARCHAR(20),   -- Defecation
  `urination`               VARCHAR(20),   -- Urination
  `water_ml`                BIGINT,   -- Water Ml
  `others_ml`               DECIMAL(6,2),   -- Others Ml
  `cigarettes_day`          BIGINT,   -- Cigarettes Day
  `cigars_day`              BIGINT,   -- Cigars Day
  `pipe_day`                BIGINT,   -- Pipe Day
  `alcohol`                 VARCHAR(20),   -- Alcohol
  `fermented_perc`          DECIMAL(6,2),   -- Fermented Perc
  `distilled_perc`          DECIMAL(6,2),   -- Distilled Perc
  `exercise`                VARCHAR(20),   -- Exercise
  `stress`                  TINYINT,   -- Stress
  `anxiety`                 TINYINT,   -- Anxiety
  `depression`              TINYINT,   -- Depression
  `eating_disorder`         TINYINT,   -- Eating Disorder
  `others_psychological`    TINYINT,   -- Others Psychological
  `no_psychological`        TINYINT,   -- No Psychological
  `sleep_weekdays`          DECIMAL(6,2),   -- Sleep Weekdays
  `sleep_weekend`           DECIMAL(6,2),   -- Sleep Weekend
  `insomnia`                TINYINT,   -- Insomnia
  `somnolence`              TINYINT,   -- Somnolence
  PRIMARY KEY (`id`),   -- 主键
  FOREIGN KEY (`id`) REFERENCES `participants` (`id`)   -- 外键约束
    ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


/* ---------------------------------------------------------
 * 4. DS4 – Biomarkers
   # 注意小于号
 * --------------------------------------------------------- */
DROP TABLE IF EXISTS `biomarkers`;   -- 若存在则先删除表 biomarkers

/* =====================================================
 *  TABLE: biomarkers
 *  Auto-generated annotations; edit freely if需要更细描述
 ===================================================== */
CREATE TABLE `biomarkers` (
  `id`                    VARCHAR(20) NOT NULL,   -- Id
  `visit`                 TINYINT UNSIGNED NOT NULL,   -- Visit
  `leukocytes_10e3_ul`    DECIMAL(6,2),   -- Leukocytes 10e3 Ul
  `plats_10e3_ul`         DECIMAL(6,2),   -- Plats 10e3 Ul
  `lympho_10e3_ul`        DECIMAL(6,2),   -- Lympho 10e3 Ul
  `mono_10e3_ul`          DECIMAL(6,2),   -- Mono 10e3 Ul
  `seg_10e3_ul`           DECIMAL(6,2),   -- Seg 10e3 Ul
  `eos_10e3_ul`           DECIMAL(6,2),   -- Eos 10e3 Ul
  `baso_10e3_ul`          DECIMAL(6,2),   -- Baso 10e3 Ul
  `erythrocytes_10e6_ul`  DECIMAL(6,2),   -- Erythrocytes 10e6 Ul
  `hgb_g_dl`              DECIMAL(5,2),   -- Hgb G Dl
  `hematocrit_perc`       DECIMAL(5,2),   -- Hematocrit Perc
  `mcv_fl`                DECIMAL(5,2),   -- Mcv Fl
  `mpv_fl`                DECIMAL(5,2),   -- Mpv Fl
  `mch_pg`                DECIMAL(5,2),   -- Mch Pg
  `mchc_g_dl`             DECIMAL(5,2),   -- Mchc G Dl
  `rdw_perc`              DECIMAL(5,2),   -- Rdw Perc
  `lympho_perc`           DECIMAL(5,2),   -- Lympho Perc
  `mono_perc`             DECIMAL(5,2),   -- Mono Perc
  `seg_perc`              DECIMAL(5,2),   -- Seg Perc
  `eos_perc`              DECIMAL(5,2),   -- Eos Perc
  `baso_perc`             DECIMAL(5,2),   -- Baso Perc
  `hba1c_perc`            DECIMAL(5,2),   -- Hba1c Perc
  `hba1ifcc_mmol_mol`     DECIMAL(6,2),   -- Hba1ifcc Mmol Mol
  `insulin_uui_ml`        DECIMAL(6,2),   -- Insulin Uui Ml
  `homa`                  DECIMAL(6,2),   -- Homa
  `glu_mg_dl`             SMALLINT,   -- Glu Mg Dl
  `chol_mg_dl`            SMALLINT,   -- Chol Mg Dl
  `tri_mg_dl`             SMALLINT,   -- Tri Mg Dl
  `hdl_mg_dl`             SMALLINT,   -- Hdl Mg Dl
  `ldl_mg_dl`             SMALLINT,   -- Ldl Mg Dl
  `homocysteine_umol_l`   DECIMAL(6,2),   -- Homocysteine Umol L
  `alb_g_dl`              DECIMAL(5,2),   -- Alb G Dl
  `prealbumin_mg_dl`      DECIMAL(6,2),   -- Prealbumin Mg Dl
  `crp_mg_dl`             DECIMAL(6,2),   -- Crp Mg Dl
  `igg_mg_dl`             DECIMAL(6,2),   -- Igg Mg Dl
  `iga_mg_dl`             DECIMAL(6,2),   -- Iga Mg Dl
  `igm_mg_dl`             DECIMAL(6,2),   -- Igm Mg Dl
  `ige_ui_ml`             DECIMAL(8,2),   -- Ige Ui Ml
  `tnf_a_ui_ml`           DECIMAL(8,2),   -- Tnf A Ui Ml
  `adiponectin_ug_ml`     DECIMAL(8,2),   -- Adiponectin Ug Ml
  PRIMARY KEY (`id`,`visit`),   -- 主键
  FOREIGN KEY (`id`) REFERENCES `participants` (`id`)   -- 外键约束
    ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

/* ---- Continuous glucose monitor (per-minute) ---- */
DROP TABLE IF EXISTS `glucose_levels`;   -- 若存在则先删除表 glucose_levels

/* =====================================================
 *  TABLE: glucose_levels
 *  Auto-generated annotations; edit freely if需要更细描述
 ===================================================== */
CREATE TABLE `glucose_levels` (
  `id`            VARCHAR(20) NOT NULL,   -- Id
  `ts`            DATETIME    NOT NULL,   -- Ts
  `glucose_mg_dl` SMALLINT UNSIGNED,   -- Glucose Mg Dl
  PRIMARY KEY (`id`,`ts`),   -- 主键
  FOREIGN KEY (`id`) REFERENCES `participants` (`id`)   -- 外键约束
    ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

/* ---------------------------------------------------------
 * 5. DS6 – Vital Signs
 * --------------------------------------------------------- */
DROP TABLE IF EXISTS `vital_signs`;   -- 若存在则先删除表 vital_signs

/* =====================================================
 *  TABLE: vital_signs
 *  Auto-generated annotations; edit freely if需要更细描述
 ===================================================== */
CREATE TABLE `vital_signs` (
  `id`               VARCHAR(20) NOT NULL,   -- Id
  `visit`            TINYINT UNSIGNED NOT NULL,   -- Visit
  `resting_hr_bpm`   SMALLINT,   -- Resting Hr Bpm
  `systolic_bp_mmhg` SMALLINT,   -- Systolic Bp Mmhg
  `diastolic_bp_mmhg`SMALLINT,   -- Diastolic Bp Mmhg Smallint,
  `heart_rate_bpm`   SMALLINT,   -- Heart Rate Bpm
  PRIMARY KEY (`id`,`visit`),   -- 主键
  FOREIGN KEY (`id`) REFERENCES `participants` (`id`)   -- 外键约束
    ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

/* ---------------------------------------------------------
 * ecg_recordings + ecg_waveforms
 * --------------------------------------------------------- */
DROP TABLE IF EXISTS `ecg_recordings`;   -- 若存在则先删除表 ecg_recordings

/* =====================================================
 *  TABLE: ecg_recordings
 *  Auto-generated annotations; edit freely if需要更细描述
 ===================================================== */
CREATE TABLE `ecg_recordings` (
  `id`                    VARCHAR(20)  NOT NULL,              -- 参与者 ID   -- Id
  `record_ts`             DATETIME     NOT NULL,              -- 本次 ECG 开始时间（CSV 的 timestamp）   -- Record Ts
  `result_classification` VARCHAR(20),                        -- 如 NSR / AF 等   -- Result Classification
  `average_heart_rate`    SMALLINT,                           -- 平均心率 (bpm)   -- Average Heart Rate
  `heart_rate_alert`      VARCHAR(20),                        -- NONE / HIGH / LOW ...   -- Heart Rate Alert
  `sample_count`          INT UNSIGNED,                       -- 该波形共有多少采样点   -- Sample Count
  PRIMARY KEY (`id`, `record_ts`),   -- 主键
  FOREIGN KEY (`id`) REFERENCES `participants` (`id`)   -- 外键约束
    ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;
DROP TABLE IF EXISTS `ecg_waveforms`;   -- 若存在则先删除表 ecg_waveforms

/* =====================================================
 *  TABLE: ecg_waveforms
 *  Auto-generated annotations; edit freely if需要更细描述
 ===================================================== */
CREATE TABLE `ecg_waveforms` (
  `id`          VARCHAR(20)  NOT NULL,   -- Id
  `record_ts`   DATETIME     NOT NULL,       -- 必须与 ecg_recordings.record_ts 对应   -- Record Ts
  `sample_idx`  INT UNSIGNED NOT NULL,       -- 从 0 开始的采样点索引   -- Sample Idx
  `voltage`     SMALLINT,                    -- 电压值（ADC 计数 / μV）   -- Voltage
  PRIMARY KEY (`id`, `record_ts`, `sample_idx`),   -- 主键
  FOREIGN KEY (`id`, `record_ts`) REFERENCES `ecg_recordings` (`id`, `record_ts`)   -- 外键约束
    ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;

/* ---------------------------------------------------------
 * heart_rate
 * --------------------------------------------------------- */
DROP TABLE IF EXISTS `heart_rate`;   -- 若存在则先删除表 heart_rate

/* =====================================================
 *  TABLE: heart_rate
 *  Auto-generated annotations; edit freely if需要更细描述
 ===================================================== */
CREATE TABLE `heart_rate` (
  `id`  VARCHAR(20) NOT NULL,   -- Id
  `ts`  DATETIME    NOT NULL,   -- Ts
  `bpm` SMALLINT,   -- Bpm
  PRIMARY KEY (`id`,`ts`),   -- 主键
  FOREIGN KEY (`id`) REFERENCES `participants` (`id`)   -- 外键约束
    ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

/* ---------------------------------------------------------
 * 6. DS7 – Physical Activity
 * --------------------------------------------------------- */

/* ============  IPAQ（International Physical Activity Questionnaire） ============ */
DROP TABLE IF EXISTS `physical_activity_ipaq`;   -- 若存在则先删除表 physical_activity_ipaq

/* =====================================================
 *  TABLE: physical_activity_ipaq
 *  Auto-generated annotations; edit freely if需要更细描述
 ===================================================== */
CREATE TABLE `physical_activity_ipaq` (
  `id`                 VARCHAR(20)  NOT NULL,              -- 参与者 ID   -- Id
  `visit`              TINYINT UNSIGNED NOT NULL,          -- 第几次随访   -- Visit

  `vigorous_n_days`    TINYINT,                            -- 每周做剧烈活动的天数   -- Vigorous N Days
  `vigorous_min_day`   SMALLINT,                           -- 剧烈活动当日分钟数   -- Vigorous Min Day
  `vigorous_met`       SMALLINT,                           -- 剧烈活动 MET∙min/周   -- Vigorous Met

  `moderate_n_days`    TINYINT,   -- Moderate N Days
  `moderate_min_day`   SMALLINT,   -- Moderate Min Day
  `moderate_met`       SMALLINT,   -- Moderate Met

  `walking_n_days`     TINYINT,   -- Walking N Days
  `walking_min_day`    SMALLINT,   -- Walking Min Day
  `walking_met`        SMALLINT,   -- Walking Met

  `total_met`          SMALLINT,                           -- 总 MET∙min/周   -- Total Met
  `categorical_score`  ENUM('low','moderate','high'),       -- IPAQ 分类结果   -- Categorical Score

  PRIMARY KEY (`id`,`visit`),    -- 主键
  FOREIGN KEY (`id`) REFERENCES `participants` (`id`)   -- 外键约束
      ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

/* ========= 1. 每日各强度分钟数 =========== */
DROP TABLE IF EXISTS `pa_active_minutes`;   -- 若存在则先删除表 pa_active_minutes

/* =====================================================
 *  TABLE: pa_active_minutes
 *  Auto-generated annotations; edit freely if需要更细描述
 ===================================================== */
CREATE TABLE `pa_active_minutes` (
  `id`                         VARCHAR(20) NOT NULL,   -- Id
  `day`                        DATE        NOT NULL,        -- 由 timestamp 取日期部分   -- Day
  `fat_burn_minutes`           SMALLINT UNSIGNED,   -- Fat Burn Minutes
  `cardio_minutes`             SMALLINT UNSIGNED,   -- Cardio Minutes
  `peak_minutes`               SMALLINT UNSIGNED,   -- Peak Minutes
  `sedentary_minutes`          SMALLINT UNSIGNED,   -- Sedentary Minutes
  `lightly_active_minutes`     SMALLINT UNSIGNED,   -- Lightly Active Minutes
  `moderately_active_minutes`  SMALLINT UNSIGNED,   -- Moderately Active Minutes
  `very_active_minutes`        SMALLINT UNSIGNED,   -- Very Active Minutes
  PRIMARY KEY (`id`,`day`),   -- 主键
  CONSTRAINT `fk_pa_intensity_id`
      FOREIGN KEY (`id`) REFERENCES `participants`(`id`)   -- 外键约束
      ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

/* ========= 2. 每日心率区间 / 计步汇总 =========== */
DROP TABLE IF EXISTS `pa_daily_summary`;   -- 若存在则先删除表 pa_daily_summary

/* =====================================================
 *  TABLE: pa_daily_summary
 *  Auto-generated annotations; edit freely if需要更细描述
 ===================================================== */
CREATE TABLE `pa_daily_summary` (
  `id`                              VARCHAR(20) NOT NULL,   -- Id
  `day`                             DATE        NOT NULL,   -- Day
  `resting_heart_rate`              DECIMAL(5,2),      -- bpm   -- Resting Heart Rate
  `altitude_m`                      SMALLINT,          -- 样例中整数   -- Altitude M
  `calories_kcal`                   DECIMAL(8,2),   -- Calories Kcal
  `steps`                           INT UNSIGNED,   -- Steps
  `distance_m`                      DECIMAL(10,2),   -- Distance M
  `min_below_default_zone_1`        SMALLINT UNSIGNED,   -- Min Below Default Zone 1
  `min_in_default_zone_1`           SMALLINT UNSIGNED,   -- Min In Default Zone 1
  `min_in_default_zone_2`           SMALLINT UNSIGNED,   -- Min In Default Zone 2
  `min_in_default_zone_3`           SMALLINT UNSIGNED,   -- Min In Default Zone 3
  PRIMARY KEY (`id`,`day`),   -- 主键
  CONSTRAINT `fk_pa_sum mary_id`
      FOREIGN KEY (`id`) REFERENCES `participants`(`id`)   -- 外键约束
      ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

/* ========= 3. VO2Max 每日估计 =========== */
DROP TABLE IF EXISTS `pa_estimated_VO2`;   -- 若存在则先删除表 pa_estimated_VO2

/* =====================================================
 *  TABLE: pa_estimated_VO2
 *  Auto-generated annotations; edit freely if需要更细描述
 ===================================================== */
CREATE TABLE `pa_estimated_VO2` (
  `id`                                  VARCHAR(20) NOT NULL,   -- Id
  `day`                                 DATE        NOT NULL,   -- Day
  `demographic_vo2_max`                 DECIMAL(6,2),   -- Demographic Vo2 Max
  `demographic_vo2_max_error`           DECIMAL(6,2),   -- Demographic Vo2 Max Error
  `filtered_demographic_vo2_max`        DECIMAL(6,2),   -- Filtered Demographic Vo2 Max
  `filtered_demographic_vo2_max_error`  DECIMAL(6,2),   -- Filtered Demographic Vo2 Max Error
  PRIMARY KEY (`id`,`day`),   -- 主键
  CONSTRAINT `fk_pa_vo2_id`
      FOREIGN KEY (`id`) REFERENCES `participants`(`id`)   -- 外键约束
      ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

/* ========= 4. 运动 Session 记录 =========== */
DROP TABLE IF EXISTS `pa_reports`;   -- 若存在则先删除表 pa_reports

/* =====================================================
 *  TABLE: pa_reports
 *  Auto-generated annotations; edit freely if需要更细描述
 ===================================================== */
CREATE TABLE `pa_reports` (
  `session_id`                      BIGINT AUTO_INCREMENT PRIMARY KEY,   -- Session Id
  `id`                              VARCHAR(20) NOT NULL,   -- Id
  `record_ts`                       DATETIME    NOT NULL,      -- CSV 的 timestamp   -- Record Ts
  `activity_name`                   VARCHAR(50),   -- Activity Name
  `average_heart_rate`              DECIMAL(5,2),   -- Average Heart Rate
  `duration_sec`                    INT UNSIGNED,              -- duration   -- Duration Sec
  `active_duration_sec`             INT UNSIGNED,   -- Active Duration Sec
  `calories_kcal`                   DECIMAL(8,2),   -- Calories Kcal
  `steps`                           INT UNSIGNED,   -- Steps

  `sedentary_minutes`               SMALLINT UNSIGNED,   -- Sedentary Minutes
  `lightly_active_minutes`          SMALLINT UNSIGNED,   -- Lightly Active Minutes
  `fairly_active_minutes`           SMALLINT UNSIGNED,   -- Fairly Active Minutes
  `very_active_minutes`             SMALLINT UNSIGNED,   -- Very Active Minutes

  `out_of_range_minutes`            SMALLINT UNSIGNED,   -- Out Of Range Minutes
  `out_of_range_min_hr`             DECIMAL(5,2),   -- Out Of Range Min Hr
  `out_of_range_max_hr`             DECIMAL(5,2),   -- Out Of Range Max Hr
  `out_of_range_calories`           DECIMAL(8,2),   -- Out Of Range Calories

  `fat_burn_minutes`                SMALLINT UNSIGNED,   -- Fat Burn Minutes
  `fat_burn_min_hr`                 DECIMAL(5,2),   -- Fat Burn Min Hr
  `fat_burn_max_hr`                 DECIMAL(5,2),   -- Fat Burn Max Hr
  `fat_burn_calories`               DECIMAL(8,2),   -- Fat Burn Calories

  `cardio_minutes`                  SMALLINT UNSIGNED,   -- Cardio Minutes
  `cardio_min_hr`                   DECIMAL(5,2),   -- Cardio Min Hr
  `cardio_max_hr`                   DECIMAL(5,2),   -- Cardio Max Hr
  `cardio_calories`                 DECIMAL(8,2),   -- Cardio Calories

  `peak_minutes`                    SMALLINT UNSIGNED,   -- Peak Minutes
  `peak_min_hr`                     DECIMAL(5,2),   -- Peak Min Hr
  `peak_max_hr`                     DECIMAL(5,2),   -- Peak Max Hr
  `peak_calories`                   DECIMAL(8,2),   -- Peak Calories

  INDEX `idx_pa_reports_id_ts` (`id`,`record_ts`),   -- 二级索引
  CONSTRAINT `fk_pa_reports_id`
      FOREIGN KEY (`id`) REFERENCES `participants`(`id`)   -- 外键约束
      ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


/* ---------------------------------------------------------
 * 7. DS8 – Sleep Activity
 * --------------------------------------------------------- */
DROP TABLE IF EXISTS `sleep_questionnaire`;   -- 若存在则先删除表 sleep_questionnaire

/* =====================================================
 *  TABLE: sleep_questionnaire
 *  Auto-generated annotations; edit freely if需要更细描述
 ===================================================== */
CREATE TABLE `sleep_questionnaire` (
  `id`         VARCHAR(20) NOT NULL,   -- Id
  `visit`      TINYINT UNSIGNED NOT NULL,   -- Visit
  `total_score`SMALLINT,   -- Total Score Smallint,
  PRIMARY KEY (`id`,`visit`),   -- 主键
  FOREIGN KEY (`id`) REFERENCES `participants` (`id`)   -- 外键约束
     ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS `additional_sleep`;   -- 若存在则先删除表 additional_sleep

/* =====================================================
 *  TABLE: additional_sleep
 *  Auto-generated annotations; edit freely if需要更细描述
 ===================================================== */
CREATE TABLE `additional_sleep` (
  `sleep_id`          BIGINT      NOT NULL,   -- Sleep Id
  `id`                VARCHAR(20) NOT NULL,   -- Id
  `start_time`        DATETIME,   -- Start Time
  `end_time`          DATETIME,   -- End Time
  `duration_min`      SMALLINT,   -- Duration Min
  `minutes_asleep`    SMALLINT,   -- Minutes Asleep
  `minutes_awake`     SMALLINT,   -- Minutes Awake
  `minutes_in_bed`    SMALLINT,   -- Minutes In Bed
  `main_sleep`        TINYINT(1),   -- Main Sleep
  `minutes_in_deep`   SMALLINT,   -- Minutes In Deep
  `minutes_in_light`  SMALLINT,   -- Minutes In Light
  `minutes_in_rem`    SMALLINT,   -- Minutes In Rem
  PRIMARY KEY (`sleep_id`),   -- 主键
  INDEX (`id`),   -- 二级索引
  FOREIGN KEY (`id`) REFERENCES `participants` (`id`)   -- 外键约束
     ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS `oxygen_sat_minute`;   -- 若存在则先删除表 oxygen_sat_minute

/* =====================================================
 *  TABLE: oxygen_sat_minute
 *  Auto-generated annotations; edit freely if需要更细描述
 ===================================================== */
CREATE TABLE `oxygen_sat_minute` (
  `id`   VARCHAR(20) NOT NULL,   -- Id
  `ts`   DATETIME    NOT NULL,   -- Ts
  `spo2` DECIMAL(5,2),   -- Spo2
  PRIMARY KEY (`id`,`ts`),   -- 主键
  FOREIGN KEY (`id`) REFERENCES `participants` (`id`)   -- 外键约束
    ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS `oxygen_sat_daily`;   -- 若存在则先删除表 oxygen_sat_daily

/* =====================================================
 *  TABLE: oxygen_sat_daily
 *  Auto-generated annotations; edit freely if需要更细描述
 ===================================================== */
CREATE TABLE `oxygen_sat_daily` (
  `id`       VARCHAR(20) NOT NULL,   -- Id
  `date`     DATE        NOT NULL,   -- Date
  `avg_spo2` DECIMAL(5,2),   -- Avg Spo2
  `min_spo2` DECIMAL(5,2),   -- Min Spo2
  `max_spo2` DECIMAL(5,2),   -- Max Spo2
  PRIMARY KEY (`id`,`date`),   -- 主键
  FOREIGN KEY (`id`) REFERENCES `participants` (`id`)   -- 外键约束
    ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS `skin_temp_wrist_minute`;   -- 若存在则先删除表 skin_temp_wrist_minute

/* =====================================================
 *  TABLE: skin_temp_wrist_minute
 *  Auto-generated annotations; edit freely if需要更细描述
 ===================================================== */
CREATE TABLE `skin_temp_wrist_minute` (
  `id`                    VARCHAR(20)  NOT NULL,        -- 参与者 ID   -- Id
  `ts`                    DATETIME     NOT NULL,        -- 采样时间   -- Ts
  `temperature_difference`DECIMAL(5,2),                 -- 与基线的温度差 (°C)   -- Temperature Difference Decimal(5,2),
  PRIMARY KEY (`id`,`ts`),   -- 主键
  CONSTRAINT `fk_wrist_temp_id`
      FOREIGN KEY (`id`) REFERENCES `participants`(`id`)   -- 外键约束
      ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;

DROP TABLE IF EXISTS `skin_temp_sleep_nightly`;   -- 若存在则先删除表 skin_temp_sleep_nightly

/* =====================================================
 *  TABLE: skin_temp_sleep_nightly
 *  Auto-generated annotations; edit freely if需要更细描述
 ===================================================== */
CREATE TABLE `skin_temp_sleep_nightly` (
  `id`                                       VARCHAR(20)  NOT NULL,   -- Id
  `start_sleep`                              DATETIME     NOT NULL,   -- Start Sleep
  `end_sleep`                                DATETIME     NOT NULL,   -- End Sleep
  `temperature_samples`                      INT UNSIGNED,   -- Temperature Samples
  `nightly_temperature`                      DECIMAL(5,2),   -- °C   -- Nightly Temperature
  `baseline_relative_sample_sum`             DECIMAL(10,4),   -- Baseline Relative Sample Sum
  `baseline_relative_sample_sum_of_squares`  DECIMAL(12,4),   -- Baseline Relative Sample Sum Of Squares
  `baseline_relative_nightly_standard_deviation`   DECIMAL(6,4),   -- Baseline Relative Nightly Standard Deviation
  `baseline_relative_sample_standard_deviation`    DECIMAL(6,4),   -- Baseline Relative Sample Standard Deviation
  PRIMARY KEY (`id`,`start_sleep`),               -- 一晚一行   -- 主键
  CONSTRAINT `fk_sleep_temp_id`
      FOREIGN KEY (`id`) REFERENCES `participants`(`id`)   -- 外键约束
      ON UPDATE CASCADE ON DELETE CASCADE,
  INDEX `idx_sleep_end` (`end_sleep`)             -- 便于按结束时间查询   -- 二级索引
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;


DROP TABLE IF EXISTS `heart_rate_variability`;   -- 若存在则先删除表 heart_rate_variability

/* =====================================================
 *  TABLE: heart_rate_variability
 *  Auto-generated annotations; edit freely if需要更细描述
 ===================================================== */
CREATE TABLE `heart_rate_variability` (
  `id`       VARCHAR(20) NOT NULL,   -- Id
  `ts`       DATETIME    NOT NULL,   -- Ts
  `rmssd` DECIMAL(6,2),   -- Rmssd
  `nrem_hr` DECIMAL(6,2),   -- Nrem Hr
  `entropy` DECIMAL(6,2),   -- Entropy
  PRIMARY KEY (`id`,`ts`),   -- 主键
  FOREIGN KEY (`id`) REFERENCES `participants` (`id`)   -- 外键约束
    ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

/* =========  Respiratory-rate (nightly summary)  ========= */
DROP TABLE IF EXISTS `respiratory_rate`;   -- 若存在则先删除表 respiratory_rate

/* =====================================================
 *  TABLE: respiratory_rate
 *  Auto-generated annotations; edit freely if需要更细描述
 ===================================================== */
CREATE TABLE `respiratory_rate` (
  `id`                                   VARCHAR(20)  NOT NULL,   -- 参与者 ID   -- Id
  `night_end`                            DATETIME     NOT NULL,   -- CSV 中的 timestamp（睡眠段结束）   -- Night End
  
  /* ---- 整晚睡眠 ---- */
  `full_sleep_breathing_rate`            DECIMAL(4,1),   -- Full Sleep Breathing Rate
  `full_sleep_standard_deviation`        DECIMAL(4,1),   -- Full Sleep Standard Deviation
  `full_sleep_signal_to_noise`           DECIMAL(6,2),   -- Full Sleep Signal To Noise
  
  /* ---- 深睡 ---- */
  `deep_sleep_breathing_rate`            DECIMAL(4,1),   -- Deep Sleep Breathing Rate
  `deep_sleep_standard_deviation`        DECIMAL(4,1),   -- Deep Sleep Standard Deviation
  `deep_sleep_signal_to_noise`           DECIMAL(6,2),   -- Deep Sleep Signal To Noise

  /* ---- 浅睡 ---- */
  `light_sleep_breathing_rate`           DECIMAL(4,1),   -- Light Sleep Breathing Rate
  `light_sleep_standard_deviation`       DECIMAL(4,1),   -- Light Sleep Standard Deviation
  `light_sleep_signal_to_noise`          DECIMAL(6,2),   -- Light Sleep Signal To Noise

  /* ---- REM 睡 ---- */
  `rem_sleep_breathing_rate`             DECIMAL(4,1),   -- Rem Sleep Breathing Rate
  `rem_sleep_standard_deviation`         DECIMAL(4,1),   -- Rem Sleep Standard Deviation
  `rem_sleep_signal_to_noise`            DECIMAL(6,2),   -- Rem Sleep Signal To Noise
  
  PRIMARY KEY (`id`, `night_end`),   -- 主键
  CONSTRAINT `fk_resprate_id`
      FOREIGN KEY (`id`) REFERENCES `participants` (`id`)   -- 外键约束
      ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;


DROP TABLE IF EXISTS `sleep_quality`;   -- 若存在则先删除表 sleep_quality

/* =====================================================
 *  TABLE: sleep_quality
 *  Auto-generated annotations; edit freely if需要更细描述
 ===================================================== */
CREATE TABLE `sleep_quality` (
  `id`     VARCHAR(20) NOT NULL,   -- Id
  `start_time`   DATETIME        NOT NULL,   -- Start Time
  `end_time`     DATETIME        NOT NULL,   -- End Time
  'overall_score' TINYINT,
  'composition_score' TINYINT,
  'revitalization_score' TINYINT,
  'duration_score' TINYINT,
  'resting_heart_rate' TINYINT,
  `restlessness`  DECIMAL(8, 7),   -- Restlessness
  PRIMARY KEY (`id`,`start_time`),   -- 主键
  FOREIGN KEY (`id`) REFERENCES `participants` (`id`)   -- 外键约束
    ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

/* =========  Oviedo Sleep Questionnaire  ========= */
DROP TABLE IF EXISTS `OviedoSleepQuestionnaire`;   -- 若存在则先删除表 OviedoSleepQuestionnaire

/* =====================================================
 *  TABLE: OviedoSleepQuestionnaire
 *  Auto-generated annotations; edit freely if需要更细描述
 ===================================================== */
CREATE TABLE `OviedoSleepQuestionnaire` (
  `id`                                   VARCHAR(20)   NOT NULL,   -- Id
  `visit`                                TINYINT UNSIGNED NOT NULL,   -- Visit

  /* ---------- 单题得分（1–7 级别；缺失允许 NULL） ---------- */
  `1_satisfaction_sleep`                 TINYINT,   -- 1 Satisfaction Sleep
  `2_1_initiate_sleep`                   TINYINT,   -- 2 1 Initiate Sleep
  `2_2_remain_asleep`                    TINYINT,   -- 2 2 Remain Asleep
  `2_3_restorative_sleep`                TINYINT,   -- 2 3 Restorative Sleep
  `2_4_usual_waking_up`                  TINYINT,   -- 2 4 Usual Waking Up
  `2_5_excessive_somnolence`             TINYINT,   -- 2 5 Excessive Somnolence
  `3_fall_asleep`                        TINYINT,   -- 3 Fall Asleep
  `4_wake_up_night`                      TINYINT,   -- 4 Wake Up Night
  `5_wake_up_earlier`                    TINYINT,   -- 5 Wake Up Earlier

  /* ---------- 量化睡眠时长与效率 ---------- */
  `6a_hours_sleep`                       DECIMAL(4,2),   -- 每晚睡眠小时数   -- 6a Hours Sleep
  `6b_hours_bed`                         DECIMAL(4,2),   -- 每晚卧床小时数   -- 6b Hours Bed
  `6c_sleep_efficiency`                  TINYINT,        -- 1–5 等级   -- 6c Sleep Efficiency

  /* ---------- 白天主观症状 ---------- */
  `7_tiredness_not_sleep`                TINYINT,   -- 7 Tiredness Not Sleep
  `8_somnolence_days`                    TINYINT,   -- 8 Somnolence Days
  `9_somnolence_effects`                 TINYINT,   -- 9 Somnolence Effects

  /* ---------- 夜间相关症状 ---------- */
  `10a_snoring`                          TINYINT,   -- 10a Snoring
  `10b_snoring_suffocation`              TINYINT,   -- 10b Snoring Suffocation
  `10c_leg_movements`                    TINYINT,   -- 10c Leg Movements
  `10d_nightmares`                       TINYINT,   -- 10d Nightmares
  `10e_others`                           TINYINT,   -- 10e Others

  /* ---------- 其他 ---------- */
  `11_sleep_aids`                        TINYINT,   -- 11 Sleep Aids

  /* ---------- 量表总分与维度分 ---------- */
  `sleep_satisfaction_score`             TINYINT,        -- 0–7   -- Sleep Satisfaction Score
  `insomnia_score`                       SMALLINT UNSIGNED,  -- 0–36   -- Insomnia Score
  `somnolence_score`                     TINYINT,        -- 0–14   -- Somnolence Score
  `total_score`                          SMALLINT UNSIGNED,   -- Total Score

  PRIMARY KEY (`id`, `visit`),   -- 主键
  CONSTRAINT `fk_oviedo_id`
      FOREIGN KEY (`id`) REFERENCES `participants` (`id`)   -- 外键约束
      ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;



/* ---------------------------------------------------------
 * 8. DS9 – Emotional State
 * --------------------------------------------------------- */
/* =========  DASS-21（Depression Anxiety Stress Scales） ========= */
DROP TABLE IF EXISTS `emotional_dass21`;   -- 若存在则先删除表 emotional_dass21

/* =====================================================
 *  TABLE: emotional_dass21
 *  Auto-generated annotations; edit freely if需要更细描述
 ===================================================== */
CREATE TABLE `emotional_dass21` (
  `id`                      VARCHAR(20)      NOT NULL,   -- Id
  `visit`                   TINYINT UNSIGNED NOT NULL,   -- Visit

  /* ---------- 21 个题项（建议 0–3 评分，TINYINT 足够） ---------- */
  `q1_wind_down`            TINYINT,   -- Q1 Wind Down
  `q2_mouth_dryness`        TINYINT,   -- Q2 Mouth Dryness
  `q3_no_positive_feelings` TINYINT,   -- Q3 No Positive Feelings
  `q4_difficulty_breathing` TINYINT,   -- Q4 Difficulty Breathing
  `q5_no_initiative`        TINYINT,   -- Q5 No Initiative
  `q6_overreact`            TINYINT,   -- Q6 Overreact
  `q7_trembling`            TINYINT,   -- Q7 Trembling
  `q8_nervous_energy`       TINYINT,   -- Q8 Nervous Energy
  `q9_panic`                TINYINT,   -- Q9 Panic
  `q10_no_prospects`        TINYINT,   -- Q10 No Prospects
  `q11_agitation`           TINYINT,   -- Q11 Agitation
  `q12_no_relax`            TINYINT,   -- Q12 No Relax
  `q13_downhearted`         TINYINT,   -- Q13 Downhearted
  `q14_intolerance`         TINYINT,   -- Q14 Intolerance
  `q15_close_to_panic`      TINYINT,   -- Q15 Close To Panic
  `q16_no_enthusiasm`       TINYINT,   -- Q16 No Enthusiasm
  `q17_selfworth`           TINYINT,   -- Q17 Selfworth
  `q18_touchy`              TINYINT,   -- Q18 Touchy
  `q19_heart`               TINYINT,   -- Q19 Heart
  `q20_scared`              TINYINT,   -- Q20 Scared
  `q21_meaningless`         TINYINT,   -- Q21 Meaningless

  /* ---------- 3 个分量表分数 & 总分 ---------- */
  `depression_score`        SMALLINT UNSIGNED,   -- 0–42   -- Depression Score
  `stress_score`            SMALLINT UNSIGNED,   -- 0–42   -- Stress Score
  `anxiety_score`           SMALLINT UNSIGNED,   -- 0–42   -- Anxiety Score
  `total_score`             SMALLINT UNSIGNED,   -- 0–126   -- Total Score

  PRIMARY KEY (`id`, `visit`),   -- 主键
  CONSTRAINT `fk_dass21_id`
      FOREIGN KEY (`id`) REFERENCES `participants` (`id`)   -- 外键约束
      ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;


/* ========== 1. 会话元信息表 ========== */
DROP TABLE IF EXISTS `eda_sessions`;   -- 若存在则先删除表 eda_sessions

/* =====================================================
 *  TABLE: eda_sessions
 *  Auto-generated annotations; edit freely if需要更细描述
 ===================================================== */
CREATE TABLE `eda_sessions` (
  `session_id`            BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,   -- Session Id
  `id`                    VARCHAR(20)  NOT NULL,          -- 参与者 ID   -- Id
  `session_ts`            DATETIME     NOT NULL,          -- 会话开始时间   -- Session Ts

  /* 心率 & HRV */
  `average_heart_rate`    DECIMAL(5,2),   -- Average Heart Rate
  `start_heart_rate`      SMALLINT,   -- Start Heart Rate
  `end_heart_rate`        SMALLINT,   -- End Heart Rate
  `hrv_baseline`          DECIMAL(6,2),   -- Hrv Baseline

  /* 统计信息 */
  `sample_count`          INT UNSIGNED,                   -- 会话采样点数   -- Sample Count

  KEY `idx_eda_id_ts` (`id`, `session_ts`),   -- 二级索引

  CONSTRAINT `fk_eda_id`
      FOREIGN KEY (`id`) REFERENCES `participants` (`id`)   -- 外键约束
      ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;

/* ========== 2. 逐点皮电值长表 ========== */
DROP TABLE IF EXISTS `eda_levels`;   -- 若存在则先删除表 eda_levels

/* =====================================================
 *  TABLE: eda_levels
 *  Auto-generated annotations; edit freely if需要更细描述
 ===================================================== */
CREATE TABLE `eda_levels` (
  `session_id`            BIGINT UNSIGNED NOT NULL,   -- Session Id
  `sample_idx`            INT UNSIGNED    NOT NULL,      -- 从 0 开始的采样序号   -- Sample Idx
  `level_microsiemens`    DECIMAL(8,3),                  -- 皮电电导 (µS)   -- Level Microsiemens

  PRIMARY KEY (`session_id`, `sample_idx`),   -- 主键

  CONSTRAINT `fk_eda_levels_session`
      FOREIGN KEY (`session_id`) REFERENCES `eda_sessions` (`session_id`)   -- 外键约束
      ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;


/* =========  Daily Stress Composite Score ========= */
DROP TABLE IF EXISTS `stress_daily_scores`;   -- 若存在则先删除表 stress_daily_scores

/* =====================================================
 *  TABLE: stress_daily_scores
 *  Auto-generated annotations; edit freely if需要更细描述
 ===================================================== */
CREATE TABLE `stress_daily_scores` (
  `id`                       VARCHAR(20)   NOT NULL,  -- 参与者 ID   -- Id
  `day`                      DATE          NOT NULL,  -- 由 timestamp 取日期   -- Day

  `stress_score`             SMALLINT UNSIGNED,   -- Stress Score
  `sleep_points`             SMALLINT,   -- Sleep Points
  `responsiveness_points`    SMALLINT,   -- Responsiveness Points
  `exertion_points`          SMALLINT,   -- Exertion Points

  PRIMARY KEY (`id`, `day`),   -- 主键
  CONSTRAINT `fk_stress_id`
      FOREIGN KEY (`id`) REFERENCES `participants` (`id`)   -- 外键约束
      ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;

/* ---------------------------------------------------------
 * 9. DS10 – Additional Information (SUS)
 * --------------------------------------------------------- */
/* =========  System Usability Scale (SUS) ========= */
DROP TABLE IF EXISTS `sus_scores`;   -- 若存在则先删除表 sus_scores

/* =====================================================
 *  TABLE: sus_scores
 *  Auto-generated annotations; edit freely if需要更细描述
 ===================================================== */
CREATE TABLE `sus_scores` (
  `id`                     VARCHAR(20)      NOT NULL,         -- 参与者 ID   -- Id
  `visit`                  TINYINT UNSIGNED NOT NULL,         -- 第几次随访   -- Visit

  /* ---------- 10 个题项 原样列名 ---------- */
  `q1_like_to_use`         TINYINT,                           -- 1_like_to_use   -- Q1 Like To Use
  `q2_complex`             TINYINT,                           -- 2_complex   -- Q2 Complex
  `q3_easy_to_use`         TINYINT,                           -- 3_easy_to_use   -- Q3 Easy To Use
  `q4_need_support`        TINYINT,                           -- 4_technical_support   -- Q4 Need Support
  `q5_well_integrated`     TINYINT,                           -- 5_well_integrated   -- Q5 Well Integrated
  `q6_inconsistent`        TINYINT,                           -- 6_inconsistency   -- Q6 Inconsistent
  `q7_quick_to_learn`      TINYINT,                           -- 7_quick_to_learn   -- Q7 Quick To Learn
  `q8_cumbersome`          TINYINT,                           -- 8_cumbersome   -- Q8 Cumbersome
  `q9_confident`           TINYINT,                           -- 9_confident   -- Q9 Confident
  `q10_need_to_learn`      TINYINT,                           -- 10_need_to_learn   -- Q10 Need To Learn

  /* ---------- 计算列 ---------- */
  `positive_score`         SMALLINT,                          -- 正向项加总×2.5   -- Positive Score
  `negative_score`         SMALLINT,                          -- 反向项处理后×2.5   -- Negative Score
  `sum_raw`                SMALLINT,                          -- CSV 列 “sum”   -- Sum Raw
  `total_score`            SMALLINT,                          -- 0–100   -- Total Score

  PRIMARY KEY (`id`, `visit`),   -- 主键
  CONSTRAINT `fk_sus_id`
      FOREIGN KEY (`id`) REFERENCES `participants` (`id`)   -- 外键约束
      ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;


/* ============  End of schema.sql  ============ */
