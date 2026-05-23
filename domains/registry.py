from typing import Dict, List

from app_config import TYPE_COMPATIBLE_DIRT
from core.models import ColumnSpec, DomainSpec


def c(name: str, definition: str, data_type: str, role: str = "feature") -> ColumnSpec:
    return ColumnSpec(
        name=name,
        definition=definition,
        data_type=data_type,
        role=role,
        allowed_dirt=TYPE_COMPATIBLE_DIRT.get(data_type, []),
    )


COMMON_DASHBOARD_GUIDANCE = [
    "Create a data quality summary before building visuals.",
    "Use slicers for the most important categorical fields.",
    "Build one trend visual if a timestamp or date field is available.",
    "Compare at least one numeric measure across two categorical dimensions.",
]


def standard_questions(topic: str) -> List[str]:
    return [
        f"Should the {topic} dataset include strong seasonal or time-based patterns?",
        f"Should the {topic} dataset include realistic regional or location-based differences?",
        f"Should the {topic} dataset include outliers that create useful cleaning and analysis practice?",
        f"Should the {topic} dataset include business-rule relationships between columns?",
        f"Should the {topic} dataset include repeated entities such as customers, products, users, assets, or locations?",
    ]


def domain(key: str, name: str, description: str, columns: List[ColumnSpec], questions: List[str] = None, dashboard_guidance: List[str] = None, recommended_min_columns: int = 10) -> DomainSpec:
    return DomainSpec(
        key=key,
        name=name,
        description=description,
        columns=columns,
        questions=questions or standard_questions(name.lower()),
        dashboard_guidance=dashboard_guidance or COMMON_DASHBOARD_GUIDANCE,
        recommended_min_columns=recommended_min_columns,
    )


DOMAIN_SPECS: Dict[str, DomainSpec] = {}


def register(spec: DomainSpec) -> None:
    DOMAIN_SPECS[spec.key] = spec


register(domain(
    "ecommerce_retail",
    "E-Commerce & Retail Transactions",
    "Transaction-level retail dataset for sales, returns, discounts, delivery, customers, and product performance.",
    [
        c("transaction_id", "Unique identifier for each transaction.", "ID"),
        c("order_timestamp", "Date and time when the order was placed.", "DateTime"),
        c("customer_id", "Synthetic customer identifier.", "ID"),
        c("customer_segment", "Customer segment such as new, returning, premium, or wholesale.", "Categorical"),
        c("product_id", "Synthetic product identifier.", "ID"),
        c("product_category", "Main product category sold.", "Categorical"),
        c("product_subcategory", "Detailed product subcategory.", "Categorical"),
        c("city", "Customer or delivery city.", "Categorical"),
        c("sales_channel", "Channel used for the sale, such as online, store, marketplace, or mobile app.", "Categorical"),
        c("payment_method", "Payment method used by customer.", "Categorical"),
        c("quantity", "Number of units purchased.", "Number"),
        c("unit_price", "Price per unit before discount.", "Accounting"),
        c("discount_percent", "Discount rate applied to the order.", "Percent"),
        c("gross_sales_amount", "Sales amount before discounts and returns.", "Accounting"),
        c("net_sales_amount", "Sales amount after discount and returns.", "Accounting"),
        c("delivery_charges", "Delivery or shipping fee charged to customer.", "Accounting"),
        c("return_flag", "Whether the order was returned.", "Binary"),
        c("delivery_status", "Delivery status such as delivered, delayed, cancelled, or returned.", "Categorical"),
        c("rating", "Customer rating after purchase.", "Decimal"),
        c("campaign_name", "Marketing campaign associated with the transaction.", "Text"),
        c("coupon_code", "Coupon or promotional code used.", "Text"),
        c("warehouse_region", "Warehouse or fulfillment region.", "Categorical"),
        c("profit_margin_percent", "Estimated profit margin percentage.", "Percent"),
        c("loyalty_member_flag", "Whether customer belongs to loyalty program.", "Binary"),
        c("refund_amount", "Refund amount if returned.", "Accounting"),
    ],
    questions=[
        "Should the dataset include returned orders?",
        "Should discounts affect net sales and profit margin?",
        "Should some customers make repeat purchases?",
        "Should sales have seasonal peaks?",
        "Should delivery delays vary by city or warehouse region?",
        "Should product categories have different profitability patterns?",
    ],
    dashboard_guidance=[
        "Create revenue trend by order timestamp.",
        "Compare net sales, gross sales, and return rate by product category.",
        "Analyze city-wise and channel-wise sales performance.",
        "Build a discount impact visual comparing discount percentage with net sales and profit margin.",
        "Add slicers for city, sales channel, product category, and payment method.",
    ],
))

register(domain(
    "supply_chain_logistics",
    "Supply Chain & Logistics",
    "Shipment, supplier, warehouse, inventory, delivery, and logistics performance data.",
    [
        c("shipment_id", "Unique shipment identifier.", "ID"), c("order_id", "Associated order identifier.", "ID"), c("shipment_timestamp", "Shipment creation timestamp.", "DateTime"), c("supplier_id", "Supplier identifier.", "ID"), c("supplier_region", "Supplier region.", "Categorical"), c("warehouse_id", "Warehouse identifier.", "ID"), c("warehouse_city", "Warehouse city.", "Categorical"), c("destination_city", "Destination city.", "Categorical"), c("transport_mode", "Transport mode such as road, rail, air, or sea.", "Categorical"), c("carrier_name", "Carrier or logistics partner.", "Categorical"), c("product_category", "Product category shipped.", "Categorical"), c("shipment_weight_kg", "Shipment weight in kilograms.", "Decimal"), c("shipment_volume_cbm", "Shipment volume in cubic meters.", "Decimal"), c("freight_cost", "Freight cost for shipment.", "Accounting"), c("expected_delivery_date", "Expected delivery date.", "Date"), c("actual_delivery_date", "Actual delivery date.", "Date"), c("delay_hours", "Delivery delay in hours.", "Decimal"), c("damage_flag", "Whether shipment was damaged.", "Binary"), c("inventory_level", "Warehouse inventory level.", "Number"), c("reorder_point", "Inventory reorder point.", "Number"), c("stockout_flag", "Whether stockout occurred.", "Binary"), c("customs_hold_flag", "Whether shipment was held by customs.", "Binary"), c("temperature_control_flag", "Whether temperature-controlled handling was required.", "Binary"), c("route_distance_km", "Estimated route distance.", "Decimal"), c("delivery_status", "Final delivery status.", "Categorical")
    ],
))

register(domain(
    "real_estate_property",
    "Real Estate & Property Markets",
    "Property listings, valuations, rents, locations, and market behavior.",
    [
        c("property_id", "Unique property identifier.", "ID"), c("listing_timestamp", "Listing creation timestamp.", "DateTime"), c("property_type", "Type of property.", "Categorical"), c("city", "City where property is located.", "Categorical"), c("area_name", "Local neighborhood or area.", "Categorical"), c("latitude", "Latitude coordinate.", "Geographic"), c("longitude", "Longitude coordinate.", "Geographic"), c("bedrooms", "Number of bedrooms.", "Number"), c("bathrooms", "Number of bathrooms.", "Number"), c("covered_area_sqft", "Covered area in square feet.", "Decimal"), c("plot_area_sqft", "Plot area in square feet.", "Decimal"), c("asking_price", "Listing asking price.", "Accounting"), c("estimated_market_value", "Estimated market value.", "Accounting"), c("monthly_rent", "Expected monthly rent.", "Accounting"), c("price_per_sqft", "Price per square foot.", "Accounting"), c("property_age_years", "Age of property in years.", "Number"), c("furnished_status", "Furnished, semi-furnished, or unfurnished.", "Categorical"), c("parking_available_flag", "Whether parking is available.", "Binary"), c("floor_number", "Floor number.", "Number"), c("total_floors", "Total floors in building.", "Number"), c("developer_name", "Developer or builder name.", "Text"), c("listing_source", "Listing source platform.", "Categorical"), c("days_on_market", "Days property has been listed.", "Number"), c("negotiation_margin_percent", "Estimated negotiation margin.", "Percent"), c("sale_status", "Listing status.", "Categorical")
    ],
))

register(domain(
    "corporate_finance_stock_market",
    "Corporate Financial Statements & Stock Market Data",
    "Corporate finance, financial statement line items, stock market observations, and valuation metrics.",
    [
        c("record_id", "Unique financial record identifier.", "ID"), c("reporting_timestamp", "Reporting or market timestamp.", "DateTime"), c("company_id", "Company identifier.", "ID"), c("company_name", "Synthetic company name.", "Text"), c("sector", "Business sector.", "Categorical"), c("exchange", "Stock exchange.", "Categorical"), c("ticker", "Synthetic ticker symbol.", "ID"), c("revenue", "Revenue for reporting period.", "Accounting"), c("cost_of_sales", "Cost of sales.", "Accounting"), c("gross_profit", "Gross profit.", "Accounting"), c("operating_expense", "Operating expense.", "Accounting"), c("net_income", "Net income.", "Accounting"), c("total_assets", "Total assets.", "Accounting"), c("total_liabilities", "Total liabilities.", "Accounting"), c("shareholders_equity", "Shareholders equity.", "Accounting"), c("closing_price", "Closing stock price.", "Accounting"), c("trading_volume", "Trading volume.", "Number"), c("market_cap", "Market capitalization.", "Accounting"), c("earnings_per_share", "Earnings per share.", "Decimal"), c("dividend_yield", "Dividend yield.", "Percent"), c("debt_to_equity_ratio", "Debt-to-equity ratio.", "Decimal"), c("gross_margin_percent", "Gross margin percentage.", "Percent"), c("net_margin_percent", "Net margin percentage.", "Percent"), c("analyst_rating", "Analyst rating category.", "Categorical"), c("audit_flag", "Whether record is marked for review.", "Binary")
    ],
))

register(domain(
    "banking_credit_scoring",
    "Banking & Credit Scoring",
    "Loan applications, creditworthiness, approval behavior, repayment risk, and banking customer attributes.",
    [
        c("application_id", "Unique loan application identifier.", "ID"), c("application_timestamp", "Application submission timestamp.", "DateTime"), c("customer_id", "Synthetic banking customer identifier.", "ID"), c("branch_city", "Branch city.", "Categorical"), c("customer_age", "Applicant age.", "Number"), c("employment_type", "Employment type.", "Categorical"), c("monthly_income", "Applicant monthly income.", "Accounting"), c("existing_debt_amount", "Existing debt amount.", "Accounting"), c("credit_score", "Synthetic credit score.", "Number"), c("loan_amount", "Requested loan amount.", "Accounting"), c("loan_purpose", "Purpose of loan.", "Categorical"), c("loan_tenure_months", "Requested tenure in months.", "Number"), c("interest_rate_percent", "Interest rate percentage.", "Percent"), c("debt_to_income_ratio", "Debt-to-income ratio.", "Percent"), c("collateral_value", "Collateral value.", "Accounting"), c("kyc_complete_flag", "Whether KYC is complete.", "Binary"), c("approval_status", "Approved, rejected, pending, or manual review.", "Categorical"), c("default_risk_band", "Risk band classification.", "Categorical"), c("default_flag", "Whether the loan defaulted.", "Binary"), c("late_payment_count", "Count of late payments.", "Number"), c("account_age_months", "Banking relationship age.", "Number"), c("product_type", "Banking product type.", "Categorical"), c("relationship_manager", "Relationship manager name.", "Text"), c("region", "Banking region.", "Categorical"), c("fraud_review_flag", "Whether application is flagged for fraud review.", "Binary")
    ],
    questions=[
        "Should credit score strongly affect approval probability?",
        "Should income and debt-to-income ratio affect default risk?",
        "Should some applications have missing KYC information?",
        "Should late payment history influence risk band?",
        "Should loan purpose affect approval behavior?",
        "Should branch region show different approval patterns?",
    ],
))

# Helper lists for remaining domains.
remaining_domains = [
    ("customer_churn_marketing", "Customer Churn & Marketing Responses", "Customer subscriptions, marketing channels, campaign response, retention, and churn behavior."),
    ("automotive_insurance", "Automotive Specifications & Insurance Risk", "Vehicle specifications, driver profile, insurance premium, claim risk, and policy behavior."),
    ("weather_meteorology", "Weather & Meteorology", "Weather station observations with temperature, humidity, rainfall, wind, and atmospheric pressure."),
    ("air_quality_pollution", "Air Quality & Pollution", "Pollution readings, air quality index, station location, weather interaction, and health advisory data."),
    ("geospatial_satellite", "Geospatial & Satellite Data", "Location, satellite-derived indicators, land cover, elevation, vegetation, and spatial observations."),
    ("astronomy_space_metrics", "Astronomical Observations & Space Metrics", "Astronomical observations, celestial object metrics, telescope readings, and space measurements."),
    ("agriculture_soil_yields", "Agricultural Yields & Soil Composition", "Crop yield, soil chemistry, rainfall, fertilizer, farm location, and production performance."),
    ("renewable_energy", "Renewable Energy Production", "Solar, wind, hydro, and renewable generation metrics with weather and plant performance."),
    ("clinical_patient_records", "Clinical Patient Records", "Synthetic patient encounters, vitals, treatments, outcomes, and clinical measurements."),
    ("fitness_wearables", "Fitness & Wearable Biometrics", "Wearable device metrics, activity, heart rate, sleep, calories, and user behavior."),
    ("public_health_nutrition", "Public Health & Nutrition", "Population health, nutrition intake, public health indicators, risk factors, and survey data."),
    ("demographics_census", "Demographics & Census Data", "Synthetic census-style population, household, geography, income, education, and employment data."),
    ("sports_statistics", "Sports Player Statistics & Match Results", "Sports player performance, match results, teams, venues, and season statistics."),
    ("psychological_surveys", "Psychological & Behavioral Surveys", "Survey responses, psychometric scales, behavioral indicators, and respondent segments."),
    ("streaming_catalogues", "Streaming Platform Catalogues", "Streaming content catalogue, views, ratings, genres, subscribers, and engagement data."),
    ("video_game_metrics", "Video Game Metrics & Sales", "Game sales, platform metrics, ratings, genres, engagement, and monetization data."),
    ("travel_hospitality_reviews", "Travel Reviews & Hospitality Ratings", "Hotel, travel, hospitality, booking, rating, and guest review behavior."),
    ("crime_urban_safety", "Crime Records & Urban Safety", "Crime incidents, city zones, safety scores, police response, and urban risk data."),
    ("student_performance", "Student Performance & Education Systems", "Student attendance, assessments, demographics, grades, and education performance data."),
    ("political_elections_polling", "Political Elections & Polling Data", "Synthetic election results, polling responses, regions, turnout, and voter segments."),
    ("public_transit_ridesharing", "Public Transit & Ride-Sharing Trips", "Trips, stations, routes, fares, vehicles, riders, and transit/rideshare performance."),
    ("electric_vehicle_population", "Electric Vehicle Populations", "EV registrations, battery specs, charging behavior, geography, and adoption trends."),
    ("flight_delays_aviation", "Flight Delays & Aviation Logistics", "Flight schedules, delays, airlines, airports, weather, aircraft, and operations data."),
    ("smart_city_iot", "Smart City IoT Sensor Streams", "IoT sensor readings, city infrastructure, device status, and time-series urban signals."),
    ("traffic_accidents", "Traffic Flow & Accident Records", "Traffic flow, speed, accidents, road conditions, weather, location, and congestion data."),
    ("sequential_timeseries", "Sequential Time-Series", "Generic sequential observations for time-series analysis, trends, seasonality, anomalies, and forecasting practice."),
    ("relational_multitable", "Relational Multi-Table Databases", "Multi-table relational CSV package for Power BI relationship modeling practice."),
]

base_columns = [
    c("record_id", "Unique row-level record identifier.", "ID"),
    c("event_timestamp", "Primary event timestamp for time-series and trend analysis.", "DateTime"),
    c("entity_id", "Synthetic entity identifier such as customer, asset, station, user, or observation unit.", "ID"),
    c("entity_name", "Synthetic entity display name.", "Text"),
    c("category", "Primary category for segmentation.", "Categorical"),
    c("subcategory", "Secondary category for deeper analysis.", "Categorical"),
    c("city", "City associated with the record.", "Categorical"),
    c("region", "Region associated with the record.", "Categorical"),
    c("latitude", "Latitude coordinate.", "Geographic"),
    c("longitude", "Longitude coordinate.", "Geographic"),
    c("numeric_measure_1", "Primary numeric measure for analysis.", "Decimal"),
    c("numeric_measure_2", "Secondary numeric measure for comparison.", "Decimal"),
    c("amount_value", "Financial or value-based amount.", "Accounting"),
    c("rate_percent", "Rate, ratio, or percentage measure.", "Percent"),
    c("score", "Score or index value.", "Number"),
    c("status", "Operational or classification status.", "Categorical"),
    c("risk_band", "Low, medium, high, or critical risk band.", "Categorical"),
    c("flag", "Binary indicator for selected behavior or outcome.", "Binary"),
    c("source_system", "Synthetic source system or data source.", "Categorical"),
    c("operator_name", "Synthetic operator, owner, or handler name.", "Text"),
    c("duration_minutes", "Duration in minutes.", "Decimal"),
    c("distance_km", "Distance in kilometers.", "Decimal"),
    c("quality_rating", "Rating or quality indicator.", "Decimal"),
    c("notes", "Short free-text note or description.", "Text"),
    c("review_required_flag", "Whether this record needs review.", "Binary"),
]

for key, name, desc in remaining_domains:
    cols = [ColumnSpec(**vars(col)) for col in base_columns]
    # Domain-specific refinements by appending and trimming to keep 25 strong candidate columns.
    if key == "weather_meteorology":
        cols = [
            c("station_id", "Weather station identifier.", "ID"), c("observation_timestamp", "Weather observation timestamp.", "DateTime"), c("station_city", "Weather station city.", "Categorical"), c("latitude", "Station latitude.", "Geographic"), c("longitude", "Station longitude.", "Geographic"), c("temperature_celsius", "Temperature in Celsius.", "Decimal"), c("humidity_percent", "Relative humidity percentage.", "Percent"), c("rainfall_mm", "Rainfall in millimeters.", "Decimal"), c("wind_speed_kph", "Wind speed in kilometers per hour.", "Decimal"), c("wind_direction", "Wind direction category.", "Categorical"), c("pressure_hpa", "Atmospheric pressure.", "Decimal"), c("visibility_km", "Visibility distance.", "Decimal"), c("cloud_cover_percent", "Cloud cover percentage.", "Percent"), c("weather_condition", "Weather condition category.", "Categorical"), c("heat_index", "Calculated heat index.", "Decimal"), c("dew_point_celsius", "Dew point temperature.", "Decimal"), c("uv_index", "UV index.", "Decimal"), c("storm_flag", "Whether storm condition was observed.", "Binary"), c("sensor_quality_score", "Sensor reading quality score.", "Number"), c("data_source", "Source of weather reading.", "Categorical"), c("region", "Weather region.", "Categorical"), c("altitude_meters", "Station altitude.", "Decimal"), c("forecast_error", "Difference between forecast and actual observation.", "Decimal"), c("alert_level", "Weather alert level.", "Categorical"), c("review_required_flag", "Whether observation needs review.", "Binary")
        ]
    elif key == "flight_delays_aviation":
        cols = [
            c("flight_id", "Unique flight identifier.", "ID"), c("scheduled_departure_timestamp", "Scheduled departure timestamp.", "DateTime"), c("actual_departure_timestamp", "Actual departure timestamp.", "DateTime"), c("airline", "Airline name.", "Categorical"), c("flight_number", "Flight number.", "ID"), c("origin_airport", "Origin airport code.", "Categorical"), c("destination_airport", "Destination airport code.", "Categorical"), c("aircraft_type", "Aircraft type.", "Categorical"), c("route_distance_km", "Route distance.", "Decimal"), c("passenger_count", "Passenger count.", "Number"), c("ticket_revenue", "Estimated ticket revenue.", "Accounting"), c("delay_minutes", "Departure delay in minutes.", "Decimal"), c("cancellation_flag", "Whether flight was cancelled.", "Binary"), c("weather_condition", "Weather condition.", "Categorical"), c("airport_congestion_level", "Airport congestion category.", "Categorical"), c("gate_number", "Gate number or code.", "Text"), c("baggage_delay_flag", "Whether baggage was delayed.", "Binary"), c("crew_delay_flag", "Whether crew delay occurred.", "Binary"), c("maintenance_flag", "Whether maintenance issue occurred.", "Binary"), c("load_factor_percent", "Flight load factor.", "Percent"), c("fuel_cost", "Estimated fuel cost.", "Accounting"), c("delay_reason", "Primary delay reason.", "Categorical"), c("region", "Route region.", "Categorical"), c("customer_satisfaction_score", "Passenger satisfaction score.", "Number"), c("review_required_flag", "Whether flight record needs review.", "Binary")
        ]
    elif key == "traffic_accidents":
        cols = [
            c("incident_id", "Unique traffic incident identifier.", "ID"), c("event_timestamp", "Traffic event timestamp.", "DateTime"), c("sensor_id", "Road sensor identifier.", "ID"), c("city", "City.", "Categorical"), c("road_name", "Road or corridor name.", "Text"), c("road_type", "Road type.", "Categorical"), c("latitude", "Incident latitude.", "Geographic"), c("longitude", "Incident longitude.", "Geographic"), c("vehicle_count", "Vehicle count.", "Number"), c("average_speed_kph", "Average speed.", "Decimal"), c("congestion_level", "Congestion level.", "Categorical"), c("accident_flag", "Whether accident occurred.", "Binary"), c("accident_severity", "Accident severity.", "Categorical"), c("weather_condition", "Weather condition.", "Categorical"), c("visibility_km", "Visibility.", "Decimal"), c("road_surface", "Road surface condition.", "Categorical"), c("response_time_minutes", "Emergency response time.", "Decimal"), c("injury_count", "Number of injuries.", "Number"), c("fatality_count", "Number of fatalities.", "Number"), c("traffic_signal_status", "Signal status.", "Categorical"), c("camera_available_flag", "Whether traffic camera exists.", "Binary"), c("public_holiday_flag", "Whether date was public holiday.", "Binary"), c("peak_hour_flag", "Whether event occurred in peak hour.", "Binary"), c("estimated_delay_minutes", "Estimated traffic delay.", "Decimal"), c("review_required_flag", "Whether incident needs review.", "Binary")
        ]
    elif key == "student_performance":
        cols = [
            c("student_id", "Synthetic student identifier.", "ID"), c("record_timestamp", "Assessment or record timestamp.", "DateTime"), c("campus", "Campus or learning center.", "Categorical"), c("program", "Academic program.", "Categorical"), c("course_name", "Course name.", "Text"), c("instructor_name", "Instructor name.", "Text"), c("attendance_percent", "Attendance percentage.", "Percent"), c("assignment_score", "Assignment score.", "Number"), c("quiz_score", "Quiz score.", "Number"), c("midterm_score", "Midterm score.", "Number"), c("final_exam_score", "Final exam score.", "Number"), c("overall_score", "Overall score.", "Number"), c("grade", "Grade category.", "Categorical"), c("study_hours_per_week", "Study hours per week.", "Decimal"), c("lms_login_count", "LMS login count.", "Number"), c("scholarship_flag", "Whether student has scholarship.", "Binary"), c("dropout_risk_band", "Dropout risk band.", "Categorical"), c("city", "Student city.", "Categorical"), c("age", "Student age.", "Number"), c("gender_group", "Synthetic demographic grouping for analysis.", "Categorical"), c("guardian_contact_available_flag", "Whether guardian contact is available.", "Binary"), c("fee_paid_percent", "Fee payment percentage.", "Percent"), c("placement_status", "Placement status.", "Categorical"), c("feedback_rating", "Feedback rating.", "Decimal"), c("review_required_flag", "Whether record needs review.", "Binary")
        ]
    elif key == "relational_multitable":
        cols = [
            c("customer_id", "Customer dimension key.", "ID"), c("product_id", "Product dimension key.", "ID"), c("order_id", "Order header key.", "ID"), c("order_item_id", "Order line key.", "ID"), c("payment_id", "Payment key.", "ID"), c("order_timestamp", "Order timestamp.", "DateTime"), c("customer_segment", "Customer segment.", "Categorical"), c("customer_city", "Customer city.", "Categorical"), c("product_category", "Product category.", "Categorical"), c("product_subcategory", "Product subcategory.", "Categorical"), c("quantity", "Quantity purchased.", "Number"), c("unit_price", "Unit price.", "Accounting"), c("discount_percent", "Discount percentage.", "Percent"), c("line_total", "Order line total.", "Accounting"), c("payment_method", "Payment method.", "Categorical"), c("payment_status", "Payment status.", "Categorical"), c("delivery_status", "Delivery status.", "Categorical"), c("return_flag", "Return flag.", "Binary"), c("supplier_id", "Supplier dimension key.", "ID"), c("warehouse_id", "Warehouse dimension key.", "ID"), c("region", "Operating region.", "Categorical"), c("loyalty_member_flag", "Loyalty member flag.", "Binary"), c("rating", "Customer rating.", "Decimal"), c("campaign_name", "Marketing campaign.", "Text"), c("review_required_flag", "Review flag.", "Binary")
        ]
    register(domain(key, name, desc, cols[:25]))


def get_domain(key: str) -> DomainSpec:
    return DOMAIN_SPECS[key]


def list_domains() -> List[DomainSpec]:
    return list(DOMAIN_SPECS.values())


def get_domain_names() -> List[str]:
    return [spec.name for spec in list_domains()]


def get_domain_by_name(name: str) -> DomainSpec:
    for spec in DOMAIN_SPECS.values():
        if spec.name == name:
            return spec
    raise KeyError(name)
