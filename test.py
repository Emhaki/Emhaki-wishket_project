import json, datetime, zipfile, csv, io, os
import requests
import urllib.request


def lambda_handler(event, context):
    
    year = event['pathParameters']['year']
    month = event['pathParameters']['month']

    # return {
    #     'statusCode': 200,
    #     'body': json.dumps(year)
    # }
    if not year or not month:
        return {
            'statusCode': 400,
            'body': 'year and month parameters are required'
        }

    # download and extract the csv file
    url = 'http://dtgqz5l2d6wuw.cloudfront.net/coding_test_1.csv.zip'
    try:
        with urllib.request.urlopen(url) as response:
            if response.getheader('Content-Length') and int(response.getheader('Content-Length')) > 10*1024*1024:
                return {
                    'statusCode': 400,
                    'body': 'csv file is too large'
                }
            with zipfile.ZipFile(io.BytesIO(response.read())) as zip_file:
                csv_filename = zip_file.namelist()[0]
                with zip_file.open(csv_filename) as csv_file:
                    csv_reader = csv.reader(io.TextIOWrapper(csv_file, encoding='utf-8'))
                    rows = []
                    for row in csv_reader:
                        rows.append(row)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return {
                'statusCode': 404,
                'body': 'csv file not found'
            }
        else:
            raise e

    # filter the rows by year and month
    filtered_rows = []
    for row in rows:
        if row[2].startswith(f'{year}-{month}'):
            filtered_rows.append(row)
            
    # create the response csv file
    csv_buffer = io.StringIO()
    writer = csv.writer(csv_buffer)
    writer.writerow(['LineItemId','userId','TimeInterval','UsageStartDate',	'UsageEndDate', 'LineItemType',	'ProductCode', 'productFamily', 'ProductName', 'Cost', 'exchangeRate'])
    writer.writerows(filtered_rows)
    csv_content = csv_buffer.getvalue()

    # return the response
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'text/csv',
            'Content-Disposition': f'attachment; filename=usage.csv'
        },
        'body': csv_content
    }
