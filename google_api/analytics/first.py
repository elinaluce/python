"""Hello Analytics Reporting API V4."""

import argparse
import pprint

from apiclient.discovery import build
import httplib2

from oauth2client import client
from oauth2client import file
from oauth2client import tools
from oauth2client.service_account import ServiceAccountCredentials

SCOPES = ['https://www.googleapis.com/auth/analytics.readonly']
DISCOVERY_URI = ('https://analyticsreporting.googleapis.com/$discovery/rest')
KEY_FILE_LOCATION = 'key.p12'
SERVICE_ACCOUNT_EMAIL = 'google-api@dulcet-port-132823.iam.gserviceaccount.com'
VIEW_ID = '10541945'

def initialize_analytics_reporting():
    """Initializes an analytics_reporting service object.

    Returns:
        analytics an authorized analytics reporting service object.
    """

    credentials = ServiceAccountCredentials.from_p12_keyfile(
        SERVICE_ACCOUNT_EMAIL, KEY_FILE_LOCATION, scopes=SCOPES)

    http = credentials.authorize(httplib2.Http())

    # Build the service object.
    analytics = build('analytics', 'v4', http=http,
        discoveryServiceUrl=DISCOVERY_URI)

    return analytics

def get_data(analytics):
    data = {}
    date_ranges = [{'startDate': '119daysAgo', 'endDate': '90daysAgo'},
                   {'startDate': '89daysAgo', 'endDate': '60daysAgo'},
                   {'startDate': '59daysAgo', 'endDate': '30daysAgo'},
                   {'startDate': '29daysAgo', 'endDate': 'today'}]
    metrics = ['sessions',]
    dimensions = ['region', 'country']
    dimension_filter = 'United States'
    for date_range in date_ranges:
        report = get_report(analytics, date_range, metrics, dimensions,
            dimension_filter)
        parse_report(report, data)
    return data


def get_report(analytics, date_range, metrics, dimensions, dimension_filter):
    report_metrics = [{'expression': 'ga:' + m} for m in metrics]
    report_dimensions = [{'name': 'ga:' + d} for d in dimensions]

    return analytics.reports().batchGet(
      body={
        'reportRequests': [
        {
          'viewId': VIEW_ID,
          'dateRanges': [date_range],
          'dimensions': report_dimensions,
          'dimensionFilterClauses': [
            {
              'filters': [
                {
                    'dimensionName': 'ga:' + dimensions[-1],
                    'operator': 'EXACT',
                    'expressions': [dimension_filter]
                }
              ]
            }
          ],
          'metrics': report_metrics
        }
        ]
      }
    ).execute()


def parse_report(report, data):
    for r in report.get('reports', []):
        column_header = r.get('columnHeader', {})
        dimension_headers = column_header.get('dimensions', [])
        metric_headers = column_header.get(
            'metricHeader', {}).get('metricHeaderEntries', [])
        rows = r.get('data', {}).get('rows', [])

        for row in rows:
            dimensions = row.get('dimensions', [])
            date_range_values = row.get('metrics', [])

            region = ''
            for header, dimension in zip(dimension_headers, dimensions):
                if header == 'ga:region':
                    region = dimension
                    if dimension not in data:
                        data[dimension] = []

            for i, values in enumerate(date_range_values):
                for metric_header, value in zip(metric_headers,
                        values.get('values')):
                    if metric_header.get('name') == 'ga:sessions':
                        data[region].append(int(value))


def main():

    analytics = initialize_analytics_reporting()
    data = get_data(analytics)
    for k, v in data.items():
        index = v.index(max(v))
        data[k] = [v, index]
    pprint.pprint(data)


if __name__ == '__main__':
    main()
