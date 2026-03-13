-- PostgreSQL tables for homework questions 4-6

-- Q4: Tumbling window by pickup location
CREATE TABLE IF NOT EXISTS tumbling_pickup (
    window_start TIMESTAMP,
    PULocationID INTEGER,
    num_trips BIGINT,
    PRIMARY KEY (window_start, PULocationID)
);

-- Q5: Session window by pickup location
CREATE TABLE IF NOT EXISTS session_pickup (
    window_start TIMESTAMP,
    window_end TIMESTAMP,
    PULocationID INTEGER,
    num_trips BIGINT
);

-- Q6: Tumbling window tip amount
CREATE TABLE IF NOT EXISTS hourly_tips (
    window_start TIMESTAMP,
    total_tips DOUBLE PRECISION,
    PRIMARY KEY (window_start)
);
