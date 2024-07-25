CREATE OR REPLACE FUNCTION insert_into_posting_new(
    p_job_title VARCHAR,
    p_company VARCHAR,
    p_work_location VARCHAR,
    p_workplace_type VARCHAR,
    p_parsed_date DATE,
    p_parsed_time TIME,
    p_posting_url VARCHAR,
    p_posting_date DATE,
    p_commitment VARCHAR
)
RETURNS VOID AS $$
BEGIN
    INSERT INTO postings_new(
        job_title,
        company,
        work_location,
        workplace_type,
        parsed_date,
        parsed_time,
        posting_url,
        posting_date,
        commitment
    ) VALUES (
        p_job_title,
        p_company,
        p_work_location,
        p_workplace_type,
        p_parsed_date,
        p_parsed_time,
        p_posting_url,
        p_posting_date,
        p_commitment
    )ON CONFLICT (posting_url) DO NOTHING;
END;
$$ LANGUAGE plpgsql;
