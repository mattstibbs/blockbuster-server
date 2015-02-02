BEGIN;

-- Create the v_cardetails view
CREATE OR REPLACE VIEW public.v_cardetails AS
select r.registration, COALESCE(u.firstname, r.firstname) as firstname, COALESCE(u.surname, r.surname) as surname, COALESCE(u.mobile, r.mobile) as mobile from registrations r
left join users u on r.user_id = u.user_id;;
ALTER TABLE public.v_cardetails
  OWNER TO blockbuster;

-- Update schema version to 1.25.00
UPDATE general
SET value = '1.25.00'
WHERE key = 'version';

COMMIT;