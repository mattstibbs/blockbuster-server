# Internal Modules
from messaging import bb_email_sender
import bb_dbconnector_base
import config

# External Modules
import psycopg2
import psycopg2.pool
import psycopg2.extras
import datetime
import logging
import bb_auditlogger

log = logging.getLogger('bb_log.' + __name__)

try:

    # Create the Postgres connection pool
    pg_pool = psycopg2.pool.SimpleConnectionPool(2,10,host=config.pg_host, database=config.pg_dbname,
                                                 user=config.pg_user, password=config.pg_passwd)
    log.debug("Connection to Postgres established. Connection pool created.")

except Exception, e:
    bb_auditlogger.BBAuditLoggerFactory().create().logException('app','DB_CONNECT', str(e))
    log.error("Error creating connection pool \n" + str(e))
    raise


class PostgresConnector(bb_dbconnector_base.DBConnector,
                        bb_dbconnector_base.DBAnalyticsConnector,
                        bb_dbconnector_base.DBLogsConnector,
                        bb_dbconnector_base.DBBlocksConnector,
                        bb_dbconnector_base.DBUserConnector,
                        bb_dbconnector_base.DBPushoverConnector,
                        bb_dbconnector_base.DBEmailConnector,
                        bb_dbconnector_base.DBCarsConnector):

    def __init__(self):
        # log.debug('Instantiating PostgresDBConnector instance.')
        self.mail = bb_email_sender.EmailSenderFactory().create()
        self.connect()

    def __del__(self):
        self.close()
        # log.debug('Clearing up PostgresDBConnector instance.')

    def connect(self):
        try:
            # Get a connection from the pool, if a connection cannot be made an exception will be raised.
            self.conn = pg_pool.getconn()

            # conn.cursor will return a cursor object, you can use this cursor to perform queries
            self.cursor = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

            # log.debug("Postgres connection retrieved from the connection pool.")

            self.dict_cursor = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        except Exception, e:
            self.log_exception(e)
            log.error("PG Error:" + str(e))
            raise

    def close(self):
        try:
            # Put the connection back into the pool.
            pg_pool.putconn(self.conn)
            # log.debug("Postgres connection returned to the connection pool.")

        except Exception, e:
            self.log_exception(e)
            log.error(str(e))

    def log_exception(self, errortext):
        bb_auditlogger.BBAuditLoggerFactory().create().logException('app', 'DB_ACCESS', str(errortext))

    # ========== ADD Methods ==============
    def register_new_car(self, registration, firstname, surname, mobile, location):
        log.debug("DAL -> register_new_car")
        log.debug("Registering car")

        #  Before we update any records, we check to see whether this user or car already exist in the database
        try:
            sql = "SELECT Count(*) from users " \
                  "WHERE mobile = %s " \
                  "limit 1;"
            data = (mobile,)

            self.cursor.execute(sql, data)
            row = self.cursor.fetchone()
            user_already_exists = (row[0] > 0)


            sql = "SELECT Count(*) from registrations " \
                  "WHERE registration = %s " \
                  "limit 1;"
            data = (registration,)

            self.cursor.execute(sql, data)
            row = self.cursor.fetchone()
            car_already_exists = (row[0] > 0)

        except psycopg2.DatabaseError, e:
            self.log_exception(e)
            log.error("Error checking if registration already exists \n" + str(e))
            return "Error whilst trying to register you. Please report this issue."

        # We then deal with adding or updating the user record
        if user_already_exists:
            # Update the user record first
            try:
                sql = "UPDATE users " \
                      "SET firstname = %s, surname = %s " \
                      "WHERE mobile = %s;"

                data = (firstname, surname, mobile)

                self.cursor.execute(sql, data)
                self.conn.commit()

            except psycopg2.DatabaseError, e:
                self.log_exception(e)
                log.error("Error updating user record \n" + str(e))
                return "Error whilst trying to register you. Please report this issue."

        elif not user_already_exists:
            try:
                sql = "INSERT INTO users " \
                      "(mobile, firstname, surname) " \
                      "VALUES (%s, %s, %s); " \

                data = (mobile, firstname, surname)

                self.cursor.execute(sql, data)
                self.conn.commit()

            except psycopg2.DatabaseError, e:
                self.log_exception(e)
                log.error("Error adding new user record \n" + str(e))
                return "Error whilst trying to register you. Please report this issue."

        # Lastly, we grab the user_id (which is a uuid) for the user record so that we can include it
        # in the registration of the car.
        try:
            sql = "SELECT user_id from users " \
                  "WHERE mobile = %s and firstname = %s and surname = %s;"
            data = (mobile, firstname, surname)

            self.cursor.execute(sql, data)
            row = self.cursor.fetchone()
            user_id = row[0]
            user_record_success = True

        except psycopg2.DatabaseError, e:
            self.log_exception(e)
            log.error("Error whilst trying to retrive the user_id for this user \n" + str(e))

        # Now, we check to make sure that we have a user_id (Which confirms that a user record has been successfully
        # created or updated) and exit early if not.

        if not user_id:
            message = "Error whilst trying to register you. Please report this issue."
            log.error("Registration process was aborted as user record was not updated successfully.")
            return message

        # Then we handle the registration of the car itself.
        # If the car already exists, we update the existing record with the new information...
        if car_already_exists:
            # Update the existing registration record
            try:
                sql = "UPDATE registrations " \
                      "SET firstname = %s, surname = %s, mobile = %s, location = %s, user_id = %s " \
                      "WHERE registration = %s;"
                data = (firstname, surname, mobile, location, user_id, registration)

                self.cursor.execute(sql, data)
                self.conn.commit()

                message = (str(registration) + " is now registered for " + str(firstname) + " " +
                           str(surname) + " on " + str(mobile) + ".")

                log.info(message)

                return message

            except psycopg2.DatabaseError, e:
                self.log_exception(e)
                log.error("Error updating existing registration with new information \n" + str(e))
                message = "Unable to complete registration - please report the issue."
                return message

        elif not car_already_exists:
            try:
                sql = "INSERT INTO registrations " \
                      "(registration, firstname, surname, mobile, location, user_id) " \
                      "VALUES (%s, %s, %s, %s, %s, %s); "

                data = (registration, firstname, surname, mobile, location, user_id)

                self.cursor.execute(sql, data)
                self.conn.commit()

                message = registration + " is now registered for " + firstname + " " + surname + " on " + mobile + "."
                log.info(message)
                return message

            except psycopg2.DatabaseError, e:
                self.log_exception(e)
                log.error("Error adding new registration \n" + str(e))
                message = "Unable to complete registration - please report the issue."
                return message

    def add_log_table_entry(self, process, type, action, description):
        try:
            sql = "INSERT INTO log " \
                  "(log_process, log_type, log_action, log_description) " \
                  "VALUES (%s, %s, %s, %s);"
            data = (process, type, action, description)

            self.cursor.execute(sql, data)
            self.conn.commit()

        except psycopg2.DatabaseError, e:
            self.log_exception(e)
            log.error("Error adding log entry \n" + str(e))

    def add_transaction_record(self, logparameters):
        logparameters['Timestamp'] = (datetime.datetime.now())

        if logparameters['Direction'] == "----> O":
            logparameters['Direction'] = "O"
        else:
            logparameters['Direction'] = "I"

        sql = "INSERT INTO logsms (timestamp, direction, smsservice, command, originator, recipient, " + \
            "originator_name, recipient_name, message) " + \
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);"

        log.debug(sql)

        data = (logparameters['Timestamp'], logparameters['Direction'], logparameters['SMSService'],
                logparameters['Command'], logparameters['Originator'], logparameters['Destination'],
                logparameters['OriginatorName'], logparameters['RecipientName'], logparameters['Details'])

        log.debug(data)

        try:
            self.cursor.execute(sql, data)
            self.conn.commit()
            log.debug("Wrote log record.")

        except Exception, e:
            self.log_exception(e)
            log.error("PG Error: " + str(e))

    def add_analytics_record(self, type, name, instance_name):

        sql = "INSERT INTO analytics (instance_name, timestamp, type, name) " + \
            "VALUES (%s, %s, %s, %s);"

        log.debug(sql)

        data = (instance_name, (datetime.datetime.now()), type, name)

        log.debug(data)

        try:
            self.cursor.execute(sql, data)
            self.conn.commit()
            log.debug("Wrote analytics record to Postgres")

        except Exception, e:
            self.log_exception(e)
            log.error("PG Error: " + str(e))

    # Overriding methods from DBBlocksConnector
    def add_block_record(self, block_parameters):
        block_parameters['Timestamp'] = (datetime.datetime.utcnow())

        # TODO: Include a check to ensure block record doesn't exist before adding it

        sql = "INSERT INTO blocks(timestamp_utc, blocker_mobile, blockee_mobile, blocked_reg)" + \
            "VALUES (%s, %s, %s, %s);"

        log.debug(sql)

        data = (block_parameters['Timestamp'],
                block_parameters['BlockerMobile'],
                block_parameters['BlockeeMobile'],
                block_parameters['BlockedReg'])

        log.debug(data)

        try:
            self.cursor.execute(sql, data)
            self.conn.commit()
            log.debug("Block record written to Postgres")

        except Exception, e:
            self.log_exception(e)
            log.error("PG Error: " + str(e))

    def add_move_request(self, move_request):
        move_request['Timestamp'] = (datetime.datetime.utcnow())

        # TODO: Include a check to ensure move request doesn't exist before adding it

        sql = "INSERT INTO move_requests(timestamp_utc, blocker_mobile, blockee_mobile)" + \
            "VALUES (%s, %s, %s);"

        log.debug(sql)

        data = (move_request['Timestamp'],
                move_request['BlockerMobile'],
                move_request['BlockeeMobile'])

        log.debug(data)

        try:
            self.cursor.execute(sql, data)
            self.conn.commit()
            log.debug("Move request record written to Postgres")

        except Exception, e:
            self.log_exception(e)
            log.error("PG Error: " + str(e))

        return

    # Overriding methods from DBPushoverConnector
    def add_pushover_token_for_user(self, mobile, pushover_token):

        try:
            sql = "SELECT * FROM users WHERE mobile = %s;"
            data = (mobile,)

            self.cursor.execute(sql, data)
            users = self.cursor.fetchone()
            print(str(users))

        except psycopg2.DatabaseError, e:
            self.log_exception(e)
            log.error(str(e))
            message = "Unable to update Pushover token - please raise issue."
            return message

        if users == None:
            print("Users equal NONE")
            try:
                sql = "INSERT INTO users" \
                      "(mobile, email_address, email_notifications, pushover_notifications, pushover_token, " \
                      "share_mobile, alt_contact_text) " \
                      "values(%s, %s, %s, %s, %s, %s, %s);"
                data = (mobile, None, False, True, pushover_token, True, None)

                self.cursor.execute(sql, data)
                self.conn.commit()

                log.info("User record updated with Pushover token")
                message = "Pushover token has been added to your account."

            except Exception, e:
                self.log_exception(e)
                log.error("Failed to update existing user record")
                message = "Unable to register Pushover token for your user - please raise issue."

        else:
            # Assumes that the user already has a record and tries to update that record.
            try:
                sql = "UPDATE users " \
                      "SET pushover_token = %s, pushover_notifications = TRUE " \
                      "WHERE mobile = %s;"
                data = (pushover_token, mobile)

                self.cursor.execute(sql, data)
                self.conn.commit()

                log.info("User record added")
                message = "Pushover token has been registered against your user."

            except Exception, e:
                self.log_exception(e)
                log.error("Failed to add new user record \n" + str(e))
                message = "Unable to register Pushover token for your user - please raise issue."

        return message

    def turn_push_notifications_on(self, mobile):

        try:
            sql = "SELECT user_id FROM users WHERE mobile = %s;"
            data = (mobile,)

            self.cursor.execute(sql, data)
            users = self.cursor.fetchone()
        except psycopg2.DatabaseError, e:
            self.log_exception(e)
            log.error(str(e))
            message = "Unable to update Pushover settings - please raise issue."
            return message

        if users == None:
            message = "Please add a Pushover token before trying to enable Pushover notifications."
            return message

        else:
            try:
                sql = "UPDATE users " \
                      "SET pushover_notifications = TRUE " \
                      "WHERE mobile = %s;"
                data = (mobile,)

                self.cursor.execute(sql, data)
                self.conn.commit()

                log.info("Push notifications have been turned on for " + mobile)
                message = "Push notifications have been turned on for you"

            except psycopg2.DatabaseError, e:
                self.log_exception(e)
                log.error("Failed to turn push notifications on for " + mobile + "\n" + str(e))
                message = "Unable to turn push notifications on for you - have you added a Pushover token yet? " \
                          "Please raise issue if you continue to have problems."

        return message

    def turn_push_notifications_off(self, mobile):

        try:
            sql = "SELECT user_id FROM users WHERE mobile = %s;"
            data = (mobile,)

            self.cursor.execute(sql, data)
            users = self.cursor.fetchone()

        except psycopg2.DatabaseError, e:
            self.log_exception(e)
            log.error(str(e))
            message = "Unable to update Pushover settings - please raise issue."
            return message

        if users == None:
            message = "You do not have Pushover notifications configured."
            return message

        else:
            try:
                sql = "UPDATE users " \
                      "SET pushover_notifications = FALSE " \
                      "WHERE mobile = %s;"
                data = (mobile,)

                self.cursor.execute(sql, data)
                self.conn.commit()

                log.info("Push notifications have been turned off for " + mobile)
                message = "Push notifications have been turned off for you"

            except psycopg2.DatabaseError, e:
                self.log_exception(e)
                log.error("Failed to turn push notifications off for " + mobile + "\n" + str(e))
                message = "Unable to turn push notifications off for you. " \
                          "Please raise issue."

        return message

    # =========== GET methods =============
    # Do a select from the stats_usage view in the DB and return a tuple containing the status text and error code
    def db_status_check(self):
        log.debug("DAL -> db_status_check")

        try:
            sql = "SELECT * from general " \
                  "where key = 'version';"

            self.cursor.execute(sql)
            rows = self.cursor.fetchone()
            version = "OK: " + str(rows[1])

            return version, 200

        except psycopg2.DatabaseError, e:
            self.log_exception(e)
            log.error("Error schema getting version from database.\n" + str(e))
            return "500: Database version check failed", 500

    # Do a select from the stats_usage view in the DB and return a tuple containing the status text and error code
    def db_stats_check(self):
        today = datetime.datetime(datetime.date.today().year,
                                    datetime.date.today().month,
                                    datetime.date.today().day)

        try:
            sql = "SELECT date::text, instance_name, name, count from v_stats_usage " \
                  "where date = %s " \
                  "ORDER BY instance_name, name, count desc;"

            data = (today,)

            self.dict_cursor.execute(sql, data)
            rows = self.dict_cursor.fetchall()
            return rows

        except psycopg2.DatabaseError, e:
            self.log_exception(e)
            log.error("Error getting stats from database.\n" + str(e))
            empty = {}
            return {}

    # Take a mobile number, return a list of active blocks from that number
    def get_list_of_blocks_for_blocker(self, blocker_mobile):
        today = datetime.datetime(datetime.date.today().year,
                                    datetime.date.today().month,
                                    datetime.date.today().day)

        log.debug("Using date of " + str(today))

        sql = "SELECT blocker_mobile, blockee_mobile, blocked_reg FROM blocks " + \
              "where blocker_mobile = %s and timestamp_utc > %s;"
        data = (blocker_mobile, today)

        self.cur1 = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        self.cur1.execute(sql, data)
        rows = self.cur1.fetchall()

        log.debug("Found " + str(len(rows)) + " active blocks.")

        return rows

    # Take a mobile number, return a list of active blocks against that number
    def get_list_of_blocks_for_blockee(self, blockee_mobile):
        today = datetime.datetime(datetime.date.today().year,
                                    datetime.date.today().month,
                                    datetime.date.today().day)

        log.debug("Using date of " + str(today) + " and number " + blockee_mobile)

        sql = "SELECT blocker_mobile, blockee_mobile, blocked_reg FROM blocks " + \
              "where blockee_mobile = %s and timestamp_utc > %s;"
        data = (blockee_mobile, today)

        self.cur1 = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        self.cur1.execute(sql, data)
        rows = self.cur1.fetchall()

        log.debug("Found " + str(len(rows)) + " active blocks.")

        return rows

    # Take a mobile number, get a count of blocks against that number
    def get_count_of_blocks_for_blockee(self, blockee_mobile):
        today = datetime.datetime(datetime.date.today().year,
                                  datetime.date.today().month,
                                  datetime.date.today().day)

        log.debug("Getting count of blocks for blockee " + blockee_mobile)
        count = 0

        try:
            sql = "SELECT Count(*) from blocks " \
                  "WHERE blockee_mobile = %s and timestamp_utc > %s;"
            data = (blockee_mobile, today)

            self.cursor.execute(sql, data)
            row = self.cursor.fetchone()
            count = row[0]

        except psycopg2.DatabaseError, e:
            self.log_exception(e)
            log.error("Error retrieving count of active blocks for mobile number.\n" + str(e))

        return count

    # Take a mobile number and return the Pushover user token for that user.
    def get_pushover_user_token_from_mobile(self, mobile):
        # First check that the user has an entry in the users table
        try:
            sql = "SELECT user_id FROM users WHERE mobile = %s;"
            data = (mobile,)

            self.cursor.execute(sql, data)
            users = self.cursor.fetchone()

        except psycopg2.DatabaseError, e:
            self.log_exception(e)
            log.error("Unable to retrieve user settings. \n" + str(e))
            return ""

        if users == None:
            log.debug("User does not have a Pushover token configured.")
            return ""

        try:
            sql = "SELECT pushover_token FROM users WHERE mobile = %s and pushover_notifications = TRUE;"
            data = (mobile,)

            self.cursor.execute(sql, data)
            rows = self.cursor.fetchone()

            if rows == None:
                log.debug("User does not have a Pushover token configured.")
                return ""

            else:
                for row in rows:
                    token = row
                    log.debug("Pushover token for user is: " + token)
                    return token

        except psycopg2.DatabaseError, e:
            self.log_exception(e)
            log.error(str(e))

        return ""

    # Take a mobile number and return a list of open move requests for that mobile number
    def get_open_move_requests(self, blocker_mobile):
        today = datetime.datetime(datetime.date.today().year,
                            datetime.date.today().month,
                            datetime.date.today().day)
        log.debug('Blocker mobile is ' + blocker_mobile)
        try:
            sql = "SELECT * from move_requests " \
                  "WHERE blocker_mobile = %s and timestamp_utc > %s;"
            data = (blocker_mobile, today)

            self.cursor.execute(sql, data)
            rows = self.cursor.fetchall()
            log.debug("Open move requests are: \n" + str(rows))

        except psycopg2.DatabaseError, e:
            self.log_exception(e)
            log.error("Error retrieving list of move requests. \n" + str(e))

        return rows

    # Take a registration plate and return a dictionary of the car details
    def getCarDetailsAsDictionary(self, registration):
        log.debug("Retrieving car details for registration " + registration)

        try:
            sql = "SELECT * from registrations " \
                  "WHERE registration = %s;"
            data = (registration, )

            self.cursor.execute(sql, data)
            row = self.cursor.fetchone()

            car = {}
            car['FirstName'] = row['firstname']
            car['Surname'] = row['surname']
            car['Reg'] = row['registration']
            car['Mobile'] = row['mobile']

            return car

        except psycopg2.DatabaseError, e:
            self.log_exception(e)
            log.error("Error retrieving car details \n" + str(e))

    def get_user_dict_from_mobile(self, mobile):
        log.debug("Getting user record from mobile " + mobile)

        try:
            sql = "SELECT " \
                  "COALESCE (u.firstname, r.firstname, NULL) as firstname, " \
                  "COALESCE (u.surname, r.surname, NULL) as surname, " \
                  "COALESCE (u.mobile, r.mobile, NULL) as mobile " \
                  "FROM registrations r " \
                  "LEFT JOIN users u on u.user_id = r.user_id " \
                  "where r.mobile = %s;"

            data = (mobile,)

            self.cursor.execute(sql, data)
            row = self.cursor.fetchone()
            user_exists = len(row) > 0
            if user_exists:
                user_dict = {
                    'FirstName': row['firstname'],
                    'Surname': row['surname'],
                    'Mobile': row['mobile']
                }

                log.debug("Returning the following user: \n" + str(user_dict))
                return user_dict
            else:
                log.debug("Could not find mobile number in the database.")
                return None

        except psycopg2.DatabaseError, e:
            self.log_exception(e)
            log.error("Error getting user dictionary from mobile number \n" + str(e))
            return None

    def get_user_dict_from_reg(self, registration):
        log.debug("Getting user record from registration " + registration)

        try:
            sql = "SELECT " \
                  "COALESCE (u.firstname, r.firstname, NULL) as firstname, " \
                  "COALESCE (u.surname, r.surname, NULL) as surname, " \
                  "COALESCE (u.mobile, r.mobile, NULL) as mobile " \
                  "FROM registrations r " \
                  "LEFT JOIN users u on u.user_id = r.user_id " \
                  "where registration = %s;"

            data = (registration,)

            self.cursor.execute(sql, data)
            row = self.cursor.fetchone()
            user_exists = (len(row) > 0)
            if user_exists:
                user_dict = {
                    'FirstName': row['firstname'],
                    'Surname': row['surname'],
                    'Mobile': row['mobile']
                }
                log.debug("Returning the following user: \n" + str(user_dict))
                return user_dict

            else:

                log.debug("Couldn't find registration in database")
                return None

        except psycopg2.DatabaseError, e:
            self.log_exception(e)
            log.error("Error getting user dictionary from registration \n" + str(e))
            return None

    # Take a Mobile Number and return the registration plate for that number in the database
    def get_reg_from_mobile(self, mobile):
        log.debug("Getting registration from mobile number " + mobile)

        try:
            sql = "SELECT registration from registrations " \
                  "WHERE mobile = %s;"
            data = (mobile,)

            self.cursor.execute(sql, data)
            registration = self.cursor.fetchone()[0]
            return registration

        except psycopg2.DatabaseError, e:
            self.log_exception(e)
            log.error("Error getting registration from mobile number \n" + str(e))
            return "Unknown"

    # Take a mobile number and return the mobile number of the most recent person to block that mobile number in.
    def get_blocker_mobile_from_blockee_mobile(self, blockee_mobile):
        log.debug("Getting most recent blocker mobile number from blockee mobile " + blockee_mobile)

        try:
            sql = "SELECT blocker_mobile from blocks " \
                  "WHERE blockee_mobile = %s " \
                  "ORDER BY timestamp_utc desc " \
                  "limit 1;"

            data = (blockee_mobile,)

            self.cursor.execute(sql, data)
            blocker_number = self.cursor.fetchone()[0]
            return blocker_number

        except psycopg2.DatabaseError, e:
            self.log_exception(e)
            log.error("Error retrieving blocker mobile from blockee mobile \n" + str(e))
            return "Unknown"

    # Take a Registration Plate and return the name associated with that plate in the database
    def get_name_from_reg(self, registration):
        log.debug("Getting name from registration " + registration)

        try:
            sql = "SELECT firstname, surname from registrations " \
                  "WHERE registration = %s;"
            data = (registration,)

            self.cursor.execute(sql, data)
            row = self.cursor.fetchone()
            print row
            full_name = row[0] + " " + row[1]
            return full_name

        except psycopg2.DatabaseError, e:
            self.log_exception(e)
            log.error("Error getting name from registration \n" + str(e))
            return "Unknown"

    # Take a Mobile Number and return the name associated with that number in the database
    def get_name_from_mobile(self, mobile):
        log.debug("Getting name from mobile number " + mobile)

        try:
            # TODO: Move get_name_from_mobile to use the users table once we can guarantee every registration will have a user record
            sql = "SELECT firstname, surname from registrations " \
                  "WHERE mobile = %s " \
                  "limit 1;"
            data = (mobile,)

            self.cursor.execute(sql, data)
            row = self.cursor.fetchone()

            if row is None:
                return "Unknown"

            full_name = row[0] + " " + row[1]
            return full_name

        except psycopg2.DatabaseError, e:
            self.log_exception(e)
            log.error("Error retrieving name from mobile number \n" + str(e))
            return "Unknown"

    # Take a registration number and get a landline number
    def get_landline_from_reg(self, registration):
        try:
            log.debug("Getting alternative contact info from registration " + registration)
        except Exception as e:
            self.log_exception(e)
            pass

        try:
            sql = "SELECT alt_contact_text from users " \
                  "WHERE user_id = (SELECT user_id from registrations where registration = %s);"
            data = (registration,)

            self.cursor.execute(sql, data)
            row = self.cursor.fetchone()
            if row[0] is None:
                log.debug("Row[0] is " + str(row))
                return ""
            else:
                log.debug("Row[0] is " + str(row))
                alt_contact_text = row[0]
                return alt_contact_text

        except psycopg2.DatabaseError, e:
            self.log_exception(e)
            log.error("Error getting alternative contact text from registration: \n" + str(e))
            return ""

    # Take a Mobile Number and return the notification preferences for that recipient
    def get_notification_preferences_for_user(self, mobile):
        log.debug("Getting notification preferences for user")

        try:
            sql = "SELECT * from users " \
                  "WHERE mobile = %s;"
            data = (mobile,)

            self.cursor.execute(sql, data)
            row = self.cursor.fetchone()

            if row is None:
                return None

            # Create a preferences dictionary to populate with the notification preferences.
            # Start off with SMS being enabled, and Email / Pushover being disabled.
            preferences = {"Email": 0, "Pushover": 0, "SMS": 1}

            # Then check the user record retrieved from the database to see which notification types are required.
            # Update the preferences dictionary with the correct values
            preferences['Email'] = 1 if (row['email_notifications'] is True and row['email_address'] is not None) else 0
            preferences['Pushover'] = 1 if row['pushover_notifications'] is True else 0

            # Return the preferences dictionary
            return preferences

        except psycopg2.DatabaseError, e:
            self.log_exception(e)
            log.error("Error getting notification preferences for user \n" + str(e))
            return None

    # Take a Mobile Number and return the email address for that recipient
    def get_email_address(self, recipient):
        log.debug("Getting email address for mobile number " + recipient)

        try:
            sql = "SELECT email_address from users " \
                  "WHERE mobile = %s;"
            data = (recipient,)

            self.cursor.execute(sql, data)
            row = self.cursor.fetchone()

            try:
                email = row['email_address']
                return email
            except Exception, e:
                self.log_exception(e)
                raise

        except psycopg2.DatabaseError, e:
            self.log_exception(e)
            log.error("Error getting email address \n" + str(e))
            return None

    def api_registrations_get(self, registration):
        log.debug("Getting registration details")

        try:
            sql = "SELECT * from registrations " \
                  "WHERE registration = %s;"
            data = (registration,)
            self.dict_cursor.execute(sql, data)
            row = self.dict_cursor.fetchone()
            return row

        except psycopg2.DatabaseError, e:
            self.log_exception(e)
            log.error("Error getting details for single registration")

    def api_registrations_getall(self):
        log.debug("Getting registration details")

        try:
            sql = "SELECT * from registrations " \
                  "order by registration;"
            self.dict_cursor.execute(sql,)
            rows = self.dict_cursor.fetchall()
            print(rows)
            return rows

        except psycopg2.DatabaseError, e:
            self.log_exception(e)
            log.error("Error getting details for single registration")

    def api_blocks_getall(self):
        log.debug("Getting all blocks")

        try:
            sql = "SELECT * from v_active_blocks;"
            self.dict_cursor.execute(sql,)
            rows = self.dict_cursor.fetchall()
            return rows

        except psycopg2.DatabaseError, e:
            self.log_exception(e)
            log.error("Error getting all blocks from database")

    def api_smslogs_get(self):
        log.debug("Getting all logs")

        try:
            sql = "SELECT * from logsms " \
                  "ORDER BY timestamp desc " \
                  "LIMIT 250;"
            self.dict_cursor.execute(sql,)
            rows = self.dict_cursor.fetchall()
            return rows

        except psycopg2.DatabaseError, e:
            self.log_exception(e)
            log.error("Error getting all SMS log entries from database")

    def api_logs_get(self):
        log.debug("Retrieve logsms resource from database")

        try:
            sql = "SELECT * from log " \
                  "WHERE log_action != %s and log_action != %s " \
                  "ORDER BY log_timestamp desc " \
                  "LIMIT 500;"
            data = ('GET_STATUS', 'STARTUP')
            self.dict_cursor.execute(sql,data)
            rows = self.dict_cursor.fetchall()
            return rows

        except psycopg2.DatabaseError, e:
            self.log_exception(e)
            log.error("Error getting all log entries from database")

    def get_api_credentials(self, username):
        log.debug(str.format("Checking if api username {0} exists", username))

        try:
            sql = "SELECT * from users_api " \
                  "WHERE username = %s;"
            data = (username,)

            self.dict_cursor.execute(sql, data)
            row = self.dict_cursor.fetchone()

            return row

        except psycopg2.DatabaseError, e:
            self.log_exception(e)
            log.error(str.format("Error checking status of username {0} \n {1}", username, e))

    # Take a mobile number
    # Return True if the number is already registered
    # Return False if number is not registered
    # Return None if error retrieving record from database
    def number_is_registered(self, number):
        log.debug("Checking if mobile " + str(number) + " is registered with BlockBuster.")

        try:
            sql = "SELECT Count(*) from registrations " \
                  "WHERE mobile = %s;"
            data = (number,)

            self.cursor.execute(sql, data)
            row = self.cursor.fetchone()
            print(row)

            registered = True if (row[0] > 0) else False

            return registered

        except psycopg2.DatabaseError, e:
            self.log_exception(e)
            log.error("Error checking status of number \n" + str(e))

    def mobile_sharing_enabled(self, mobile):
        log.debug("Checking whether mobile sharing is enabled for " + mobile)

        try:
            sql = "SELECT share_mobile " \
                  "FROM users " \
                  "WHERE mobile = %s;"
            data = (mobile,)

            self.cursor.execute(sql, data)
            enabled = self.cursor.fetchone()[0]
            return enabled

        except psycopg2.DatabaseError, e:
            log.error("Error checking mobile sharing status \n" + str(e))
            self.log_exception(e)

    def checkifregexists(self, registration):
        log.debug("Checking if registration exists in the database")

        try:
            sql = "SELECT Count(*) from registrations " \
                  "WHERE registration = %s;"

            data = (registration,)

            self.cursor.execute(sql, data)
            row = self.cursor.fetchone()
            log.debug(row[0])
            exists = (row[0] > 0)

            return 1 if exists else 0

        except psycopg2.DatabaseError, e:
            self.log_exception(e)
            log.error("Error whilst checking if registration exists in database \n" + str(e))

    # =========== UPDATE methods =============
    def enable_mobile_number_sharing(self, userMobile):
        """Update the user record to allow the sharing of their mobile number with other users"""
        # First, check to see whether the user already has an entry in the users table
        try:
            sql = "SELECT * from users " \
                  "WHERE mobile = %s limit 1;"
            data = (userMobile,)

            self.cursor.execute(sql, data)
            rows = self.cursor.fetchone()

        except psycopg2.DatabaseError, e:
            self.log_exception(e)
            log.error(str(e))
            return 1

        if rows is None:
            # Add a new row for this user with the share_mobile field set to TRUE.
            log.debug('Setting Share_Mobile = TRUE on new user record.')
            try:
                sql = "INSERT INTO users" \
                      "(mobile, email_address, email_notifications, pushover_notifications, pushover_token, " \
                      "share_mobile, alt_contact_text) " \
                      "values(%s, %s, %s, %s, %s, %s, %s);"
                data = (userMobile, None, False, False, None, True, None)

                self.cursor.execute(sql,data)
                self.conn.commit()
                return 0

            except psycopg2.DatabaseError, e:
                self.log_exception(e)
                log.error(str(e))
                return 1

        elif len(rows) >= 1:
            # Update the existing row for this user so that the share_mobile field is TRUE
            log.debug('Setting Share_Mobile = TRUE on existing user record.')
            try:
                sql = "UPDATE users " \
                      "SET share_mobile = TRUE " \
                      "WHERE mobile = %s;"
                data = (userMobile,)

                self.cursor.execute(sql, data)
                self.conn.commit()
                return 0

            except psycopg2.DatabaseError, e:
                self.log_exception(e)
                log.error(str(e))
                return 1

    def disable_mobile_number_sharing(self, userMobile):

        # First, check to see whether the user already has an entry in the users table
        try:
            sql = "SELECT * from users " \
                  "WHERE mobile = %s limit 1;"
            data = (userMobile,)

            self.cursor.execute(sql, data)
            rows = self.cursor.fetchone()

        except psycopg2.DatabaseError, e:
            self.log_exception(e)
            log.error(str(e))
            return 1

        if rows == None:
            # Add a new row for this user with the share_mobile field set to FALSE.
            log.debug('Setting Share_Mobile = FALSE on new user record.')
            try:
                sql = "INSERT INTO users" \
                      "(mobile, email_address, email_notifications, pushover_notifications, pushover_token, " \
                      "share_mobile, alt_contact_text) " \
                      "values(%s, %s, %s, %s, %s, %s, %s);"
                data = (userMobile, None, False, False, None, False, None)

                self.cursor.execute(sql,data)
                self.conn.commit()
                return 0

            except psycopg2.DatabaseError, e:
                self.log_exception(e)
                log.error(str(e))
                return 1

        elif len(rows) >= 1:
            # Update the existing row for this user so that the share_mobile field is FALSE
            log.debug('Setting Share_Mobile = FALSE on existing user record.')
            try:
                sql = "UPDATE users " \
                      "SET share_mobile = FALSE " \
                      "WHERE mobile = %s;"
                data = (userMobile,)

                self.cursor.execute(sql, data)
                self.conn.commit()
                return 0

            except psycopg2.DatabaseError, e:
                self.log_exception(e)
                log.error(str(e))
                return 1

    def update_alternative_contact_text(self, userMobile, altText):

        # First, check to see whether the user already has an entry in the users table
        try:
            sql = "SELECT * from users " \
                  "WHERE mobile = %s limit 1;"
            data = (userMobile,)

            self.cursor.execute(sql, data)
            rows = self.cursor.fetchone()

        except psycopg2.DatabaseError, e:
            self.log_exception(e)
            log.error(str(e))
            return 1

        if rows is None:
            # Add a new row for this user with the specified alternative contact text set.
            log.debug('Setting alternative contact text on new user record.')
            try:
                sql = "INSERT INTO users" \
                      "(mobile, email_address, email_notifications, pushover_notifications, pushover_token, " \
                      "share_mobile, alt_contact_text) " \
                      "values(%s, %s, %s, %s, %s, %s, %s);"
                data = (userMobile, None, False, False, None, True, altText)

                self.cursor.execute(sql,data)
                self.conn.commit()
                return 0

            except psycopg2.DatabaseError, e:
                self.log_exception(e)
                log.error(str(e))
                return 1

        elif len(rows) >= 1:
            # Update the existing row for this user so that the share_mobile field is TRUE
            log.debug('Setting alternative contact text on new existing record.')
            try:
                sql = "UPDATE users " \
                      "SET alt_contact_text = %s " \
                      "WHERE mobile = %s;"
                data = (altText, userMobile)

                self.cursor.execute(sql, data)
                self.conn.commit()
                return 0

            except psycopg2.DatabaseError, e:
                self.log_exception(e)
                log.error(str(e))
                return 1

    def update_email_address(self, mobile, email_address):
        log.debug("Updating email address for " + mobile + " to " + email_address)

        # First, check to see whether the user already has an entry in the users table
        try:
            sql = "SELECT * from users " \
                  "WHERE mobile = %s limit 1;"
            data = (mobile,)

            self.cursor.execute(sql, data)
            rows = self.cursor.fetchone()
            user_already_exists = not (rows == None)
            print user_already_exists

        except psycopg2.DatabaseError, e:
            self.log_exception(e)
            log.error(str(e))
            return 1

        # If the user does not already have a record in the users table, create them one and set the email address
        if not user_already_exists:

            # Add a new row for this user with the specified alternative contact text set.
            log.debug("Adding new user record for " + mobile + " and setting email address to " + email_address)

            try:
                sql = "INSERT INTO users" \
                      "(mobile, email_address, share_mobile, alt_contact_text) " \
                      "values(%s, %s, %s, (SELECT landline from registrations where mobile = %s));" \

                # Only insert the minimum values needed to create the record. (Share Mobile always defaults to Yes)
                data = (mobile, email_address, True, mobile)

                self.cursor.execute(sql,data)
                self.conn.commit()
                log.info("New user record added for " + mobile)
                return "Your email address has been set to " + email_address

            except psycopg2.DatabaseError, e:
                self.log_exception(e)
                log.error("Failed to add new user record \n" + str(e))
                return "Unable to update your email address. Please report this issue."

        # If the user already has a record in the users table, then simply update that record
        elif user_already_exists:

            # Update the existing user record with the specified email address
            log.debug("Updating user record for " + mobile + " with email address " + email_address)

            try:
                sql = "UPDATE users " \
                      "SET email_address = %s " \
                      "WHERE mobile = %s;"
                data = (email_address, mobile)

                self.cursor.execute(sql, data)
                self.conn.commit()
                log.info("User record for " + mobile + " updated with email address " + email_address)

                return "Your email address has been set to " + email_address

            except psycopg2.DatabaseError, e:
                self.log_exception(e)
                log.error("Error trying to update user record with new email address \n" + str(e))
                return "Unable to update your email address. Please report this issue."

    def enable_email_notifications(self, mobile):
        log.debug("Enabling email notifications for " + mobile)

        # First, check to see whether the user already has an entry in the users table
        try:
            sql = "SELECT * from users " \
                  "WHERE mobile = %s limit 1;"
            data = (mobile,)

            self.cursor.execute(sql, data)
            rows = self.cursor.fetchone()
            user_already_exists = not (rows == None)
            print user_already_exists

        except psycopg2.DatabaseError, e:
            self.log_exception(e)
            log.error(str(e))
            return 1

        # If the user does not already have a record in the users table, create them one and set the email address
        if not user_already_exists:

            # Add a new row for this user with the specified alternative contact text set.
            log.debug("Adding new user record for " + mobile + " and enabling email notifications")

            try:
                sql = "INSERT INTO users" \
                      "(mobile, email_notifications, share_mobile, alt_contact_text) " \
                      "values(%s, %s, %s, (SELECT landline from registrations where mobile = %s));" \

                # Only insert the minimum values needed to create the record. (Share Mobile always defaults to Yes)
                data = (mobile, True, True, mobile)

                self.cursor.execute(sql,data)
                self.conn.commit()
                log.info("New user record added for " + mobile)
                return "Email notifications have been enabled for you. Please make sure you set an email address using " \
                       "SET EMAIL email@address.com"

            except psycopg2.DatabaseError, e:
                self.log_exception(e)
                log.error("Failed to add new user record \n" + str(e))
                return "Unable to enable email notifications. Please report this issue."

        # If the user already has a record in the users table, then simply update that record
        elif user_already_exists:

            # Update the existing user record with the specified email address
            log.debug("Updating user record to enable email notifications for " + mobile)

            try:
                sql = "UPDATE users " \
                      "SET email_notifications = %s " \
                      "WHERE mobile = %s;"
                data = (True, mobile)

                self.cursor.execute(sql, data)
                self.conn.commit()
                log.info("User record for " + mobile + " updated to enable email notifications")

                return "Email notifications have now been turned on for you.  Please make sure you set an email address using " \
                       "SET EMAIL email@address.com"

            except psycopg2.DatabaseError, e:
                self.log_exception(e)
                log.error("Error trying to enable email notifications for user \n" + str(e))
                return "Unable to update your email notification preferences. Please report this issue."

    def disable_email_notifications(self, mobile):
        log.debug("Disabling email notifications for " + mobile)

        # First, check to see whether the user already has an entry in the users table
        try:
            sql = "SELECT * from users " \
                  "WHERE mobile = %s limit 1;"
            data = (mobile,)

            self.cursor.execute(sql, data)
            rows = self.cursor.fetchone()
            user_already_exists = not (rows == None)
            print user_already_exists

        except psycopg2.DatabaseError, e:
            self.log_exception(e)
            log.error(str(e))
            return 1

        # If the user does not already have a record in the users table, create them one and set the email address
        if not user_already_exists:

            # Add a new row for this user with the specified alternative contact text set.
            log.debug("Adding new user record for " + mobile + " and disabling email notifications")

            try:
                sql = "INSERT INTO users" \
                      "(mobile, email_notifications, share_mobile, alt_contact_text) " \
                      "values(%s, %s, %s, (SELECT landline from registrations where mobile = %s));" \

                # Only insert the minimum values needed to create the record. (Share Mobile always defaults to Yes)
                data = (mobile, False, True, mobile)

                self.cursor.execute(sql,data)
                self.conn.commit()
                log.info("New user record added for " + mobile)
                return "Email notifications have now been turned off."

            except psycopg2.DatabaseError, e:
                self.log_exception(e)
                log.error("Failed to add new user record \n" + str(e))
                return "Unable to enable email notifications. Please report this issue."

        # If the user already has a record in the users table, then simply update that record
        elif user_already_exists:

            # Update the existing user record with the specified email address
            log.debug("Updating user record to disable email notifications for " + mobile)

            try:
                sql = "UPDATE users " \
                      "SET email_notifications = %s " \
                      "WHERE mobile = %s;"
                data = (False, mobile)

                self.cursor.execute(sql, data)
                self.conn.commit()
                log.info("User record for " + mobile + " updated to disable email notifications")

                return "Email notifications have now been turned off."

            except psycopg2.DatabaseError, e:
                self.log_exception(e)
                log.error("Error trying to disable email notifications for user \n" + str(e))
                return "Unable to update your email notification preferences. Please report this issue."

    # ========== REMOVE methods ============
    def remove_blocks(self, blocker_mobile, blocked_reg):
        try:
            log.debug('Removing blocks matching ' + blocked_reg + ' and ' + blocker_mobile)
            sql = "DELETE FROM blocks " \
                  "WHERE blocker_mobile = %s and blocked_reg = %s;"
            data = (blocker_mobile, blocked_reg)

            self.cursor.execute(sql, data)
            self.conn.commit()

        except psycopg2.DatabaseError, e:
            self.log_exception(e)
            log.error("Error removing blocks for this mobile number. \n" + str(e))

    def remove_move_request(self, blocker_mobile, blockee_mobile):
        try:
            log.debug('Removing move requests matching ' + blockee_mobile + ' and ' + blocker_mobile)
            sql = "DELETE FROM move_requests " \
                  "WHERE blocker_mobile = %s and blockee_mobile = %s;"
            data = (blocker_mobile, blockee_mobile)

            self.cursor.execute(sql, data)
            self.conn.commit()

        except psycopg2.DatabaseError, e:
            self.log_exception(e)
            log.error("Error removing move requests for this number combination. \n" + str(e))

    # Take a registration plate and mobile number and, if valid, remove the registration from the database
    def remove_registration(self, registration, mobile):
        try:

            try:
                log.debug('Checking that registration belongs to this mobile number.')

                sql = "SELECT Count(*) from registrations " \
                      "WHERE registration = %s and mobile = %s;"

                data = (registration, mobile)

                self.cursor.execute(sql, data)
                row = self.cursor.fetchone()
                exists = (row[0] > 0)

                if exists:
                    try:
                        sql = "DELETE FROM registrations " \
                              "WHERE registration = %s and mobile = %s;"

                        self.cursor.execute(sql, data)
                        self.conn.commit()

                        log.debug('Registration removed.')
                        return 1

                    except psycopg2.DatabaseError, e:
                        self.log_exception(e)
                        log.error('Error unregistering car from BlockBuster.' + str(e))
                        return -1

                else:
                    log.debug('Registration not verified as belonging to this mobile number.')
                    return 0

            except psycopg2.DatabaseError, e:
                self.log_exception(e)
                log.error(str(e))

        except Exception as e:
            self.log_exception(e)
            log.error('Error encountered whilst trying to remove a registration from the database.' + str(e))
            return -1

    # Take a mobile number and erase the alternative contact text for that user
    def remove_alternative_contact_text(self, mobile):

        log.debug("Attempting erase of alternative contact text for mobile " + mobile)
        try:
            sql = "UPDATE users " \
                  "SET alt_contact_text = NULL " \
                  "WHERE mobile = %s;"

            data = (mobile,)

            self.cursor.execute(sql, data)
            self.conn.commit()

            return 0
        except psycopg2.DatabaseError, e:
            self.log_exception(e)
            log.error("Error erasing alternative contact text \n" + str(e))

            return 1