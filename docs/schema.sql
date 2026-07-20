-- RecoMart Feature Table Schema
-- Represents the structure if this data were stored in a data warehouse (e.g. Snowflake/Postgres)

CREATE TABLE feature_table (
    user_id INT NOT NULL,
    item_id INT NOT NULL,
    rating INT CHECK (rating BETWEEN 1 AND 5),
    timestamp BIGINT,
    rating_date TIMESTAMP,

    -- User demographic features
    age INT,
    gender VARCHAR(1),
    occupation VARCHAR(50),
    zip_code VARCHAR(10),
    gender_encoded INT,
    occupation_encoded INT,
    age_normalized FLOAT,

    -- User behavioral features
    user_activity_count INT,
    user_avg_rating FLOAT,

    -- Item behavioral features
    item_popularity INT,
    item_avg_rating FLOAT,

    PRIMARY KEY (user_id, item_id)
);

-- Indexes for faster feature retrieval during training/inference
CREATE INDEX idx_user_id ON feature_table(user_id);
CREATE INDEX idx_item_id ON feature_table(item_id);