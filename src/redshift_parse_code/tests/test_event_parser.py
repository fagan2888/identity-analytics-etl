import unittest
import sys
import os
import json

from context import EventParser
from io import BytesIO


class EventParserTestCases(unittest.TestCase):
    event_json = '2017-04-10T17:45:24.621Z idp {"id":"ff2d1183-3a82-42d6-8b08-19845ea8da3d","name":"Sign in page visited","properties":{"event_properties":{},"user_id":"anonymous-uuid","user_ip":"24.124.56.64","user_agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36","host":"idp.staging.login.gov"},"visit_id":"e6808a77-4c6f-4feb-bca6-fc88e5f67292","visitor_id":"76e2e090-0f78-4b77-b5a6-bd5c6c2e484e","time":"2017-04-10T17:45:22.754Z"}'
    test_event_log_txt = BytesIO(b"""
    2017-04-10T17:45:24.621Z idp 172.16.33.245 - - [10/Apr/2017:17:45:21 +0000] "GET / HTTP/1.1" 401 188 "-" "ELB-HealthChecker/2.0"
    2017-04-10T17:45:24.621Z idp 172.16.33.245 - - [10/Apr/2017:17:45:23 +0000] "GET /manifest.json HTTP/1.1" 304 0 "https://idp.staging.login.gov/?issuer=" "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36"
    2017-04-10T17:45:28.382Z idp Apr 10 17:45:22 idp ossec: Alert Level: 5; Rule: 31101 - Web server 400 error code.; Location: idp->/opt/nginx/logs/access.log; srcip: 172.16.33.245; 172.16.33.245 - - [10/Apr/2017:17:45:21 +0000] "GET / HTTP/1.1" 401 188 "-" "ELB-HealthChecker/2.0"
    2017-04-10T17:45:29.473Z idp {"id":"ff2d1183-3a82-42d6-8b08-19845ea8da3d","name":"Sign in page visited","properties":{"event_properties":{},"user_id":"anonymous-uuid","user_ip":"24.124.56.64","user_agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36","host":"idp.staging.login.gov"},"visit_id":"e6808a77-4c6f-4feb-bca6-fc88e5f67292","visitor_id":"76e2e090-0f78-4b77-b5a6-bd5c6c2e484e","time":"2017-04-10T17:45:22.754Z"}
    2017-04-10T17:45:29.022Z idp Apr 10 17:45:21 idp ossec: Alert Level: 5; Rule: 31101 - Web server 400 error code.; Location: idp->/opt/nginx/logs/access.log; srcip: 172.16.33.245; 172.16.33.245 - - [10/Apr/2017:17:45:21 +0000] "GET / HTTP/1.1" 401 188 "-" "ELB-HealthChecker/2.0"
    2017-04-10T17:45:43.383Z idp Apr 10 17:45:40 idp ossec: Alert Level: 5; Rule: 31101 - Web server 400 error code.; Location: idp->/opt/nginx/logs/access.log; srcip: 172.16.33.233; 172.16.33.233 - - [10/Apr/2017:17:45:39 +0000] "GET / HTTP/1.1" 401 188 "-" "ELB-HealthChecker/2.0"
    2017-04-10T17:45:44.023Z idp Apr 10 17:45:41 idp ossec: Alert Level: 5; Rule: 31101 - Web server 400 error code.; Location: idp->/opt/nginx/logs/access.log; srcip: 172.16.33.233; 172.16.33.233 - - [10/Apr/2017:17:45:39 +0000] "GET / HTTP/1.1" 401 188 "-" "ELB-HealthChecker/2.0"
    """)
    in_io = test_event_log_txt.read()

    def test_stream_csv(self):
        parser = EventParser()
        parsed_rows, total_rows, out, out_parquet = parser.stream_csv(self.in_io)
        self.assertEqual(parsed_rows, 1)
        self.assertTrue(len(out_parquet.read()) > 0)

    def test_extract_json(self):
        parser = EventParser()
        data = parser.extract_json(self.event_json, line_num=1)
        self.assertEqual(data['id'], 'ff2d1183-3a82-42d6-8b08-19845ea8da3d')
        self.assertEqual(data['properties']['user_ip'], '24.124.56.64')

    def test_json_to_csv(self):
        parser = EventParser()
        data = parser.extract_json(self.event_json, line_num=1)
        res = parser.json_to_csv(data)[0]
        self.assertEqual(len(res), 20)
        self.assertEqual(res[8], '2017-04-10 17:45:22')
        self.assertFalse(res[-1])

if __name__ == '__main__':
    unittest.main()
