import json, datetime, zipfile, csv, io, os
import requests
import urllib.request


def lambda_handler(event, context):
    
    # 사용자가 https://clcbp2jct1.execute-api.ap-northeast-2.amazonaws.com/aws/usage/{year}/{month} 에 year, month 정보를 입력하면 해당 년 월을 기준으로 데이터 출력
    year = event['pathParameters']['year']
    month = event['pathParameters']['month']
    
    # 예외 처리 조건 2
    # 입력해야 할 year, month 값이 없는 경우 
    if not year or not month:
        
        response = {
            "statusCode": 404,
            "body": json.dumps({"message": "입력해야 할 year, month 값이 없습니다."})
        }

        return response
    
    # 데이터가 저장된 zip파일 저장
    url = 'http://dtgqz5l2d6wuw.cloudfront.net/coding_test_1.csv.zip'
    try:
        with urllib.request.urlopen(url) as data:
            # 예외 처리 조건 3
            # 데이터 URL의 압축 파일이 10MB를 넘는 경우
            if data.getheader('Content-Length') and int(data.getheader('Content-Length')) > 10*1024*1024:
                
                response = {
                    "statusCode": 400,
                    "body": json.dumps({"message": '데이터 URL의 압축 파일이 10MB를 넘습니다.'})
                }

                return response

            # zip파일을 csv로 변환
            with zipfile.ZipFile(io.BytesIO(data.read())) as zip_file:
                csv_filename = zip_file.namelist()[0]
                with zip_file.open(csv_filename) as csv_file:
                    csv_reader = csv.reader(io.TextIOWrapper(csv_file, encoding='utf-8'))
                    rows = []
                    for row in csv_reader:
                        rows.append(row)

    # 예외 처리 조건 1
    # 데이터 URL에 파일이 없는 경우
    except urllib.error.HTTPError as e:
        if e.code == 404:
          
          response = {
                    "statusCode": 404,
                    "body": json.dumps({"message": '데이터 URL에 파일이 없습니다.'})
                }
            
        else:
            raise e
    
    # 주어진 데이터 엑셀의 TimeInterval 값에서 해당 year-month로 시작하는 데이터 필터링
    filtered_rows = []
    for row in rows:
        if row[2].startswith(f'{year}-{month}'):
            filtered_rows.append(row)
            
    # csv파일 생성
    csv_buffer = io.StringIO()
    writer = csv.writer(csv_buffer)
    writer.writerow(['LineItemId','userId','TimeInterval','UsageStartDate',	'UsageEndDate', 'LineItemType',	'ProductCode', 'productFamily', 'ProductName', 'Cost', 'exchangeRate'])
    writer.writerows(filtered_rows)
    csv_content = csv_buffer.getvalue()

    # 필터링 한 값 return
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'text/csv',
            'Content-Disposition': f'attachment; filename=usage.csv'
        },
        'body': csv_content
    }

