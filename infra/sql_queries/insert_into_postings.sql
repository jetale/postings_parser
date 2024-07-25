CREATE OR REPLACE FUNCTION insert_into_posting(
    p_job_title VARCHAR,
    p_company VARCHAR,
    p_work_location VARCHAR,
    p_posting_date DATE,
    p_posting_url VARCHAR,
    p_parsed_date DATE,
    p_parsed_time TIME
)
RETURNS VOID AS $$
BEGIN
    INSERT INTO postings (
        job_title,
        company,
        work_location,
        posting_date,
        posting_url,
        parsed_date,
        parsed_time
    ) VALUES (
        p_job_title,
        p_company,
        p_work_location,
        p_posting_date,
        p_posting_url,
        p_parsed_date,
        p_parsed_time
    )
    ON CONFLICT (posting_url) DO NOTHING;
END;
$$ LANGUAGE plpgsql;
