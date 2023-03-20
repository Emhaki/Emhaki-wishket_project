from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
import zipfile, csv, io
import urllib.request
import requests
from decimal import Decimal

class AWSViewSet(viewsets.ViewSet):
    
    @action(detail=False, methods=['get'])
    def usage(self, request, year, month):

        # 예외 처리 조건 2
        # 입력해야 할 year, month 값이 없는 경우 
        if not year or not month:

            return Response({'error': "입력해야 할 year, month 값이 없습니다."}, status=status.HTTP_404_NOT_FOUND)
        
        # 데이터가 저장된 zip파일 저장
        url = 'http://dtgqz5l2d6wuw.cloudfront.net/coding_test_1.csv.zip'

        # 예외 처리 조건 1
        # 데이터 URL에 파일이 없는 경우
        if not urllib.request.urlopen(url):
            return Response({'error': '데이터 URL에 파일이 없습니다.'}, status=status.HTTP_404_NOT_FOUND)

        with urllib.request.urlopen(url) as data:
            # 예외 처리 조건 3
            # 데이터 URL의 압축 파일이 10MB를 넘는 경우
            if data.getheader('Content-Length') and int(data.getheader('Content-Length')) > 10*1024*1024:

                return Response({'error': '데이터 URL의 압축 파일이 10MB를 넘습니다.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # zip파일을 csv로 변환
            with zipfile.ZipFile(io.BytesIO(data.read())) as zip_file:
                csv_filename = zip_file.namelist()[0]
                with zip_file.open(csv_filename) as csv_file:
                    csv_reader = csv.reader(io.TextIOWrapper(csv_file, encoding='utf-8'))
                    rows = []
                    for row in csv_reader:
                        rows.append(row)
        
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

        result = {
                'ContentType': 'text/csv',
                'Filename': f'attachment; filename=usage.csv',
                'body': csv_content
        }
        return Response(result, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'])
    def bill(self, request):
        # POST 요청에서 form-data 파라미터 가져오기
        user_id = request.data.get('user_id')
        year = request.data.get('year')
        month = request.data.get('month')

        # 데이터 압축 파일 URL
        data_url = "http://dtgqz5l2d6wuw.cloudfront.net/coding_test_1.csv.zip"
        # 압축 파일 다운로드
        r = requests.get(data_url)
        # 압축 파일을 메모리에서 읽어들이기
        z = zipfile.ZipFile(io.BytesIO(r.content))
        # csv 파일 읽기
        with z.open('coding_test_1.csv') as f:
            reader = csv.DictReader(io.TextIOWrapper(f))
            # 필터링된 row들을 저장할 리스트
            filtered_rows = []
            for row in reader:
                # TimeInterval에서 year, month 추출 => str타입
                year_interval = row['TimeInterval'].split('-')[0]
                month_interval = row['TimeInterval'].split('-')[1]

                # 오류 처리 조건
                # 데이터 URL의 파일에 환율 정보가 없는 경우
                if not row['exchangeRate']:
                    return Response({'error': "데이터 URL 파일에 환율 정보가 없습니다."}, status=status.HTTP_400_BAD_REQUEST)

                # 필터링 조건 확인
                # month 값이 있다면 해당 월 데이터 필터링
                if int(month_interval) == month and int(row['userId']) == user_id and int(year_interval) == year:
                    filtered_rows.append(row)
                # month 값이 없다면 해당 년 데이터 필터링
                elif not month and int(row['userId']) == user_id and int(year_interval) == year:
                    filtered_rows.append(row)

            # 월별로 분리하여 계산하기
            result = {}
            month_costs = {}
            month_exchange_rates = {}

            for row_data in filtered_rows:
                mth = row_data['TimeInterval'].split('-')[1]
                # exchange_rate 계산
                exchange_rate = Decimal((row_data['exchangeRate']))
                if mth not in month_exchange_rates:
                    month_exchange_rates[mth] = []
                month_exchange_rates[mth].append(exchange_rate)

                # cost 계산
                cost = Decimal((row_data['Cost']))
                if mth not in month_costs:
                    month_costs[mth] = Decimal(0)
                month_costs[mth] += cost
                
                # 각 월별로 환율, 요금, 원화요금 계산         
                # 월별 환율 계산 (소수점 8자리까지 계산)
                exchange_rate_avg = sum(month_exchange_rates[mth]) / len(month_exchange_rates[mth])
                exchange_rate_avg = round(exchange_rate_avg, 8)

                # 월별 요금 계산
                mth_cost = month_costs[mth]

                # 월별 원화 요금 계산 (소수점 2의 자리에서 버림)
                cost_krw = round((mth_cost * exchange_rate_avg), 2)
                
                # 결과값 저장
                if mth not in result:
                    result[mth] = []
                    
                result[mth] = {
                    "exchange_rate": exchange_rate_avg,
                    "cost": mth_cost,
                    "cost_krw": cost_krw
                }
              
            # 결과값 반환
            return Response(result)

# {
#  "user_id": 12344321,
#  "year": 2022,
#  "month": 11
# }