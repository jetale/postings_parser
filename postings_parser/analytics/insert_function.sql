-- #### NOTE ##### Storing just for reference. Not intended to be used
CREATE OR REPLACE FUNCTION insert_today_counts()
RETURNS void AS $$
BEGIN
    -- Insert today's date into a variable
    DECLARE
        today_date DATE := CURRENT_DATE;
    BEGIN
        -- Insert or update the row for today's date in the stats table
        INSERT INTO stats (date_stat, total_all, total_scrapy, total_selenium, added_today_scrapy, added_today_selenium, stat_time)
        SELECT
            today_date,
            (SELECT COUNT(*) FROM postings) + (SELECT COUNT(*) FROM postings_new) AS total_all,  -- total_all
            (SELECT COUNT(*) FROM postings_new WHERE parsed_date = today_date) AS total_scrapy,    -- added_today_scrapy
            (SELECT COUNT(*) FROM postings WHERE parsed_date = today_date),         -- added_today_selenium
            (SELECT COUNT(*) FROM postings_new) AS total_scrapy,
            (SELECT COUNT(*) FROM postings) AS total_selenium,
            CURRENT_TIME;  -- stat_time
    END;
END;
$$ LANGUAGE plpgsql;
