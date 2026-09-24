# INTEGRATED SMART FOOD-WASTE REDUCTION FRAMEWORK
## System Architecture, AI Predictive Engine & Phased Execution Plan
**Focus Area:** Quick Service Restaurants (QSRs) in South-East Nigeria  
**Target Chains:** Crunchies, Kilimanjaro, Chicken Republic, etc.  
**Study Locations:** Enugu, Awka, Owerri, Abakaliki, Umuahia, Onitsha, Aba  

---

## Executive Summary
This document provides the complete architectural, methodological, and technical blueprint for designing, developing, and validating an **Integrated Smart Food-Waste Reduction Framework** tailored to commercial food service operations in South-East Nigeria. 

The framework bridges physical waste quantification audits, behavioral and economic determinants, pre-trained Time-Series Foundation Models (Amazon Chronos-Bolt and Google TimesFM), and a robust Django REST Framework backend testable via an interactive Swagger UI.

---

## 1. Research Objectives & Context

### 1.1 Main Objective
To develop and validate a smart food-waste reduction framework in food service operations in South-East Nigeria.

### 1.2 Specific Objectives
1. **Objective 1 (Quantification & Characterization):** To quantify and characterize edible food waste generated at different operational stages (preparation, storage/spoilage, overproduction/buffet, and customer plate waste) of selected food service operations in the study area.
2. **Objective 2 (Determinants Analysis):** To identify the operational, technological, behavioral, and economic determinants of edible food waste in food service operations in the study area.
3. **Objective 3 (Primary AI & Modeling Focus):** To examine the effects of smart technologies, demand forecasting, inventory management, and menu engineering on edible food waste in the study area.
4. **Objective 4 (Primary Software Engineering Focus):** To develop an integrated smart food-waste reduction framework tailored to food service operations in the study area.
5. **Objective 5 (Field Validation):** To implement and evaluate the effectiveness of the proposed framework using a quasi-experimental pilot intervention across selected intervention and control branches.
6. **Objective 6 (Policy & Scaling):** To develop policy, operational, and technological guidelines for scaling smart food-waste reduction practices across the food service sector in Nigeria.

---

## 2. Research Methodology & Phased Execution Roadmap

The study adopts a **mixed-methods research design** combining quantitative waste stream measurements and machine learning analytics with qualitative operational interviews.

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                               PHASED METHODOLOGICAL ROADMAP                            │
├─────────┬─────────────────────────────────────────────────┬────────────────────────────┤
│ Phase   │ Methodological Focus                            │ Deliverables               │
├─────────┼─────────────────────────────────────────────────┼────────────────────────────┤
│ Phase 1 │ Direct physical waste quantification & weighing │ Baseline audit data        │
│         │ across shifts, days, and operational stages.    │ (kg/day, ₦/day lost).      │
├─────────┼─────────────────────────────────────────────────┼────────────────────────────┤
│ Phase 2 │ Quantitative surveys & structured interviews    │ Econometric regression &   │
│         │ with kitchen supervisors, cooks, and storemen.  │ determinant coefficients.  │
├─────────┼─────────────────────────────────────────────────┼────────────────────────────┤
│ Phase 3 │ Mathematical modeling of demand forecasting,    │ Validated Chronos/TimesFM  │
│         │ inventory FEFO rotation, and menu profitability.│ predictive models.         │
├─────────┼─────────────────────────────────────────────────┼────────────────────────────┤
│ Phase 4 │ Software engineering of the integrated backend  │ Django REST API backend    │
│         │ and interactive kitchen prep touchpoints.       │ with Swagger UI docs.      │
├─────────┼─────────────────────────────────────────────────┼────────────────────────────┤
│ Phase 5 │ Quasi-experimental pilot intervention           │ Pre- vs. post-intervention │
│         │ (Intervention branches vs. Control branches).   │ waste reduction metrics.   │
├─────────┼─────────────────────────────────────────────────┼────────────────────────────┤
│ Phase 6 │ Synthesis of findings into operational SOPs     │ Industry rollout roadmap   │
│         │ and governmental/hospitality policy briefs.     │ and policy guidelines.     │
└─────────┴─────────────────────────────────────────────────┴────────────────────────────┘
```

---

## 3. The AI Demand Forecasting Engine (Objective 3)

### 3.1 Pre-trained Foundation Models: Chronos-Bolt & Google TimesFM
Rather than training neural networks from scratch with sparse localized data, the platform utilizes two complementary Time-Series Foundation Models (TSFMs):
* **Amazon Chronos-Bolt:** Quantizes time-series values into discrete tokens using a T5 transformer architecture. Highly sensitive to sudden non-linear shifts, daily volatility, and short-term variance.
* **Google TimesFM:** A decoder-only patch transformer pre-trained on over 100 billion time-series points. Demonstrates exceptional baseline stability, long-horizon consistency, and weekly seasonality capture.

### 3.2 The South-East Nigeria Local Feature Layer
To adapt global foundation models to local Nigerian realities, the inputs are conditioned on four critical localized feature sets:
1. **Igbo Traditional Market Day Calendar:** The 4-day cycle (**Eke, Oye, Afor, Nkwo**) that governs trade and customer mobility in commercial hubs such as Onitsha, Aba, and Awka.
2. **Civil Service & Corporate Payday Windows:** Pronounced spending surges between the 25th and 31st of each month in administrative capitals like Enugu and Abakaliki.
3. **Sunday Church & Weekend Event Surges:** Substantial lunch rushes on Sundays (12:30 PM – 4:00 PM) and Saturday social/wedding catering demands.
4. **Rainy Season Weather Flags:** Afternoon tropical downpours that depress walk-in dining while spiking delivery requests.

### 3.3 The Ensemble Strategy & Disagreement-Based Batching
The models are combined into an operational ensemble:
$$\text{Final Forecast} = (0.50 \times \text{Chronos}) + (0.50 \times \text{TimesFM}) + \text{Local Context Multipliers}$$

#### Operational Innovation: Disagreement-Based Batching
* **High Model Agreement ($\Delta < 8\%$):** High demand certainty. The kitchen prepares standard bulk batches for shift opening.
* **High Model Disagreement ($\Delta \ge 8\%$):** High demand volatility. The system automatically triggers a **2-stage staggered prep schedule**:
  * **Batch 1 (Conservative):** Prepare 65% of target for lunch rush.
  * **Batch 2 (Top-up):** Prepare the remaining 35% only if noon sales match the upper trajectory.
* **Food Waste Impact:** Directly eliminates end-of-day overproduction—the primary source of edible QSR food waste.

---

## 4. Software System Architecture (Objective 4)

### 4.1 Technology Stack
* **Backend Framework:** Python 3.11+, Django 5.x, Django REST Framework (DRF)
* **API Documentation & Testing:** Swagger UI / OpenAPI 3.0 via `drf-spectacular`
* **Machine Learning Runtime:** Python-native worker executing Chronos-Bolt and Google TimesFM
* **Database:** SQLite (local development and prototyping) transitioning to PostgreSQL (pilot deployment)
* **Frontend Touchpoint Concept:** Offline-first Progressive Web App (PWA) optimized for rugged 10-inch kitchen touchscreen tablets.

### 4.2 Core Functional Modules
1. **Smart Daily Prep Calculator:** Translates predicted customer portions into exact raw ingredient weights (kg of rice, pieces of chicken, liters of oil) using standardized Recipe Bills of Materials (BOM).
2. **3-Click Rapid Waste Logger:** Enables kitchen and clearing staff to log waste events in under 10 seconds (stage, item, weight in kg, root-cause determinant), automatically converting physical mass into financial loss ($\text{₦}$).
3. **Smart Inventory & FEFO Expiry Tracking:** First-Expired, First-Out stock monitoring tracking perishable ingredients with ambient vs. chilled shelf-life alerts and power-outage risk flags.
4. **Dynamic Menu Engineering Matrix:** Evaluates dishes across profit margin and waste volume (Stars, Plowhorses, Puzzles, Dogs) to recommend portion resizing or menu pruning.
5. **Executive & Multi-Branch Analytics:** Centralized monitoring of waste cost in Naira ($\text{₦}$), forecast accuracy tracking (MAPE/RMSE), and branch benchmarking.

---

## 5. Complete Database Schema Blueprint

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                               RELATIONAL SCHEMA OVERVIEW                               │
├──────────────────────────┬──────────────────────┬──────────────────────────────────────┤
│ Table Name               │ Domain / Cluster     │ Key Fields & Purpose                 │
├──────────────────────────┼──────────────────────┼──────────────────────────────────────┤
│ RestaurantChain          │ Organization         │ id, name, hq_city                    │
│ Branch                   │ Multi-Branch         │ id, chain, name, city, is_pilot      │
│ UserProfile              │ Access & Security    │ id, user, branch, role, phone        │
│ Ingredient               │ Inventory & Raw Stock│ id, name, unit, cost_naira, shelf    │
│ MenuItem                 │ Menu Management      │ id, chain, name, category, price     │
│ RecipeBOM                │ Recipe Formulation   │ id, menu_item, ingredient, qty, loss │
│ LocalCalendarContext     │ Regional Features    │ id, date, city, market_day, payday   │
│ SalesRecord              │ Historical POS       │ id, branch, menu_item, date, qty     │
│ ForecastRun              │ Forecasting Metadata │ id, branch, target_date, status      │
│ DailyForecastItem        │ Ensemble Predictions │ id, chronos, timesfm, ensemble, prep │
│ KitchenPrepTarget        │ Daily Kitchen Sheet  │ id, ingredient, raw_kg, cooked_kg    │
│ WasteLog                 │ Direct Waste Audits  │ id, stage, weight_kg, loss_naira     │
│ MenuEngineeringSnapshot  │ Managerial Analytics │ id, sales, waste_kg, margin, category│
└──────────────────────────┴──────────────────────┴──────────────────────────────────────┘
```

### Detailed Field Specifications

#### 1. `RestaurantChain`
* `id` (UUID, Primary Key)
* `name` (CharField, max 100): e.g., "Crunchies Fried Chicken", "Kilimanjaro", "Chicken Republic"
* `headquarters_city` (CharField, max 100)
* `created_at` (DateTimeField, auto_now_add=True)

#### 2. `Branch`
* `id` (UUID, Primary Key)
* `chain` (ForeignKey -> RestaurantChain, on_delete=CASCADE)
* `name` (CharField, max 150): e.g., "Enugu Ogui Road", "Awka Aroma", "Owerri Wetheral"
* `city` (CharField, max 50): Enugu, Awka, Owerri, Abakaliki, Umuahia, Onitsha, Aba
* `state` (CharField, max 50): Enugu, Anambra, Imo, Ebonyi, Abia
* `is_pilot_intervention` (BooleanField, default=False): **Key for Phase 5 Quasi-Experiment** (True = Intervention/Treatment, False = Control)
* `has_standby_generator` (BooleanField, default=True)
* `is_active` (BooleanField, default=True)

#### 3. `UserProfile`
* `id` (UUID, Primary Key)
* `user` (OneToOneField -> Django auth.User)
* `branch` (ForeignKey -> Branch)
* `role` (CharField): `KITCHEN_COOK`, `STORE_KEEPER`, `BRANCH_MANAGER`, `RESEARCH_AUDITOR`
* `phone_number` (CharField, max 20)

#### 4. `Ingredient`
* `id` (UUID, Primary Key)
* `chain` (ForeignKey -> RestaurantChain)
* `name` (CharField, max 100): e.g., "Parboiled Rice", "Fresh Whole Chicken", "Vegetable Oil"
* `unit_of_measure` (CharField): `KG`, `GRAM`, `LITRE`, `PIECE`
* `unit_cost_naira` (DecimalField, max_digits=10, decimal_places=2)
* `shelf_life_days_chilled` (PositiveIntegerField): Days usable under active refrigeration
* `shelf_life_days_ambient` (PositiveIntegerField): Days usable under ambient temperature
* `minimum_reorder_level` (DecimalField, max_digits=10, decimal_places=2)

#### 5. `MenuItem`
* `id` (UUID, Primary Key)
* `chain` (ForeignKey -> RestaurantChain)
* `name` (CharField, max 150): e.g., "Jollof Rice Standard", "Fried Chicken 1-Piece"
* `category` (CharField): `MAIN_RICE`, `PROTEIN`, `SIDES`, `SWALLOW_SOUP`, `PASTA`
* `selling_price_naira` (DecimalField, max_digits=10, decimal_places=2)
* `is_perishable_daily` (BooleanField, default=True)

#### 6. `RecipeBOM` (Bill of Materials)
* `id` (UUID, Primary Key)
* `menu_item` (ForeignKey -> MenuItem, related_name='bom_items')
* `ingredient` (ForeignKey -> Ingredient)
* `quantity_required` (DecimalField, max_digits=10, decimal_places=4): Raw quantity per portion
* `prep_yield_loss_pct` (DecimalField, max_digits=5, decimal_places=2): Expected cooking shrinkage/loss

#### 7. `LocalCalendarContext`
* `id` (UUID, Primary Key)
* `date` (DateField)
* `city` (CharField, max 50)
* `traditional_market_day` (CharField): `NONE`, `EKE`, `OYE`, `AFOR`, `NKWO`
* `is_market_day` (BooleanField, default=False)
* `is_payday_window` (BooleanField, default=False): Active between 25th and 31st
* `is_sunday_church_surge` (BooleanField, default=False)
* `weather_flag` (CharField): `SUNNY`, `RAINY_AFTERNOON`, `HEAVY_DOWNPOUR`

#### 8. `SalesRecord`
* `id` (UUID, Primary Key)
* `branch` (ForeignKey -> Branch)
* `menu_item` (ForeignKey -> MenuItem)
* `sale_date` (DateField)
* `shift` (CharField): `MORNING_LUNCH`, `EVENING_DINNER`
* `quantity_sold` (PositiveIntegerField)
* `total_revenue_naira` (DecimalField, max_digits=12, decimal_places=2)

#### 9. `ForecastRun`
* `id` (UUID, Primary Key)
* `branch` (ForeignKey -> Branch)
* `forecast_target_date` (DateField)
* `executed_at` (DateTimeField, auto_now_add=True)
* `status` (CharField): `SUCCESS`, `PARTIAL_FALLBACK`, `FAILED`

#### 10. `DailyForecastItem`
* `id` (UUID, Primary Key)
* `forecast_run` (ForeignKey -> ForecastRun, related_name='forecast_items')
* `menu_item` (ForeignKey -> MenuItem)
* `chronos_prediction` (DecimalField, max_digits=10, decimal_places=2)
* `timesfm_prediction` (DecimalField, max_digits=10, decimal_places=2)
* `ensemble_prediction` (DecimalField, max_digits=10, decimal_places=2)
* `disagreement_score` (DecimalField, max_digits=10, decimal_places=2)
* `confidence_level` (CharField): `HIGH`, `LOW`
* `recommended_prep_strategy` (CharField): `SINGLE_BULK_BATCH`, `TWO_STAGGERED_BATCHES`
* `batch_1_portions` (PositiveIntegerField)
* `batch_2_portions` (PositiveIntegerField)

#### 11. `KitchenPrepTarget`
* `id` (UUID, Primary Key)
* `forecast_run` (ForeignKey -> ForecastRun)
* `ingredient` (ForeignKey -> Ingredient)
* `total_raw_kg_to_prep` (DecimalField, max_digits=10, decimal_places=2)
* `actual_cooked_kg` (DecimalField, max_digits=10, decimal_places=2, null=True, blank=True)
* `variance_kg` (DecimalField, max_digits=10, decimal_places=2, null=True, blank=True)

#### 12. `WasteLog`
* `id` (UUID, Primary Key)
* `branch` (ForeignKey -> Branch)
* `logged_by` (ForeignKey -> UserProfile)
* `timestamp` (DateTimeField, auto_now_add=True)
* `operational_stage` (CharField): `PREPARATION`, `STORAGE_SPOILAGE`, `OVERPRODUCTION_BUFFET`, `PLATE_WASTE`
* `menu_item` (ForeignKey -> MenuItem, null=True, blank=True)
* `ingredient` (ForeignKey -> Ingredient, null=True, blank=True)
* `weight_kg` (DecimalField, max_digits=10, decimal_places=3)
* `financial_loss_naira` (DecimalField, max_digits=12, decimal_places=2)
* `root_cause_determinant` (CharField): `POWER_OUTAGE_SPOILAGE`, `OVERCOOKED_BURNT`, `EXPIRED_IN_STORE`, `OVERPRODUCED_UNSOLD`, `CUSTOMER_LEFTOVER`, `TRIMMING_EXCESS`
* `notes` (TextField, blank=True)

#### 13. `MenuEngineeringSnapshot`
* `id` (UUID, Primary Key)
* `branch` (ForeignKey -> Branch)
* `menu_item` (ForeignKey -> MenuItem)
* `period_start` (DateField)
* `period_end` (DateField)
* `units_sold` (PositiveIntegerField)
* `waste_weight_kg` (DecimalField, max_digits=10, decimal_places=3)
* `waste_cost_naira` (DecimalField, max_digits=12, decimal_places=2)
* `profit_margin_naira` (DecimalField, max_digits=10, decimal_places=2)
* `matrix_category` (CharField): `STAR`, `PLOWHORSE`, `PUZZLE`, `DOG`
* `recommendation` (TextField)

---

## 6. Interactive Swagger UI API Specification

When the backend server runs, the following endpoints will be directly testable in the browser via Swagger UI (`/api/docs/`):

```
[AUTHENTICATION]
POST /api/v1/auth/login/                      Authenticate user & return auth token
GET  /api/v1/auth/me/                         Return active user branch & profile role

[ORGANIZATIONAL HIERARCHY]
GET  /api/v1/branches/                        List all branch locations with city filters
POST /api/v1/branches/                        Register new branch outlet

[MENU & RECIPE BILL OF MATERIALS]
GET  /api/v1/menu/items/                      List dishes with retail prices & categories
POST /api/v1/menu/items/                      Create new dish entry
GET  /api/v1/recipes/bom/                     Inspect ingredient ratios & shrinkage loss
POST /api/v1/recipes/bom/                     Define raw ingredient requirements for dish

[LOCAL SOUTH-EAST CALENDAR CONTEXT]
GET  /api/v1/calendar/today/                  Get today's market day, payday flag & weather
POST /api/v1/calendar/set-context/            Override or update local event context

[WASTE TRACKING (OBJECTIVES 1 & 2)]
POST /api/v1/waste/logs/                      Record waste event (kg, stage, cause, ₦ loss)
GET  /api/v1/waste/logs/                      List historical waste entries with filters
GET  /api/v1/waste/daily-summary/             Get real-time total waste weight & ₦ loss

[AI PREDICTION & PREP (OBJECTIVES 3 & 4)]
POST /api/v1/forecast/trigger/                Run Chronos-Bolt + TimesFM ensemble
GET  /api/v1/forecast/prep-sheet/             Fetch tomorrow's digital kitchen prep sheet

[MANAGERIAL ANALYTICS & PILOT EVALUATION]
GET  /api/v1/analytics/menu-matrix/           Fetch Star/Plowhorse/Puzzle/Dog matrix
GET  /api/v1/analytics/pilot-comparison/      Compare Intervention vs Control branches
```

---

## 7. Phased Implementation Roadmap

* **Milestone 1:** Django project initialization, database configuration, Django REST Framework setup, and Swagger UI integration.
* **Milestone 2:** Definition of core models (`Branch`, `Ingredient`, `MenuItem`, `RecipeBOM`) and verification of master data in Swagger UI.
* **Milestone 3:** Waste logging endpoint with automatic Naira valuation and the South-East Nigeria market day & payday calendar logic.
* **Milestone 4:** The Python forecasting service integrating Chronos-Bolt, TimesFM, and the kitchen prep sheet generator.
* **Milestone 5:** Field deployment to intervention branches in South-East Nigeria for the Phase 5 quasi-experimental evaluation.

