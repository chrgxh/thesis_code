from configparser import ConfigParser
from datetime import datetime, timedelta


#def read_config_file():
#    config_object = ConfigParser()
#    config_object.read("HERON_ETLs/config.ini")
#    return config_object

#onfig_object = read_config_file()

# HERON API SETTINGS (Directly included)
HERON_DOMAIN = "api.platform.heron.gr"
HERON_EMAIL = "vmichalakopoulos@epu.ntua.gr"
HERON_PASS = "43214321"
HERON_START_DATE = 1623828783  # 2021-06-21T07:32:56.409Z
HERON_NANO_MUL = 1000000000  # In nanoseconds
HERON_DATA_API_STEP = 86400 * 30  # 30 days

HERON_DEVICES_EXTRA_INFO = []
SPARE = []

HISTORY = [
    {
        "deviceid": "domxem3-3494546ECDA9",
        "device_type_text": "3-phase EM",
        "device_name": "267-meter-EV",
        "device_type": 2,
        "home_id": "41",
        "registeredat": "2024-02-28T15:54:49.021Z",
        "measurements": [
            "energy",
            "returned_energy",
            "current",
            "energy",
            "pf",
            "power",
            "returned_energy",
            "total",
            "total_returned",
            "voltage",
            "relay"
        ]
    },
    {
        "deviceid": "domxem-C7FBD3",
        "device_type_text": "1-phase EM",
        "device_name": "69-meter-AC",
        "device_type": 1,
        "home_id": "69",
        "registeredat": "2024-02-01T11:44:01.692Z",
        "measurements": [
            "energy",
            "returned_energy",
            "energy",
            "power",
            "reactive_power",
            "returned_energy",
            "total",
            "total_returned",
            "voltage",
            "relay"
        ]
    },
    {
        "deviceid": "domxem3-244CAB43661F",
        "device_type_text": "3-phase EM",
        "device_name": "303-meter",
        "device_type": 2,
        "home_id": "303",
        "registeredat": "2024-02-01T07:35:12.589Z",
        "measurements": [
            "energy",
            "returned_energy",
            "current",
            "energy",
            "pf",
            "power",
            "returned_energy",
            "total",
            "total_returned",
            "voltage",
            "relay"
        ]
    },
    {
        "deviceid": "shellyplug-s-7C87CEBA3F5C",
        "device_type_text": "Shelly Plug S",
        "device_name": "126-PC",
        "device_type": 5,
        "home_id": "126",
        "registeredat": "2024-01-17T08:49:47.446Z",
        "measurements": [
            "energy",
            "energy",
            "power",
            "relay"
        ]
    },
    {
        "deviceid": "domxplug-4A8D4F",
        "device_type_text": "Shelly Plug",
        "device_name": "254-WM",
        "device_type": 4,
        "home_id": "254",
        "registeredat": "2024-01-05T15:29:08.423Z",
        "measurements": [
            "energy",
            "energy",
            "power",
            "relay"
        ]
    },
    {
        "deviceid": "domxplug-8F899E",
        "device_type_text": "Shelly Plug",
        "device_name": "126-AC",
        "device_type": 4,
        "home_id": "126",
        "registeredat": "2023-11-24T09:26:14.478Z",
        "measurements": [
            "energy",
            "energy",
            "power",
            "relay"
        ]
    },
    {
        "deviceid": "domxplug-8FF3B4",
        "device_type_text": "Shelly Plug",
        "device_name": "126-Dryer(S)",
        "device_type": 4,
        "home_id": "126",
        "registeredat": "2023-11-10T12:11:23.346Z",
        "measurements": [
            "energy",
            "energy",
            "power",
            "relay"
        ]
    },
    {
        "deviceid": "domxem3-3494547195AF",
        "device_type_text": "3-phase EM",
        "device_name": "300-meter-HP",
        "device_type": 2,
        "home_id": "120",
        "registeredat": "2023-10-31T12:24:25.052Z",
        "measurements": [
            "energy",
            "returned_energy",
            "current",
            "energy",
            "pf",
            "power",
            "returned_energy",
            "total",
            "total_returned",
            "voltage",
            "relay"
        ]
    },
    {
        "deviceid": "domxplug-2C9D91",
        "device_type_text": "Shelly Plug",
        "device_name": "266-DW",
        "device_type": 4,
        "home_id": "266",
        "registeredat": "2023-10-30T09:46:24.694Z",
        "measurements": [
            "energy",
            "energy",
            "power",
            "relay"
        ]
    },
    {
        "deviceid": "domxplug-286A3B",
        "device_type_text": "Shelly Plug",
        "device_name": "266-freezer",
        "device_type": 4,
        "home_id": "266",
        "registeredat": "2023-10-30T08:34:50.918Z",
        "measurements": [
            "energy",
            "energy",
            "power",
            "relay"
        ]
    },
    {
        "deviceid": "domxem3-3494546ED493",
        "device_type_text": "3-phase EM",
        "device_name": "293-meter-HP",
        "device_type": 2,
        "home_id": "293",
        "registeredat": "2023-10-30T08:26:18.237Z",
        "measurements": [
            "energy",
            "current",
            "energy",
            "pf",
            "power",
            "returned_energy",
            "total",
            "total_returned",
            "voltage",
            "relay"
        ]
    },
    {
        "deviceid": "domxplug-2869F0",
        "device_type_text": "Shelly Plug",
        "device_name": "266-TV_1",
        "device_type": 4,
        "home_id": "266",
        "registeredat": "2023-10-11T08:55:38.661Z",
        "measurements": [
            "energy",
            "energy",
            "power",
            "relay"
        ]
    },
    {
        "deviceid": "domxplug-C1A105",
        "device_type_text": "Shelly Plug",
        "device_name": "266-Humidifier",
        "device_type": 4,
        "home_id": "266",
        "registeredat": "2023-10-11T08:54:43.801Z",
        "measurements": [
            "energy",
            "energy",
            "power",
            "relay"
        ]
    },
    {
        "deviceid": "domxplug-C1CEA8",
        "device_type_text": "Shelly Plug",
        "device_name": "266-WM",
        "device_type": 4,
        "home_id": "266",
        "registeredat": "2023-10-11T08:54:19.223Z",
        "measurements": [
            "energy",
            "energy",
            "power",
            "relay"
        ]
    },
    {
        "deviceid": "domxplug-C1CA02",
        "device_type_text": "Shelly Plug",
        "device_name": "266-Dryer",
        "device_type": 4,
        "home_id": "266",
        "registeredat": "2023-10-11T08:53:51.282Z",
        "measurements": [
            "energy",
            "energy",
            "power",
            "relay"
        ]
    },
    {
        "deviceid": "domxplug-2CC63A",
        "device_type_text": "Shelly Plug",
        "device_name": "266-WM",
        "device_type": 4,
        "home_id": "266",
        "registeredat": "2023-10-11T08:53:29.259Z",
        "measurements": [
            "energy",
            "energy",
            "power",
            "relay"
        ]
    },
    {
        "deviceid": "domxplug-56057A",
        "device_type_text": "Shelly Plug",
        "device_name": "266-TV_2",
        "device_type": 4,
        "home_id": "266",
        "registeredat": "2023-10-11T08:52:23.963Z",
        "measurements": [
            "energy",
            "energy",
            "power",
            "relay"
        ]
    },
    {
        "deviceid": "domxem3-3494546ED449",
        "device_type_text": "3-phase EM",
        "device_name": "266-meter",
        "device_type": 2,
        "home_id": "266",
        "registeredat": "2023-10-11T08:49:38.999Z",
        "measurements": [
            "energy",
            "returned_energy",
            "current",
            "energy",
            "pf",
            "power",
            "returned_energy",
            "total",
            "total_returned",
            "voltage",
            "relay"
        ]
    },
    {
        "deviceid": "domxem3-349454718E54",
        "device_type_text": "3-phase EM",
        "device_name": "268-meter-EV",
        "device_type": 2,
        "home_id": "279",
        "registeredat": "2023-10-09T07:43:49.362Z",
        "measurements": [
            "energy",
            "current",
            "energy",
            "pf",
            "power",
            "returned_energy",
            "total",
            "total_returned",
            "voltage",
            "relay"
        ]
    },
    {
        "deviceid": "shellyplug-s-7C87CEBA3E4C",
        "device_type_text": "Shelly Plug S",
        "device_name": "279-TV",
        "device_type": 5,
        "home_id": "279",
        "registeredat": "2023-10-09T07:42:35.404Z",
        "measurements": [
            "energy",
            "energy",
            "power",
            "relay"
        ]
    },
    {
        "deviceid": "domxplug-2C907E",
        "device_type_text": "Shelly Plug",
        "device_name": "279-A/C",
        "device_type": 4,
        "home_id": "279",
        "registeredat": "2023-10-09T07:41:52.448Z",
        "measurements": [
            "energy",
            "energy",
            "power",
            "relay"
        ]
    },
    {
        "deviceid": "domxplug-2CAB64",
        "device_type_text": "Shelly Plug",
        "device_name": "279-DW",
        "device_type": 4,
        "home_id": "279",
        "registeredat": "2023-10-09T07:40:53.666Z",
        "measurements": [
            "energy",
            "energy",
            "power",
            "relay"
        ]
    },
    {
        "deviceid": "domxem3-244CAB436349",
        "device_type_text": "3-phase EM",
        "device_name": "279-meter",
        "device_type": 2,
        "home_id": "279",
        "registeredat": "2023-10-09T07:39:50.952Z",
        "measurements": [
            "energy",
            "returned_energy",
            "current",
            "energy",
            "pf",
            "power",
            "returned_energy",
            "total",
            "total_returned",
            "voltage",
            "relay"
        ]
    },
    {
        "deviceid": "shellyplug-s-7C87CEB520B4",
        "device_type_text": "Shelly Plug S",
        "device_name": "282-TV",
        "device_type": 5,
        "home_id": "282",
        "registeredat": "2023-10-04T13:23:14.250Z",
        "measurements": [
            "energy",
            "energy",
            "power",
            "relay"
        ]
    },
    {
        "deviceid": "shellyplug-s-7C87CEB50BAE",
        "device_type_text": "Shelly Plug S",
        "device_name": "282-Purifier",
        "device_type": 5,
        "home_id": "282",
        "registeredat": "2023-10-04T13:22:47.121Z",
        "measurements": [
            "energy",
            "energy",
            "power",
            "relay"
        ]
    },
    {
        "deviceid": "domxplug-C1CF07",
        "device_type_text": "Shelly Plug",
        "device_name": "282-A/C",
        "device_type": 4,
        "home_id": "282",
        "registeredat": "2023-10-04T13:22:05.591Z",
        "measurements": [
            "energy",
            "energy",
            "power",
            "relay"
        ]
    },
    {
        "deviceid": "domxem3-349454717314",
        "device_type_text": "3-phase EM",
        "device_name": "282-meter",
        "device_type": 2,
        "home_id": "282",
        "registeredat": "2023-10-04T13:19:39.110Z",
        "measurements": [
            "energy",
            "returned_energy",
            "current",
            "energy",
            "pf",
            "power",
            "returned_energy",
            "total",
            "total_returned",
            "voltage",
            "relay"
        ]
    },
    {
        "deviceid": "shellyplug-s-7C87CEB484E0",
        "device_type_text": "Shelly Plug S",
        "device_name": "289-TV",
        "device_type": 5,
        "home_id": "289",
        "registeredat": "2023-09-26T08:19:12.948Z",
        "measurements": [
            "energy",
            "energy",
            "power",
            "relay"
        ]
    },
    {
        "deviceid": "domxplug-2C35B5",
        "device_type_text": "Shelly Plug",
        "device_name": "289-A/C 2",
        "device_type": 4,
        "home_id": "289",
        "registeredat": "2023-09-26T08:18:14.600Z",
        "measurements": [
            "energy",
            "energy",
            "power",
            "relay"
        ]
    },
    {
        "deviceid": "domxplug-55F7BC",
        "device_type_text": "Shelly Plug",
        "device_name": "289-A/C 1",
        "device_type": 4,
        "home_id": "289",
        "registeredat": "2023-09-26T08:17:31.278Z",
        "measurements": [
            "energy",
            "energy",
            "power",
            "relay"
        ]
    },
    {
        "deviceid": "domxem3-3494546ED8F9",
        "device_type_text": "3-phase EM",
        "device_name": "283-meter-EV",
        "device_type": 2,
        "home_id": "283",
        "registeredat": "2023-09-26T07:41:52.219Z",
        "measurements": [
            "energy",
            "current",
            "energy",
            "pf",
            "power",
            "returned_energy",
            "total",
            "total_returned",
            "voltage",
            "relay"
        ]
    },
    {
        "deviceid": "shellyplug-s-7C87CEBA9A48",
        "device_type_text": "Shelly Plug S",
        "device_name": "281-TV",
        "device_type": 5,
        "home_id": "281",
        "registeredat": "2023-09-26T07:37:10.475Z",
        "measurements": [
            "energy",
            "energy",
            "power",
            "relay"
        ]
    },
    {
        "deviceid": "domxplug-286E36",
        "device_type_text": "Shelly Plug",
        "device_name": "281-A/C",
        "device_type": 4,
        "home_id": "281",
        "registeredat": "2023-09-26T07:36:22.728Z",
        "measurements": [
            "energy",
            "energy",
            "power",
            "relay"
        ]
    },
    {
        "deviceid": "domxplug-286BE0",
        "device_type_text": "Shelly Plug",
        "device_name": "281-WM",
        "device_type": 4,
        "home_id": "281",
        "registeredat": "2023-09-26T07:35:05.468Z",
        "measurements": [
            "energy",
            "energy",
            "power",
            "relay"
        ]
    },
    {
        "deviceid": "domxem3-349454719423",
        "device_type_text": "3-phase EM",
        "device_name": "281-meter",
        "device_type": 2,
        "home_id": "281",
        "registeredat": "2023-09-20T08:02:44.710Z",
        "measurements": [
            "energy",
            "returned_energy",
            "current",
            "energy",
            "pf",
            "power",
            "returned_energy",
            "total",
            "total_returned",
            "voltage",
            "relay"
        ]
    },
    {
        "deviceid": "domxem3-244CAB4353DB",
        "device_type_text": "3-phase EM",
        "device_name": "289-meter",
        "device_type": 2,
        "home_id": "289",
        "registeredat": "2023-09-19T09:38:37.723Z",
        "measurements": [
            "energy",
            "returned_energy",
            "current",
            "energy",
            "pf",
            "power",
            "returned_energy",
            "total",
            "total_returned",
            "voltage",
            "relay"
        ]
    },
    {
        "deviceid": "shellyplug-s-C8C9A3A5CA8F",
        "device_type_text": "Shelly Plug S",
        "device_name": "284-TV",
        "device_type": 5,
        "home_id": "284",
        "registeredat": "2023-09-13T18:04:39.047Z",
        "measurements": [
            "energy",
            "energy",
            "power",
            "relay"
        ]
    },
    {
        "deviceid": "domxplug-C19AEE",
        "device_type_text": "Shelly Plug",
        "device_name": "284-DW",
        "device_type": 4,
        "home_id": "284",
        "registeredat": "2023-09-13T18:04:04.350Z",
        "measurements": [
            "energy",
            "energy",
            "power",
            "relay"
        ]
    },
    {
        "deviceid": "domxem3-244CAB4356D1",
        "device_type_text": "3-phase EM",
        "device_name": "285-meter-EV",
        "device_type": 2,
        "home_id": "285",
        "registeredat": "2023-09-13T18:03:05.346Z",
        "measurements": [
            "energy",
            "returned_energy",
            "current",
            "energy",
            "pf",
            "power",
            "returned_energy",
            "total",
            "total_returned",
            "voltage",
            "relay"
        ]
    },
    {
        "deviceid": "domxem3-244CAB436229",
        "device_type_text": "3-phase EM",
        "device_name": "284-meter",
        "device_type": 2,
        "home_id": "284",
        "registeredat": "2023-09-13T18:01:16.468Z",
        "measurements": [
            "energy",
            "returned_energy",
            "current",
            "energy",
            "pf",
            "power",
            "returned_energy",
            "total",
            "total_returned",
            "voltage",
            "relay"
        ]
    },
    {
        "deviceid": "domxplug-8FF852",
        "device_type_text": "Shelly Plug",
        "device_name": "39-A/C Living Room",
        "device_type": 4,
        "home_id": "39",
        "registeredat": "2023-07-31T08:59:30.181Z",
        "measurements": [
            "energy",
            "energy",
            "power",
            "relay"
        ]
    },
    {
        "deviceid": "domxplug-8F8991",
        "device_type_text": "Shelly Plug",
        "device_name": "130-A/C Bedroom2",
        "device_type": 4,
        "home_id": "130",
        "registeredat": "2023-07-31T08:57:49.065Z",
        "measurements": [
            "energy",
            "energy",
            "power",
            "relay"
        ]
    },
    {
        "deviceid": "domxplug-8FF464",
        "device_type_text": "Shelly Plug",
        "device_name": "130-A/C Living Room",
        "device_type": 4,
        "home_id": "130",
        "registeredat": "2023-07-31T08:57:10.077Z",
        "measurements": [
            "energy",
            "energy",
            "power",
            "relay"
        ]
    },
    {
        "deviceid": "domxplug-900030",
        "device_type_text": "Shelly Plug",
        "device_name": "81-A/C 3",
        "device_type": 4,
        "home_id": "81",
        "registeredat": "2023-07-21T11:25:09.111Z",
        "measurements": [
            "energy",
            "energy",
            "power",
            "relay"
        ]
    },
    {
        "deviceid": "domxplug-90002F",
        "device_type_text": "Shelly Plug",
        "device_name": "81-A/C Living Room",
        "device_type": 4,
        "home_id": "81",
        "registeredat": "2023-07-21T11:24:40.531Z",
        "measurements": [
            "energy",
            "energy",
            "power",
            "relay"
        ]
    },
    {
        "deviceid": "domxplug-8FF5B3",
        "device_type_text": "Shelly Plug",
        "device_name": "81-A/C Dining Room",
        "device_type": 4,
        "home_id": "81",
        "registeredat": "2023-07-21T11:24:06.687Z",
        "measurements": [
            "energy",
            "energy",
            "power",
            "relay"
        ]
    },
    {
        "deviceid": "domxem3-C8C9A37059DE",
        "device_type_text": "3-phase EM",
        "device_name": "280-meter",
        "device_type": 2,
        "home_id": "280",
        "registeredat": "2023-07-17T13:08:55.979Z",
        "measurements": [
            "energy",
            "returned_energy",
            "current",
            "energy",
            "pf",
            "power",
            "returned_energy",
            "total",
            "total_returned",
            "voltage",
            "relay"
        ]
    },
    {
        "deviceid": "shellyplug-s-4022D88E369D",
        "device_type_text": "Shelly Plug S",
        "device_name": "280-TV",
        "device_type": 5,
        "home_id": "280",
        "registeredat": "2023-07-17T13:06:07.456Z",
        "measurements": [
            "energy",
            "energy",
            "power",
            "relay"
        ]
    },
    {
        "deviceid": "domxplug-C16066",
        "device_type_text": "Shelly Plug",
        "device_name": "280-WM",
        "device_type": 4,
        "home_id": "280",
        "registeredat": "2023-07-17T13:04:20.108Z",
        "measurements": [
            "energy",
            "energy",
            "power",
            "relay"
        ]
    },
    {
        "deviceid": "shellyplug-s-7C87CEB4A329",
        "device_type_text": "Shelly Plug S",
        "device_name": "292-TV",
        "device_type": 5,
        "home_id": "292",
        "registeredat": "2023-07-17T09:33:44.651Z",
        "measurements": [
            "energy",
            "power",
            "relay"
        ]
    },
    {
        "deviceid": "domxplug-8F8980",
        "device_type_text": "Shelly Plug",
        "device_name": "292-Dryer",
        "device_type": 4,
        "home_id": "292",
        "registeredat": "2023-07-17T09:33:01.159Z",
        "measurements": [
            "energy",
            "energy",
            "power",
            "relay"
        ]
    },
    {
        "deviceid": "domxplug-90004F",
        "device_type_text": "Shelly Plug",
        "device_name": "292-WM",
        "device_type": 4,
        "home_id": "292",
        "registeredat": "2023-07-17T09:32:12.434Z",
        "measurements": [
            "energy",
            "energy",
            "power",
            "relay"
        ]
    },
    {
        "deviceid": "domxem3-C8C9A3705C4F",
        "device_type_text": "3-phase EM",
        "device_name": "292-meter",
        "device_type": 2,
        "home_id": "292",
        "registeredat": "2023-07-17T09:27:33.640Z",
        "measurements": [
            "energy",
            "current",
            "energy",
            "pf",
            "power",
            "returned_energy",
            "total",
            "total_returned",
            "voltage",
            "relay"
        ]
    },
    {
        "deviceid": "domxplug-8FFAF9",
        "device_type_text": "Shelly Plug",
        "device_name": "270-A/C",
        "device_type": 4,
        "home_id": "270",
        "registeredat": "2023-07-14T10:33:28.989Z",
        "measurements": [
            "energy",
            "energy",
            "power",
            "relay"
        ]
    },
    {
        "deviceid": "domxplug-8FF1F4",
        "device_type_text": "Shelly Plug",
        "device_name": "270-DW",
        "device_type": 4,
        "home_id": "270",
        "registeredat": "2023-07-14T10:32:49.465Z",
        "measurements": [
            "energy",
            "energy",
            "power",
            "relay"
        ]
    },
    {
        "deviceid": "domxplug-9002A5",
        "device_type_text": "Shelly Plug",
        "device_name": "270-WM-Hoover",
        "device_type": 4,
        "home_id": "270",
        "registeredat": "2023-07-14T10:31:44.423Z",
        "measurements": [
            "energy",
            "energy",
            "power",
            "relay"
        ]
    },
    {
        "deviceid": "domxem3-244CAB435699",
        "device_type_text": "3-phase EM",
        "device_name": "273-meter-EV",
        "device_type": 2,
        "home_id": "263",
        "registeredat": "2023-03-30T08:36:51.672Z",
        "measurements": [
            "energy",
            "current",
            "energy",
            "pf",
            "power",
            "returned_energy",
            "total",
            "total_returned",
            "voltage",
            "relay"
        ]
    },
    {
        "deviceid": "shellyplug-s-C1AE2F",
        "device_type_text": "Shelly Plug S",
        "device_name": "272-TV",
        "device_type": 5,
        "home_id": "272",
        "registeredat": "2023-03-30T08:30:28.184Z",
        "measurements": [
            "energy",
            "energy",
            "power",
            "relay"
        ]
    },
    {
        "deviceid": "domxplug-286A3F",
        "device_type_text": "Shelly Plug",
        "device_name": "272-DW",
        "device_type": 4,
        "home_id": "272",
        "registeredat": "2023-03-30T08:30:02.932Z",
        "measurements": [
            "energy",
            "energy",
            "power",
            "relay"
        ]
    },
    {
        "deviceid": "shellyplug-s-D9B0E6",
        "device_type_text": "Shelly Plug S",
        "device_name": "262-TV",
        "device_type": 5,
        "home_id": "262",
        "registeredat": "2023-03-30T08:09:47.491Z",
        "measurements": [
            "energy",
            "energy",
            "power",
            "relay"
        ]
    },
    {
        "deviceid": "domxplug-C152C9",
        "device_type_text": "Shelly Plug",
        "device_name": "262-AC",
        "device_type": 4,
        "home_id": "262",
        "registeredat": "2023-03-30T08:09:18.534Z",
        "measurements": [
            "energy",
            "energy",
            "power",
            "relay"
        ]
    },
    {
        "deviceid": "domxplug-C16646",
        "device_type_text": "Shelly Plug",
        "device_name": "262-WM",
        "device_type": 4,
        "home_id": "262",
        "registeredat": "2023-03-30T08:08:55.654Z",
        "measurements": [
            "energy",
            "energy",
            "power",
            "relay"
        ]
    },
    {
        "deviceid": "domxem3-485519C9BBAA",
        "device_type_text": "3-phase EM",
        "device_name": "262-meter",
        "device_type": 2,
        "home_id": "262",
        "registeredat": "2023-03-30T08:08:20.340Z",
        "measurements": [
            "energy",
            "returned_energy",
            "current",
            "energy",
            "pf",
            "power",
            "returned_energy",
            "total",
            "total_returned",
            "voltage",
            "relay"
        ]
    },
    {
        "deviceid": "domxem3-485519C9C37E",
        "device_type_text": "3-phase EM",
        "device_name": "272-meter",
        "device_type": 2,
        "home_id": "272",
        "registeredat": "2023-03-29T09:56:08.527Z",
        "measurements": [
            "energy",
            "returned_energy",
            "current",
            "energy",
            "pf",
            "power",
            "returned_energy",
            "total",
            "total_returned",
            "voltage",
            "relay"
        ]
    },
    {
        "deviceid": "shellyplug-s-F1BA46",
        "device_type_text": "Shelly Plug S",
        "device_name": "263-TV",
        "device_type": 5,
        "home_id": "263",
        "registeredat": "2023-03-29T09:26:32.308Z",
        "measurements": [
            "energy",
            "energy",
            "power",
            "relay"
        ]
    },
    {
        "deviceid": "domxplug-C19758",
        "device_type_text": "Shelly Plug",
        "device_name": "263-DW",
        "device_type": 4,
        "home_id": "263",
        "registeredat": "2023-03-29T09:25:56.977Z",
        "measurements": [
            "energy",
            "energy",
            "power",
            "relay"
        ]
    },
    {
        "deviceid": "domxplug-2CA74F",
        "device_type_text": "Shelly Plug",
        "device_name": "263-WM/Dr",
        "device_type": 4,
        "home_id": "263",
        "registeredat": "2023-03-29T09:13:35.476Z",
        "measurements": [
            "energy",
            "energy",
            "power",
            "relay"
        ]
    },
    {
        "deviceid": "domxem3-3494546EC9F0",
        "device_type_text": "3-phase EM",
        "device_name": "263-meter",
        "device_type": 2,
        "home_id": "263",
        "registeredat": "2023-03-29T09:12:43.264Z",
        "measurements": [
            "energy",
            "current",
            "energy",
            "pf",
            "power",
            "returned_energy",
            "total",
            "total_returned",
            "voltage",
            "relay"
        ]
    },
    {
        "deviceid": "shellyplug-s-6EDFFE",
        "device_type_text": "Shelly Plug S",
        "device_name": "265-TV",
        "device_type": 5,
        "home_id": "265",
        "registeredat": "2023-03-29T07:37:55.078Z",
        "measurements": [
            "energy",
            "energy",
            "power",
            "relay"
        ]
    },
    {
        "deviceid": "domxplug-286C52",
        "device_type_text": "Shelly Plug",
        "device_name": "265-WM",
        "device_type": 4,
        "home_id": "265",
        "registeredat": "2023-03-29T07:37:28.381Z",
        "measurements": [
            "energy",
            "energy",
            "power",
            "relay"
        ]
    },
    {
        "deviceid": "domxplug-C1C45B",
        "device_type_text": "Shelly Plug",
        "device_name": "265-A/C",
        "device_type": 4,
        "home_id": "265",
        "registeredat": "2023-03-29T07:37:03.901Z",
        "measurements": [
            "energy",
            "energy",
            "power",
            "relay"
        ]
    },
    {
        "deviceid": "domxem3-C8C9A3705052",
        "device_type_text": "3-phase EM",
        "device_name": "265-meter",
        "device_type": 2,
        "home_id": "265",
        "registeredat": "2023-03-29T07:36:29.964Z",
        "measurements": [
            "energy",
            "returned_energy",
            "current",
            "energy",
            "pf",
            "power",
            "returned_energy",
            "total",
            "total_returned",
            "voltage",
            "relay"
        ]
    },
    {
        "deviceid": "shellyplug-s-F1B8D8",
        "device_type_text": "Shelly Plug S",
        "device_name": "264-TV",
        "device_type": 5,
        "home_id": "264",
        "registeredat": "2023-03-28T07:04:11.438Z",
        "measurements": [
            "energy",
            "energy",
            "power",
            "relay"
        ]
    },
    {
        "deviceid": "domxplug-2CC4F6",
        "device_type_text": "Shelly Plug",
        "device_name": "264-A/C",
        "device_type": 4,
        "home_id": "264",
        "registeredat": "2023-03-28T07:03:45.258Z",
        "measurements": [
            "energy",
            "energy",
            "power",
            "relay"
        ]
    },
    {
        "deviceid": "domxplug-C15A17",
        "device_type_text": "Shelly Plug",
        "device_name": "264-WM",
        "device_type": 4,
        "home_id": "264",
        "registeredat": "2023-03-28T07:03:19.740Z",
        "measurements": [
            "energy",
            "energy",
            "power",
            "relay"
        ]
    },
    {
        "deviceid": "domxem3-3494546ED3B7",
        "device_type_text": "3-phase EM",
        "device_name": "264-meter",
        "device_type": 2,
        "home_id": "264",
        "registeredat": "2023-03-28T07:01:25.352Z",
        "measurements": [
            "energy",
            "returned_energy",
            "current",
            "energy",
            "pf",
            "power",
            "returned_energy",
            "total",
            "total_returned",
            "voltage",
            "relay"
        ]
    },
    {
        "deviceid": "shellyplug-s-6F608E",
        "device_type_text": "Shelly Plug S",
        "device_name": "276-TV",
        "device_type": 5,
        "home_id": "276",
        "registeredat": "2023-01-13T08:38:27.467Z",
        "measurements": [
            "energy",
            "energy",
            "power",
            "relay"
        ]
    },
    {
        "deviceid": "domxplug-C1514C",
        "device_type_text": "Shelly Plug",
        "device_name": "276-DW",
        "device_type": 4,
        "home_id": "276",
        "registeredat": "2023-01-13T08:37:36.492Z",
        "measurements": [
            "energy",
            "energy",
            "power",
            "relay"
        ]
    },
    {
        "deviceid": "domxem3-C8C9A370578A",
        "device_type_text": "3-phase EM",
        "device_name": "276-meter",
        "device_type": 2,
        "home_id": "276",
        "registeredat": "2023-01-13T08:36:02.746Z",
        "measurements": [
            "energy",
            "returned_energy",
            "current",
            "energy",
            "pf",
            "power",
            "returned_energy",
            "total",
            "total_returned",
            "voltage",
            "relay"
        ]
    },
    {
        "deviceid": "domxplug-2845DA",
        "device_type_text": "Shelly Plug",
        "device_name": "250-WM/Dr",
        "device_type": 4,
        "home_id": "250",
        "registeredat": "2023-01-04T16:04:29.953Z",
        "measurements": [
            "energy",
            "energy",
            "power",
            "relay"
        ]
    },
    {
        "deviceid": "shellyplug-s-ECBF52",
        "device_type_text": "Shelly Plug S",
        "device_name": "250-TV",
        "device_type": 5,
        "home_id": "250",
        "registeredat": "2023-01-04T16:03:58.740Z",
        "measurements": [
            "energy",
            "energy",
            "power",
            "relay"
        ]
    },
    {
        "deviceid": "domxplug-283B9D",
        "device_type_text": "Shelly Plug",
        "device_name": "197-WM",
        "device_type": 4,
        "home_id": "197",
        "registeredat": "2023-01-03T16:03:39.979Z",
        "measurements": [
            "energy",
            "energy",
            "power",
            "relay"
        ]
    },
    {
        "deviceid": "domxplug-C19B0E",
        "device_type_text": "Shelly Plug",
        "device_name": "81-Dishwasher-(S)",
        "device_type": 4,
        "home_id": "81",
        "registeredat": "2022-12-16T12:58:55.542Z",
        "measurements": [
            "energy",
            "energy",
            "power",
            "relay"
        ]
    },
    {
        "deviceid": "domxplug-2BA3BE",
        "device_type_text": "Shelly Plug",
        "device_name": "145-WM",
        "device_type": 4,
        "home_id": "145",
        "registeredat": "2022-12-14T13:18:44.341Z",
        "measurements": [
            "energy",
            "energy",
            "power",
            "relay"
        ]
    },
    {
        "deviceid": "domxplug-C14B8F",
        "device_type_text": "Shelly Plug",
        "device_name": "145-DW",
        "device_type": 4,
        "home_id": "145",
        "registeredat": "2022-12-14T13:17:54.595Z",
        "measurements": [
            "energy",
            "energy",
            "power",
            "relay"
        ]
    },
    {
        "deviceid": "shellyplug-s-C119AC",
        "device_type_text": "Shelly Plug S",
        "device_name": "145-TV",
        "device_type": 5,
        "home_id": "145",
        "registeredat": "2022-12-14T13:17:09.279Z",
        "measurements": [
            "energy",
            "energy",
            "power",
            "relay"
        ]
    },
    {
        "deviceid": "shellyplug-s-C0FE7E",
        "device_type_text": "Shelly Plug S",
        "device_name": "200-TV",
        "device_type": 5,
        "home_id": "200",
        "registeredat": "2022-12-14T09:44:28.529Z",
        "measurements": [
            "energy",
            "energy",
            "power",
            "relay"
        ]
    },
    {
        "deviceid": "domxplug-286F34",
        "device_type_text": "Shelly Plug",
        "device_name": "200-DW",
        "device_type": 4,
        "home_id": "200",
        "registeredat": "2022-12-14T09:44:01.231Z",
        "measurements": [
            "energy",
            "energy",
            "power",
            "relay"
        ]
    },
    {
        "deviceid": "domxplug-2CA084",
        "device_type_text": "Shelly Plug",
        "device_name": "200-WM",
        "device_type": 4,
        "home_id": "200",
        "registeredat": "2022-12-14T09:43:23.804Z",
        "measurements": [
            "energy",
            "energy",
            "power",
            "relay"
        ]
    },
    {
        "deviceid": "domxem3-3494547194C7",
        "device_type_text": "3-phase EM",
        "device_name": "252-meter",
        "device_type": 2,
        "home_id": "252",
        "registeredat": "2022-12-07T17:12:09.824Z",
        "measurements": [
            "energy",
            "returned_energy",
            "current",
            "energy",
            "pf",
            "power",
            "returned_energy",
            "total",
            "total_returned",
            "voltage",
            "relay"
        ]
    },
    {
        "deviceid": "shellyplug-s-ECF394",
        "device_type_text": "Shelly Plug S",
        "device_name": "252-PC",
        "device_type": 5,
        "home_id": "252",
        "registeredat": "2022-12-07T11:04:30.934Z",
        "measurements": [
            "energy",
            "energy",
            "power",
            "relay"
        ]
    },
    {
        "deviceid": "domxplug-284456",
        "device_type_text": "Shelly Plug",
        "device_name": "252-A/C Living Room",
        "device_type": 4,
        "home_id": "252",
        "registeredat": "2022-12-07T11:03:31.528Z",
        "measurements": [
            "energy",
            "energy",
            "power",
            "relay"
        ]
    },
    {
        "deviceid": "domxplug-2847A0",
        "device_type_text": "Shelly Plug",
        "device_name": "252-A/C Office",
        "device_type": 4,
        "home_id": "252",
        "registeredat": "2022-12-07T10:48:20.434Z",
        "measurements": [
            "energy",
            "energy",
            "power",
            "relay"
        ]
    },
    {
        "deviceid": "shellyplug-s-ED979C",
        "device_type_text": "Shelly Plug S",
        "device_name": "197-TV",
        "device_type": 5,
        "home_id": "197",
        "registeredat": "2022-12-07T10:47:43.497Z",
        "measurements": [
            "energy",
            "energy",
            "power",
            "relay"
        ]
    },
    {
        "deviceid": "domxplug-283D60",
        "device_type_text": "Shelly Plug",
        "device_name": "197-A/C",
        "device_type": 4,
        "home_id": "197",
        "registeredat": "2022-12-07T10:47:20.550Z",
        "measurements": [
            "energy",
            "energy",
            "power",
            "relay"
        ]
    },
    {
        "deviceid": "domxem3-485519C9780F",
        "device_type_text": "3-phase EM w/ Relay",
        "device_name": "197-meter-boiler-P2",
        "device_type": 7,
        "home_id": "197",
        "registeredat": "2022-12-07T10:45:20.572Z",
        "measurements": [
            "energy",
            "returned_energy",
            "current",
            "energy",
            "pf",
            "power",
            "returned_energy",
            "total",
            "total_returned",
            "voltage",
            "relay"
        ]
    },
    {
        "deviceid": "domxem3-485519C979E2",
        "device_type_text": "3-phase EM w/ Relay",
        "device_name": "200-meter-boiler-P2",
        "device_type": 7,
        "home_id": "200",
        "registeredat": "2022-12-07T10:43:20.119Z",
        "measurements": [
            "energy",
            "current",
            "energy",
            "pf",
            "power",
            "returned_energy",
            "total",
            "total_returned",
            "voltage",
            "relay"
        ]
    },
    {
        "deviceid": "domxem3-C8C9A3705CD1",
        "device_type_text": "3-phase EM",
        "device_name": "250-meter",
        "device_type": 2,
        "home_id": "250",
        "registeredat": "2022-12-07T10:41:30.900Z",
        "measurements": [
            "energy",
            "current",
            "energy",
            "pf",
            "power",
            "returned_energy",
            "total",
            "total_returned",
            "voltage",
            "relay"
        ]
    },
    {
        "deviceid": "shellyplug-s-2219F9",
        "device_type_text": "Shelly Plug S",
        "device_name": "196-TV",
        "device_type": 5,
        "home_id": "196",
        "registeredat": "2022-12-04T11:38:25.178Z",
        "measurements": [
            "energy",
            "energy",
            "power",
            "relay"
        ]
    },
    {
        "deviceid": "shellyplug-s-F1C2FB",
        "device_type_text": "Shelly Plug S",
        "device_name": "36-TV",
        "device_type": 5,
        "home_id": "36",
        "registeredat": "2022-11-28T08:58:17.217Z",
        "measurements": [
            "energy",
            "energy",
            "power",
            "relay"
        ]
    },
    {
        "deviceid": "shellyplug-s-D9B4B9",
        "device_type_text": "Shelly Plug S",
        "device_name": "195-TV",
        "device_type": 5,
        "home_id": "195",
        "registeredat": "2022-11-21T16:36:51.169Z",
        "measurements": [
            "energy",
            "energy",
            "power",
            "relay"
        ]
    },
    {
        "deviceid": "domxplug-284336",
        "device_type_text": "Shelly Plug",
        "device_name": "195-A/C",
        "device_type": 4,
        "home_id": "195",
        "registeredat": "2022-11-21T16:36:24.451Z",
        "measurements": [
            "energy",
            "energy",
            "power",
            "relay"
        ]
    },
    {
        "deviceid": "domxplug-2844D0",
        "device_type_text": "Shelly Plug",
        "device_name": "195-DW",
        "device_type": 4,
        "home_id": "195",
        "registeredat": "2022-11-21T16:35:52.341Z",
        "measurements": [
            "energy",
            "energy",
            "power",
            "relay"
        ]
    },
    {
        "deviceid": "shellyplug-s-D9AEB4",
        "device_type_text": "Shelly Plug S",
        "device_name": "194-TV",
        "device_type": 5,
        "home_id": "194",
        "registeredat": "2022-11-21T16:35:13.639Z",
        "measurements": [
            "energy",
            "energy",
            "power",
            "relay"
        ]
    },
    {
        "deviceid": "domxplug-28486E",
        "device_type_text": "Shelly Plug",
        "device_name": "194-A/C",
        "device_type": 4,
        "home_id": "194",
        "registeredat": "2022-11-21T16:34:52.648Z",
        "measurements": [
            "energy",
            "energy",
            "power",
            "relay"
        ]
    },
    {
        "deviceid": "domxplug-E0AFBA",
        "device_type_text": "Shelly Plug",
        "device_name": "194-WM",
        "device_type": 4,
        "home_id": "194",
        "registeredat": "2022-11-21T16:34:26.802Z",
        "measurements": [
            "energy",
            "energy",
            "power",
            "relay"
        ]
    },
    {
        "deviceid": "shellyplug-s-F13DA4",
        "device_type_text": "Shelly Plug S",
        "device_name": "136-TV",
        "device_type": 5,
        "home_id": "136",
        "registeredat": "2022-11-21T16:31:34.379Z",
        "measurements": [
            "energy",
            "energy",
            "power",
            "relay"
        ]
    },
    {
        "deviceid": "domxplug-284632",
        "device_type_text": "Shelly Plug",
        "device_name": "136-WM",
        "device_type": 4,
        "home_id": "136",
        "registeredat": "2022-11-21T16:31:14.957Z",
        "measurements": [
            "energy",
            "energy",
            "power",
            "relay"
        ]
    },
    {
        "deviceid": "domxplug-2841C9",
        "device_type_text": "Shelly Plug",
        "device_name": "136-AC",
        "device_type": 4,
        "home_id": "136",
        "registeredat": "2022-11-21T16:30:47.614Z",
        "measurements": [
            "energy",
            "energy",
            "power",
            "relay"
        ]
    },
    {
        "deviceid": "shellyplug-s-224371",
        "device_type_text": "Shelly Plug S",
        "device_name": "130-TV",
        "device_type": 5,
        "home_id": "130",
        "registeredat": "2022-11-21T16:13:25.900Z",
        "measurements": [
            "energy",
            "energy",
            "power",
            "relay"
        ]
    },
    {
        "deviceid": "domxplug-284409",
        "device_type_text": "Shelly Plug",
        "device_name": "130-WM",
        "device_type": 4,
        "home_id": "130",
        "registeredat": "2022-11-21T16:13:03.496Z",
        "measurements": [
            "energy",
            "energy",
            "power",
            "relay"
        ]
    },
    {
        "deviceid": "domxplug-283E8A",
        "device_type_text": "Shelly Plug",
        "device_name": "130-A/C Bedroom1",
        "device_type": 4,
        "home_id": "130",
        "registeredat": "2022-11-21T16:12:30.646Z",
        "measurements": [
            "energy",
            "energy",
            "power",
            "relay"
        ]
    },
    {
        "deviceid": "domxplug-E0AF97",
        "device_type_text": "Shelly Plug",
        "device_name": "127-WM",
        "device_type": 4,
        "home_id": "127",
        "registeredat": "2022-11-21T16:08:57.462Z",
        "measurements": [
            "energy",
            "energy",
            "power",
            "relay"
        ]
    },
    {
        "deviceid": "domxplug-2840CB",
        "device_type_text": "Shelly Plug",
        "device_name": "127-DW",
        "device_type": 4,
        "home_id": "127",
        "registeredat": "2022-11-21T16:08:32.352Z",
        "measurements": [
            "energy",
            "energy",
            "power",
            "relay"
        ]
    },
    {
        "deviceid": "shellyplug-s-F14B29",
        "device_type_text": "Shelly Plug S",
        "device_name": "95-TV",
        "device_type": 5,
        "home_id": "95",
        "registeredat": "2022-11-21T16:05:03.356Z",
        "measurements": [
            "energy",
            "energy",
            "power",
            "relay"
        ]
    },
    {
        "deviceid": "domxplug-284897",
        "device_type_text": "Shelly Plug",
        "device_name": "95-WM",
        "device_type": 4,
        "home_id": "95",
        "registeredat": "2022-11-21T16:04:36.436Z",
        "measurements": [
            "energy",
            "energy",
            "power",
            "relay"
        ]
    },
    {
        "deviceid": "domxplug-28471E",
        "device_type_text": "Shelly Plug",
        "device_name": "95-A/C",
        "device_type": 4,
        "home_id": "95",
        "registeredat": "2022-11-21T16:04:03.340Z",
        "measurements": [
            "energy",
            "energy",
            "overpower_value",
            "power",
            "relay"
        ]
    },
    {
        "deviceid": "shellyplug-s-F143AC",
        "device_type_text": "Shelly Plug S",
        "device_name": "81-TV",
        "device_type": 5,
        "home_id": "81",
        "registeredat": "2022-11-21T16:03:04.823Z",
        "measurements": [
            "energy",
            "energy",
            "power",
            "relay"
        ]
    },
    {
        "deviceid": "domxplug-2846B6",
        "device_type_text": "Shelly Plug",
        "device_name": "81-WM",
        "device_type": 4,
        "home_id": "81",
        "registeredat": "2022-11-21T16:02:22.528Z",
        "measurements": [
            "energy",
            "energy",
            "power",
            "relay"
        ]
    },
    {
        "deviceid": "shellyplug-s-D9DEBE",
        "device_type_text": "Shelly Plug S",
        "device_name": "126-TV",
        "device_type": 5,
        "home_id": "126",
        "registeredat": "2022-11-16T11:25:23.887Z",
        "measurements": [
            "energy",
            "energy",
            "power",
            "relay"
        ]
    },
    {
        "deviceid": "domxplug-28467C",
        "device_type_text": "Shelly Plug",
        "device_name": "126-WM",
        "device_type": 4,
        "home_id": "126",
        "registeredat": "2022-11-15T14:02:55.219Z",
        "measurements": [
            "energy",
            "energy",
            "power",
            "relay"
        ]
    },
    {
        "deviceid": "domxem3-3494547192C2",
        "device_type_text": "3-phase EM",
        "device_name": "196-meter",
        "device_type": 2,
        "home_id": "196",
        "registeredat": "2022-11-15T13:49:20.690Z",
        "measurements": [
            "energy",
            "returned_energy",
            "current",
            "energy",
            "pf",
            "power",
            "returned_energy",
            "total",
            "total_returned",
            "voltage",
            "relay"
        ]
    },
    {
        "deviceid": "shellyplug-s-2295BC",
        "device_type_text": "Shelly Plug S",
        "device_name": "39-TV",
        "device_type": 5,
        "home_id": "39",
        "registeredat": "2022-11-09T21:08:23.107Z",
        "measurements": [
            "energy",
            "energy",
            "power",
            "relay"
        ]
    },
    {
        "deviceid": "domxplug-2842FB",
        "device_type_text": "Shelly Plug",
        "device_name": "39-DW",
        "device_type": 4,
        "home_id": "39",
        "registeredat": "2022-11-09T21:07:43.036Z",
        "measurements": [
            "energy",
            "energy",
            "overpower_value",
            "power",
            "relay"
        ]
    },
    {
        "deviceid": "domxplug-2845C2",
        "device_type_text": "Shelly Plug",
        "device_name": "39-WMDr",
        "device_type": 4,
        "home_id": "39",
        "registeredat": "2022-11-09T21:06:38.572Z",
        "measurements": [
            "energy",
            "energy",
            "power",
            "relay"
        ]
    },
    {
        "deviceid": "domxem3-485519C91061",
        "device_type_text": "3-phase EM",
        "device_name": "195-meter",
        "device_type": 2,
        "home_id": "195",
        "registeredat": "2022-07-28T09:25:07.875Z",
        "measurements": [
            "energy",
            "current",
            "energy",
            "pf",
            "power",
            "returned_energy",
            "total",
            "total_returned",
            "voltage",
            "relay"
        ]
    },
    {
        "deviceid": "domxem3-349454717054",
        "device_type_text": "3-phase EM",
        "device_name": "194-meter",
        "device_type": 2,
        "home_id": "194",
        "registeredat": "2022-07-28T09:24:33.709Z",
        "measurements": [
            "energy",
            "returned_energy",
            "current",
            "energy",
            "pf",
            "power",
            "returned_energy",
            "total",
            "total_returned",
            "voltage",
            "relay"
        ]
    },
    {
        "deviceid": "domxem3-C82B9611688B",
        "device_type_text": "3-phase EM",
        "device_name": "130-meter",
        "device_type": 2,
        "home_id": "130",
        "registeredat": "2022-07-28T09:20:36.176Z",
        "measurements": [
            "energy",
            "returned_energy",
            "current",
            "energy",
            "pf",
            "power",
            "returned_energy",
            "total",
            "total_returned",
            "voltage",
            "relay"
        ]
    },
    {
        "deviceid": "domxem3-C82B96116913",
        "device_type_text": "3-phase EM",
        "device_name": "136-meter",
        "device_type": 2,
        "home_id": "136",
        "registeredat": "2022-07-23T12:56:07.351Z",
        "measurements": [
            "energy",
            "returned_energy",
            "current",
            "energy",
            "pf",
            "power",
            "returned_energy",
            "total",
            "total_returned",
            "voltage",
            "relay"
        ]
    },
    {
        "deviceid": "domxem3-68C63AFB3BF6",
        "device_type_text": "3-phase EM",
        "device_name": "127-meter",
        "device_type": 2,
        "home_id": "127",
        "registeredat": "2022-07-15T07:44:42.726Z",
        "measurements": [
            "energy",
            "returned_energy",
            "current",
            "energy",
            "pf",
            "power",
            "returned_energy",
            "total",
            "total_returned",
            "voltage",
            "relay"
        ]
    },
    {
        "deviceid": "domxem3-68C63AFB1F30",
        "device_type_text": "3-phase EM w/ Relay",
        "device_name": "126-meter-relay-P2",
        "device_type": 7,
        "home_id": "126",
        "registeredat": "2022-07-13T17:32:18.883Z",
        "measurements": [
            "energy",
            "returned_energy",
            "current",
            "energy",
            "pf",
            "power",
            "returned_energy",
            "total",
            "total_returned",
            "voltage",
            "relay"
        ]
    },
    {
        "deviceid": "domxem3-C82B96116354",
        "device_type_text": "3-phase EM",
        "device_name": "138-meter",
        "device_type": 2,
        "home_id": "138",
        "registeredat": "2022-05-19T12:30:28.960Z",
        "measurements": [
            "energy",
            "current",
            "energy",
            "pf",
            "power",
            "returned_energy",
            "total",
            "total_returned",
            "voltage",
            "relay"
        ]
    },
    {
        "deviceid": "domxem3-C82B9610EA08",
        "device_type_text": "3-phase EM",
        "device_name": "145-meter",
        "device_type": 2,
        "home_id": "145",
        "registeredat": "2022-05-12T15:54:33.374Z",
        "measurements": [
            "energy",
            "returned_energy",
            "current",
            "energy",
            "pf",
            "power",
            "returned_energy",
            "total",
            "total_returned",
            "voltage",
            "relay"
        ]
    },
    {
        "deviceid": "domxem3-C82B9611633D",
        "device_type_text": "3-phase EM",
        "device_name": "123-meter",
        "device_type": 2,
        "home_id": "123",
        "registeredat": "2021-06-29T15:00:06.110Z",
        "measurements": [
            "energy",
            "current",
            "energy",
            "pf",
            "power",
            "returned_energy",
            "total",
            "total_returned",
            "voltage",
            "relay"
        ]
    },
    {
        "deviceid": "domxem3-FCF5C49641CF",
        "device_type_text": "3-phase EM",
        "device_name": "114-meter",
        "device_type": 2,
        "home_id": "114",
        "registeredat": "2021-06-09T13:32:08.023Z",
        "measurements": [
            "energy",
            "returned_energy",
            "current",
            "energy",
            "pf",
            "power",
            "reactive_power",
            "returned_energy",
            "total",
            "total_returned",
            "voltage",
            "relay"
        ]
    },
    {
        "deviceid": "domxem3-ECFABCC7F071",
        "device_type_text": "3-phase EM",
        "device_name": "39-meter",
        "device_type": 2,
        "home_id": "39",
        "registeredat": "2021-06-03T10:03:24.267Z",
        "measurements": [
            "energy",
            "returned_energy",
            "current",
            "energy",
            "pf",
            "power",
            "reactive_power",
            "returned_energy",
            "total",
            "total_returned",
            "voltage",
            "relay"
        ]
    },
    {
        "deviceid": "domxem3-ECFABCC7F0FF",
        "device_type_text": "3-phase EM",
        "device_name": "36-meter",
        "device_type": 2,
        "home_id": "36",
        "registeredat": "2021-05-28T13:15:29.470Z",
        "measurements": [
            "energy",
            "returned_energy",
            "current",
            "energy",
            "pf",
            "power",
            "reactive_power",
            "returned_energy",
            "total",
            "total_returned",
            "voltage",
            "relay"
        ]
    },
    {
        "deviceid": "domxem-C7F4EB",
        "device_type_text": "1-phase EM",
        "device_name": "95-meter",
        "device_type": 1,
        "home_id": "95",
        "registeredat": "2021-03-19T13:48:23.344Z",
        "measurements": [
            "energy",
            "returned_energy",
            "energy",
            "pf",
            "power",
            "reactive_power",
            "returned_energy",
            "total",
            "total_returned",
            "voltage",
            "relay"
        ]
    },
    {
        "deviceid": "domxem-C7FCB5",
        "device_type_text": "1-phase EM",
        "device_name": "81-meter",
        "device_type": 1,
        "home_id": "81",
        "registeredat": "2021-03-11T11:35:46.393Z",
        "measurements": [
            "energy",
            "returned_energy",
            "energy",
            "pf",
            "power",
            "reactive_power",
            "returned_energy",
            "total",
            "total_returned",
            "voltage",
            "relay"
        ]
    }
          
]

SPARE_HISTORY = []
