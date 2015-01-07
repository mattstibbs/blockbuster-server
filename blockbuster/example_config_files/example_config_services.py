__author__ = 'matt'

def identify_service(number):
    if number == "+440000000000":
        instancename = "BB England"
        location = "England"
    elif number == "+440000000001":
        instancename = "BB Wales"
        location = "Wales"
    else:
        instancename = "BB Unknown"
        location = "Unknown"
    return instancename, location