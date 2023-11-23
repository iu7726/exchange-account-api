from log.scripts.logging import createAccessLog, getIp, get_client_ip
from django.db import connections
from libs_exchange_handler.og_exception import OgException
from django.http import JsonResponse 
def history_middleware(get_response):
    # One-time configuration and initialization.

    def middleware(request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        # print('1', get_client_ip(request))
        # print('2', getIp(request))
        location = getLocation(request)
        # print(location)
        if location is None:
            location = {}
            location['isRestricted'] = 0
            location['country'] = None
            location['city'] = None
            print('location null')
        
        createAccessLog(request, location)

        response = get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response

    return middleware

def getLocation(request):
    ip = getIp(request)
    print(ip)
    sql = ("SELECT "
            "locations.geoname_id AS geonameId, "
            "country_iso_code AS IsoCode, "
            "continent_code AS continentCode, "
            "continent_name AS continentName, "
            "country_name AS country, "
            "subdivision_1_name AS subdivision1, "
            "subdivision_1_iso_code AS subdivisionIsoCode1, "
            "subdivision_2_name AS subdivision2, "
            "subdivision_2_iso_code AS subdivisionIsoCode2, "
            "city_name AS city, "
            "time_zone AS timeZone, "
            "latitude, "
            "longitude, "
            "accuracy_radius AS accuracyRadius, "
            "postal_code AS postalCode, "
            "IF( restrict_locations.id IS NULL , False, True) AS isRestricted "
            "FROM "
            "( " 
                "SELECT "
                    "geoname_id, "
                    "start_ip_num, "
                    "end_ip_num, "
                    "latitude, "
                    "longitude, "
                    "accuracy_radius, "
                    "postal_code  "
                "FROM "
                    "iprange "
                "WHERE "
                    f"start_ip_num <= INET_ATON('{ip}') "
                "ORDER BY start_ip_num DESC LIMIT 100 "
            ") AS T "
        "LEFT JOIN "
            "locations ON locations.geoname_id = T.geoname_id "
        "LEFT JOIN "
            "restrict_locations ON locations.geoname_id = T.geoname_id "
        "WHERE "
            f"end_ip_num >= INET_ATON('{ip}');")
    
    with connections['geo'].cursor() as cursor:
            cursor.execute(sql)
            row = cursor.fetchone()

    print(row)

    return row