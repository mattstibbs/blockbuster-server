import os

SERVICE_LIST = os.environ.get('SERVICE_LIST')

list_of_services = SERVICE_LIST.split('|')

new_service_list = {}

for service_item in list_of_services:
    service_config_items = service_item.split(':')

    service = {
        'number': service_config_items[0],
        'instance_name': service_config_items[1],
        'location': service_config_items[2],
    }

    new_service_list[service['number']] = service

print(new_service_list)


# def identify_service(number):
    # if number == "+440000000000":
    #     instancename = "BB England"
    #     location = "England"
    # elif number == "+440000000001":
    #     instancename = "BB Wales"
    #     location = "Wales"
    # else:
    #     instancename = "BB Unknown"
    #     location = "Unknown"
    # return instancename, location

def identify_service(number):
    return "BlockBuster", "England"
