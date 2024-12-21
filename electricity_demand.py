import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rc

# 한글 폰트 설정
rc('font', family='Malgun Gothic')

# 데이터 파일 경로 지정
file_path = '한국전력거래소_시간별 전국 전력수요량_20231231.csv'

# 데이터 불러오기
data = pd.read_csv(file_path, encoding='cp949')

# 데이터 전처리
data_melted = data.melt(id_vars=['날짜'], var_name='Hour', value_name='Demand')
data_melted['날짜'] = pd.to_datetime(data_melted['날짜'])
data_melted['Hour'] = data_melted['Hour'].str.replace('시', '').astype(int)
data_melted['Month'] = data_melted['날짜'].dt.month
data_melted['DayOfWeek'] = data_melted['날짜'].dt.dayofweek  # 0=월요일, 6=일요일

# 월을 계절 치환 (봄: 3-5, 여름: 6-8, 가을: 9-11, 겨울: 12-2)
def map_season(month):
    if month in [3, 4, 5]:
        return 'Spring'
    elif month in [6, 7, 8]:
        return 'Summer'
    elif month in [9, 10, 11]:
        return 'Fall'
    else:
        return 'Winter'

data_melted['Season'] = data_melted['Month'].apply(map_season)

# 계절별로 월별 수요량 차이가 큰 월 구하기
monthly_stats = data_melted.groupby(['Month', 'Season'])['Demand'].agg(['max', 'min']).reset_index()
monthly_stats['Difference'] = monthly_stats['max'] - monthly_stats['min']
seasonal_top_months = monthly_stats.loc[monthly_stats.groupby('Season')['Difference'].idxmax()]

# 계절별 색상 설정
color_map = {
    'Spring': ['#a8e6a3', '#57d057', '#247b24'],  # 연두, 초록, 진한 초록
    'Summer': ['#ff9999', '#ff4d4d', '#b30000'],  # 밝은 빨강, 중간 빨강, 진한 빨강
    'Fall': ['#b399ff', '#8000ff', '#4d0099'],    # 연한 보라, 중간 보라, 진한 보라
    'Winter': ['#b3d9ff', '#66b3ff', '#0066cc']   # 연한 파랑, 중간 파랑, 진한 파랑
}

#공휴일 추가
holidays = [
    '2023-01-01','2023-01-21','2023-01-22','2023-01-23','2023-01-24',
    '2023-03-01','2023-05-01','2023-05-05','2023-05-27','2023-05-29',
    '2023-06-06','2023-08-15','2023-09-28','2023-09-29','2023-09-30',
    '2023-10-03','2023-10-09','2023-12-25'
]
holidays = pd.to_datetime(holidays)

# 월별 그래프 그리기
plt.figure(figsize=(14, 8))
for month in range(1, 13):
    month_data = data_melted[data_melted['Month'] == month]
    hourly_avg = month_data.groupby('Hour')['Demand'].mean().reset_index()
    season = month_data['Season'].iloc[0]
    color_index = (month - 1) % 3
    plt.plot(hourly_avg['Hour'], hourly_avg['Demand'], label=f'{month}월', color=color_map[season][color_index])

plt.title('월별 시간대 평균 전력 수요량', fontsize=16)
plt.xlabel('시간 (시)', fontsize=14)
plt.ylabel('평균 전력 수요량 (MW)', fontsize=14)
plt.legend(title='월', fontsize=10)
plt.grid(True, linestyle='--', alpha=0.7)
plt.xticks(range(1, 25))  # X축을 1시부터 24시까지만 표시
plt.tight_layout()
plt.show()

# 계절 순서대로 정렬 (봄, 여름, 가을, 겨울)
seasonal_top_months = seasonal_top_months.set_index('Season').loc[['Spring', 'Summer', 'Fall', 'Winter']].reset_index()

# 계절별로 가장 차이가 큰 월의 일별 그래프 그리기
for _, row in seasonal_top_months.iterrows():
    month = row['Month']
    season = row['Season']
    month_data = data_melted[data_melted['Month'] == month]

    # 일별 그래프
    daily_demand = month_data.groupby('날짜')['Demand'].sum().reset_index()
    plt.figure(figsize=(14, 8))
    for _, day_row in daily_demand.iterrows():
        date = day_row['날짜']
        demand = day_row['Demand']
        if date in holidays or date.dayofweek in [5, 6]:  # 공휴일 또는 주말
            plt.bar(date, demand, color='red', label='공휴일/주말' if '공휴일/주말' not in plt.gca().get_legend_handles_labels()[1] else "")
        else:
            plt.bar(date, demand, color='blue', label='평일' if '평일' not in plt.gca().get_legend_handles_labels()[1] else "")

    plt.title(f'{season} ({month}월) 일별 전력 수요량', fontsize=16)
    plt.xlabel('날짜', fontsize=14)
    plt.ylabel('일별 전력 수요량 (MW)', fontsize=14)
    plt.legend(title='구분', fontsize=10)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.show()

