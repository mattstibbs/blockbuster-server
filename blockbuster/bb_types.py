class SMSRequest:

    def __init__(self):
        self.requestormobile = ""
        self.requesterId = ""
        self.requestorname = ""
        self.requestorreg = ""
        self.requestbody = ""
        self.requestsmsservice = ""
        self.servicenumber = ""
        self.instancename = ""
        self.requestcommandlist = []
        self.requestcommand = ""

    # Returns the first word from the request body as the required command
    def get_command_element(self):
        return self.requestcommandlist[0].upper()


class SMSRequestFactory:
    def __init__(self):
        pass

    def create(self):
        return SMSRequest()


class APIRequest:

    def __init__(self):
        self.requestormobile = ""
        self.servicenumber = ""


class APIRequestFactory:
    def __init__(self):
        pass

    def create(self):
        return APIRequest()


class BBRequest:
    def __init__(self):
        self.requestormobile = ""
        self.requesterId = ""

