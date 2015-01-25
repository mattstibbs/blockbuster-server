class DBConnector:

    def __init__(self):
        pass

    def db_status_check(self):
        raise NotImplementedError()

    def db_stats_check(self):
        raise NotImplementedError()

    def db_version_check(self):
        raise NotImplementedError()

    def checkifregexists(self):
        raise NotImplementedError()

    def add_log_table_entry(self):
        raise NotImplementedError()

    def remove_registration(self):
        raise NotImplementedError()


class DBAnalyticsConnector:

    def __init__(self):
        pass

    def add_analytics_record(self):
        raise NotImplementedError()


class DBLogsConnector:

    def __init__(self):
        pass

    def add_transaction_record(self):
        raise NotImplementedError()


class DBBlocksConnector:

    def __init__(self):
        raise NotImplementedError()


    def add_block_record(self):
        raise NotImplementedError()


    def get_list_of_blocks_for_blockee(self):
        raise NotImplementedError()


    def get_count_of_blocks_for_blockee(self):
        raise NotImplementedError()


    def get_list_of_blocks_for_blocker(self):
        raise NotImplementedError()


    def add_move_request(self):
        raise NotImplementedError()


    def remove_blocks(self):
        raise NotImplementedError()


    def get_open_move_requests(self):
        raise NotImplementedError()


    def remove_move_request(self):
        raise NotImplementedError()


class DBPushoverConnector:

    def __init__(self):
        raise NotImplementedError()

    def add_pushover_token_for_user(self):
        raise NotImplementedError()


    def get_pushover_user_token_from_mobile(self):
        raise NotImplementedError()


    def turn_push_notifications_on(self):
        raise NotImplementedError()


    def turn_push_notifications_off(self):
        raise NotImplementedError()


class DBEmailConnector:

    def __init__(self):
        raise NotImplementedError()

    def enable_email_notifications(self):
        raise NotImplementedError()


    def disable_email_notifications(self):
        raise NotImplementedError()


    def update_email_address(self):
        raise NotImplementedError()


    def get_email_address(self):
        raise NotImplementedError()


class DBUserConnector:

    def __init__(self):
        raise NotImplementedError()


    def get_api_credentials(self):
        raise NotImplementedError()

    def number_is_registered(self):
        raise NotImplementedError()


    def mobile_sharing_enabled(self):
        raise NotImplementedError()


    def get_notification_preferences_for_user(self):
        raise NotImplementedError()


    def get_landline_from_reg(self):
        raise NotImplementedError()


    def get_name_from_mobile(self):
        raise NotImplementedError()


    def get_name_from_reg(self):
        raise NotImplementedError()


    def get_reg_from_mobile(self):
        raise NotImplementedError()


    def get_blocker_mobile_from_blockee_mobile(self):
        raise NotImplementedError()


    def remove_registration(self):
        raise NotImplementedError()

    def enable_mobile_number_sharing(self, mobile_number):
        raise NotImplementedError()


    def disable_mobile_number_sharing(self):
        raise NotImplementedError()


    def update_alternative_contact_text(self):
        raise NotImplementedError()


    def get_user_dict_from_mobile(self):
        raise NotImplementedError()


    def get_user_dict_from_reg(self):
        raise NotImplementedError()


    def remove_alternative_contact_text(self):
        raise NotImplementedError()



class DBCarsConnector:
    def __init__(self):
        raise NotImplementedError()


    def getCarDetailsAsDictionary(self):
        raise NotImplementedError()


    def register_new_car(self):
        raise NotImplementedError()


class DBApiConnector:
    def __init__(self):
        raise NotImplementedError()


    def api_registrations_get(self, registration):
        raise NotImplementedError()

    def api_registrations_getall(self):
        raise NotImplementedError()

    def api_blocks_getall(self):
        raise NotImplementedError()

    def api_smslogs_get(self):
        raise NotImplementedError()

    def api_logs_get(self):
        raise NotImplementedError()

    def api_logsms_get(self):
        raise NotImplementedError()