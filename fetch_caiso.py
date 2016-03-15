import datetime
import io
import xml.etree.ElementTree as et
import zipfile

import requests


s = requests.Session()


def datetime_to_api_date(dt):
    """Accepts a datetime object in UTC
    (from e.g. datetime.datetime.utcnow()).
    """
    return dt.strftime("%Y%m%dT%H:%M-0000")


def oasis_get_current_rtm(query, **kwargs):
    now = datetime.datetime.utcnow()
    then = now - datetime.timedelta(minutes=6)
    url = "http://oasis.caiso.com/oasisapi/SingleZip"
    params = {
        "queryname": query,
        "startdatetime": datetime_to_api_date(then),
        "enddatetime": datetime_to_api_date(now),
        "version": 1,
    }
    params.update(kwargs)
    response = s.get(url, params=params)
    response.raise_for_status()

    content_file = io.BytesIO(response.content)
    content_archive = zipfile.ZipFile(content_file)
    data_entry = content_archive.infolist()[0]
    xml = content_archive.read(data_entry).decode('utf-8')
    return et.fromstring(xml)


def get_current_renewables():
    root = oasis_get_current_rtm("SLD_REN_FCST", market_run_id="RTD")
    ns = {"oasis": "http://www.caiso.com/soa/OASISReport_v1.xsd"}
    reports = root.findall(".//oasis:REPORT_DATA", ns)
    result = {}
    for report in reports:
        value = float(report.find("oasis:VALUE", ns).text)
        renewable = report.find("oasis:RENEWABLE_TYPE", ns).text
        result[renewable] = result.get(renewable, 0) + value
    return result


def get_current_demand():
    root = oasis_get_current_rtm("SLD_FCST", market_run_id="RTM")
    ns = {"oasis": "http://www.caiso.com/soa/OASISReport_v1.xsd"}
    search_string = ".//oasis:REPORT_DATA[oasis:RESOURCE_NAME='CA ISO-TAC']"
    report = root.find(search_string, ns)
    return float(report.find('oasis:VALUE', ns).text)


if __name__ == "__main__":
    print(get_current_renewables())
    print(get_current_demand())
