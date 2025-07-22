import streamlit as st
import requests
import datetime

API_KEY = "c4ef97602ca54adc9e4cd49648b247f6"
REGION_CODES = {
    '서울특별시': 'B10', '부산광역시': 'C10', '대구광역시': 'D10', '인천광역시': 'E10',
    '광주광역시': 'F10', '대전광역시': 'G10', '울산광역시': 'H10', '세종특별자치시': 'I10',
    '경기도': 'J10', '강원도': 'K10', '충청북도': 'M10', '충청남도': 'N10', '전라북도': 'P10',
    '전라남도': 'Q10', '경상북도': 'R10', '경상남도': 'S10', '제주특별자치도': 'T10'
}

st.title("학교 시간표 조회 웹 서비스")

# 1. 학교 검색
region = st.selectbox("지역 선택", list(REGION_CODES.keys()))
school_name = st.text_input("학교명 입력")
if st.button("학교 검색"):
    params = {
        'KEY': API_KEY, 'Type': 'json', 'pIndex': 1, 'pSize': 100,
        'ATPT_OFCDC_SC_CODE': REGION_CODES[region], 'SCHUL_NM': school_name
    }
    res = requests.get("http://open.neis.go.kr/hub/schoolInfo", params=params)
    data = res.json()
    schools = []
    if 'schoolInfo' in data and len(data['schoolInfo']) > 1:
        schools = data['schoolInfo'][1]['row']
    if schools:
        st.session_state['schools'] = schools
        st.success(f"{len(schools)}개 학교 검색됨")
    else:
        st.warning("검색 결과가 없습니다.")

# 2. 학교 선택
schools = st.session_state.get('schools', [])
school_options = [f"{s['SCHUL_NM']} ({s['LCTN_SC_NM']})" for s in schools]
school_idx = st.selectbox("학교 선택", range(len(school_options)), format_func=lambda i: school_options[i] if schools else "")
selected_school = schools[school_idx] if schools else None
school_kind = selected_school['SCHUL_KND_SC_NM'] if selected_school else ""

# 3. 학년/반 선택
if "초등학교" in school_kind:
    grade_options = [str(i) for i in range(1, 7)]
else:
    grade_options = ["1", "2", "3"]
grade = st.selectbox("학년", grade_options)
class_num = st.selectbox("반", [str(i) for i in range(1, 21)])

# 4. 주차 선택 (3월~내년 2월/3월까지)
today = datetime.date.today()
current_year = today.year
start_date = datetime.date(current_year, 3, 1)
if today.month < 3:
    start_date = datetime.date(current_year - 1, 3, 1)
end_date = datetime.date(start_date.year + 1, 3, 1)

def get_week_options(start_date, end_date):
    week_options = []
    current = start_date - datetime.timedelta(days=start_date.weekday())
    while current < end_date:
        week_end = current + datetime.timedelta(days=4)
        week_str = f"{current.strftime('%Y-%m-%d')} ~ {week_end.strftime('%m-%d')}"
        week_options.append((week_str, current))
        current += datetime.timedelta(weeks=1)
    return week_options

week_options = get_week_options(start_date, end_date)
week_labels = [w[0] for w in week_options]
def_week_idx = 0
for i, (_, monday) in enumerate(week_options):
    if monday <= today <= monday + datetime.timedelta(days=4):
        def_week_idx = i
        break
selected_week_idx = st.selectbox("주차 선택", range(len(week_labels)), format_func=lambda i: week_labels[i], index=def_week_idx)
monday = week_options[selected_week_idx][1]
week_str = week_labels[selected_week_idx]
st.write(f"선택된 주: {week_str}")

# 5. 시간표 조회
if st.button("주간 시간표 조회") and selected_school:
    timetable = {}
    # 학교 종류에 따라 엔드포인트 결정
    if "초등학교" in school_kind:
        timetable_api = "elsTimetable"
    elif "중학교" in school_kind:
        timetable_api = "misTimetable"
    elif "고등학교" in school_kind:
        timetable_api = "hisTimetable"
    else:
        st.warning(f"지원하지 않는 학교 종류입니다: {school_kind}")
        timetable_api = None

    if timetable_api:
        for i in range(5):  # 월~금
            date = monday + datetime.timedelta(days=i)
            params = {
                'KEY': API_KEY, 'Type': 'json', 'pIndex': 1, 'pSize': 100,
                'ATPT_OFCDC_SC_CODE': selected_school['ATPT_OFCDC_SC_CODE'],
                'SD_SCHUL_CODE': selected_school['SD_SCHUL_CODE'],
                'GRADE': grade, 'CLASS_NM': class_num, 'SEM': '1',
                'ALL_TI_YMD': date.strftime("%Y%m%d")
            }
            url = f"http://open.neis.go.kr/hub/{timetable_api}"
            res = requests.get(url, params=params)
            data = res.json()
            day_data = [""] * 8
            if timetable_api in data and len(data[timetable_api]) > 1:
                for item in data[timetable_api][1]['row']:
                    period = int(item['PERIO']) - 1
                    subject = item['ITRT_CNTNT']
                    if 0 <= period < 8:
                        day_data[period] = subject
            timetable[i] = day_data
        st.session_state['timetable'] = timetable
        st.success("시간표 조회 완료!")

# 6. 시간표 표시 (HTML 표 + 과목 강조)
timetable = st.session_state.get('timetable', {})
subject = st.text_input("강조할 과목명 입력", key="highlight_subject")
highlight = subject.strip()

if timetable:
    st.write("### 주간 시간표")
    days = ["월", "화", "수", "목", "금"]
    periods = ["1교시", "2교시", "3교시", "4교시", "5교시", "6교시", "7교시", "8교시"]

    # HTML 표 생성
    html = "<table border='1' style='border-collapse:collapse; text-align:center;'>"
    html += "<tr><th></th>" + "".join(f"<th>{d}</th>" for d in days) + "</tr>"
    for p in range(8):
        html += f"<tr><td><b>{periods[p]}</b></td>"
        for d in range(5):
            cell = timetable[d][p] if d in timetable else ""
            if highlight and highlight == cell:
                html += f"<td style='background-color: #fff59d; color: #000; font-weight:bold'>{cell}</td>"
            else:
                html += f"<td>{cell}</td>"
        html += "</tr>"
    html += "</table>"
    st.markdown(html, unsafe_allow_html=True) 