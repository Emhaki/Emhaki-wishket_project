from collections import defaultdict
import csv, io, datetime, requests
import os
from django.http import HttpResponse, HttpResponseBadRequest
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from zipfile import ZipFile
import json 

class AWSViewSet(viewsets.ViewSet):

    @action(detail=False, methods=['get'])
    def usage(self, request):
        year = request.query_params.get('year')
        month = request.query_params.get('month')

        if not year or not month:
            return Response(data={'error': 'Year and month parameters are required.'}, status=status.HTTP_400_BAD_REQUEST)

        url = 'http://dtgqz5l2d6wuw.cloudfront.net/coding_test_1.csv.zip'  # 데이터 압축 파일일
        response = requests.get(url)

        if not response.ok:
            return Response(data={'error': 'Failed to retrieve data.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        with ZipFile(io.BytesIO(response.content)) as zip_file:
            csv_filename = f'{year}-{month}.csv'

            try:
                with zip_file.open(csv_filename) as csv_file:
                    reader = csv.DictReader(io.TextIOWrapper(csv_file))
                    filtered_data = [row for row in reader if row['TimeInterval'].startswith(f'{year}-{month}')]
            except KeyError:
                return Response(data={'error': 'Data not found.'}, status=status.HTTP_404_NOT_FOUND)

        if not filtered_data:
            return Response(data={'error': 'Data not found.'}, status=status.HTTP_404_NOT_FOUND)

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(filtered_data[0].keys())
        for row in filtered_data:
            writer.writerow(row.values())

        output.seek(0)

        response = HttpResponse(output, content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{csv_filename}"'

        return response
    
    # 위 코드는 AWSBillViewSet라는 ViewSet 클래스를 정의하고, usage라는 액션 메서드를 추가합니다. usage 메서드는 HTTP GET 요청을 받아 year와 month 파라미터를 추출한 뒤, 지정된 URL에서 AWS 사용 내역을 압축 파일 형식으로 가져옵니다. 가져온 압축 파일에서 요청받은 월에 해당하는 CSV 파일을 찾아서 해당 내역을 필터링하고, 필터링된 결과를 CSV 파일로 변환하여 HTTP 응답으로 반환합니다.

    # 예외 처리를 위해 다음과 같은 상황에서 HTTP 응답을 반환합니다.

    # 요청 시 입력해야할 year, month 값이 없는 경우: HTTP 400 Bad Request
    # 데이터 URL에 파일이 없는 경우: HTTP 404 Not Found
    # 데이터 URL의 압축 파일이 10MB를 넘는 경우: HTTP 500 Internal Server Error

    @action(detail=False, methods=['get'])
    def bill(self, request):
        # 요청 폼 데이터에서 필요한 값 추출
        user_id = request.data.get('id')
        year = request.data.get('year')
        month = request.data.get('month')

        # 압축 파일의 URL
        url = 'http://dtgqz5l2d6wuw.cloudfront.net/coding_test_1.csv.zip'

        # 압축 파일 다운로드
        response = requests.get(url)
        with ZipFile(io.BytesIO(response.content)) as zip_ref:
            zip_ref.extractall()

        # csv 파일 읽기
        with open('coding_test_1.csv') as f:
            reader = csv.DictReader(f)
            # 필터링된 데이터 저장할 딕셔너리
            filtered_data = {}
            for row in reader:
                # 필터링 조건
                if row['userId'] == user_id and row['TimeInterval'].startswith(year):
                    # 월별 key 생성
                    if not month:
                        key = row['TimeInterval'][:7]
                    elif month == row['TimeInterval'][5:7]:
                        key = row['TimeInterval'][:7]
                    else:
                        continue
                    # 필터링된 데이터 저장
                    if key not in filtered_data:
                        filtered_data[key] = {
                            'exchange_rate': [],
                            'cost': []
                        }
                    filtered_data[key]['exchange_rate'].append(float(row['exchangeRate']))
                    filtered_data[key]['cost'].append(float(row['cost']))

        # 필터링된 데이터가 없으면 오류 반환
        if not filtered_data:
            return Response({'error': 'No data matches the given conditions.'}, status=status.HTTP_400_BAD_REQUEST)

        # 각 월별로 요구되는 값을 계산하여 결과값을 저장할 딕셔너리
        result = {}
        for key, value in filtered_data.items():
            # 월별 환율
            exchange_rate = round(sum(value['exchange_rate']) / len(value['exchange_rate']), 8)
            # 월별 요금
            cost = sum(value['cost'])
            # 월별 원화 요금
            cost_krw = int(exchange_rate * cost)
            result[key] = {
                'exchange_rate': exchange_rate,
                'cost': cost,
                'cost_krw': cost_krw
            }

        # 결과값 반환
        return Response(result)
    
# 사용자로부터 id, year, month 데이터를 요청으로 받습니다.
# 받은 데이터를 바탕으로 데이터를 필터링하고 각 월별로 요구되는 값을 계산하여 결과값을 저장합니다.
# 필터링된 데이터가 없으면 오류를 반환합니다.
# 결과값을 json 형태로 반환합니다.
  
{
    "version": "1.0", "resource": "/View-usage-history-API", "path": "/default/View-usage-history-API", "httpMethod": "GET", 
    "headers": {"Content-Length": "0", "Host": "5e3zklx4vg.execute-api.ap-northeast-2.amazonaws.com", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36", "X-Amzn-Trace-Id": "Root=1-641108e3-15ee874906fba5e62acff0c9", "X-Forwarded-For": "183.96.82.158", "X-Forwarded-Port": "443", "X-Forwarded-Proto": "https", "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7", "accept-encoding": "gzip, deflate, br", "accept-language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7", "cache-control": "max-age=0", "sec-ch-ua": "\"Google Chrome\";v=\"111\", \"Not(A:Brand\";v=\"8\", \"Chromium\";v=\"111\"", "sec-ch-ua-mobile": "?0", "sec-ch-ua-platform": "\"Windows\"", "sec-fetch-dest": "document", "sec-fetch-mode": "navigate", "sec-fetch-site": "none", "sec-fetch-user": "?1", "upgrade-insecure-requests": "1"}, "multiValueHeaders": {"Content-Length": ["0"], "Host": ["5e3zklx4vg.execute-api.ap-northeast-2.amazonaws.com"], "User-Agent": ["Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"], "X-Amzn-Trace-Id": ["Root=1-641108e3-15ee874906fba5e62acff0c9"], "X-Forwarded-For": ["183.96.82.158"], "X-Forwarded-Port": ["443"], "X-Forwarded-Proto": ["https"], "accept": ["text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7"], "accept-encoding": ["gzip, deflate, br"], "accept-language": ["ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7"], "cache-control": ["max-age=0"], "sec-ch-ua": ["\"Google Chrome\";v=\"111\", \"Not(A:Brand\";v=\"8\", \"Chromium\";v=\"111\""], "sec-ch-ua-mobile": ["?0"], "sec-ch-ua-platform": ["\"Windows\""], "sec-fetch-dest": ["document"], "sec-fetch-mode": ["navigate"], "sec-fetch-site": ["none"], "sec-fetch-user": ["?1"], "upgrade-insecure-requests": ["1"]}, "queryStringParameters": null, "multiValueQueryStringParameters": null, "requestContext": {"accountId": "934881210813", "apiId": "5e3zklx4vg", "domainName": "5e3zklx4vg.execute-api.ap-northeast-2.amazonaws.com", "domainPrefix": "5e3zklx4vg", "extendedRequestId": "By5TojpJoE0EMiA=", "httpMethod": "GET", "identity": {"accessKey": null, "accountId": null, "caller": null, "cognitoAmr": null, "cognitoAuthenticationProvider": null, "cognitoAuthenticationType": null, "cognitoIdentityId": null, "cognitoIdentityPoolId": null, "principalOrgId": null, "sourceIp": "183.96.82.158", "user": null, "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36", "userArn": null}, "path": "/default/View-usage-history-API", "protocol": "HTTP/1.1", "requestId": "By5TojpJoE0EMiA=", "requestTime": "14/Mar/2023:23:53:07 +0000", "requestTimeEpoch": 1678837987788, "resourceId": "ANY /View-usage-history-API", "resourcePath": "/View-usage-history-API", "stage": "default"},
    "pathParameters": null, "stageVariables": null, "body": null, "isBase64Encoded": false}