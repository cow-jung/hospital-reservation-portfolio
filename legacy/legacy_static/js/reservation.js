// =====================================================================
// 유민정 담당 - 예약하기 페이지 JavaScript
// =====================================================================
//
// 주요 기능
// 1. 진료과를 선택하면 해당 진료과 의료진만 표시
// 2. 예약 날짜를 달력 형태로 표시
// 3. 오늘 이전 날짜는 선택 불가
// 4. 날짜 선택 시 선택한 날짜 표시
// 5. 선택한 의료진 + 날짜 기준으로 예약된 시간 조회
// 6. 예약 가능한 시간을 버튼으로 표시
// 7. 의료진 변경 시 기존 날짜/시간 선택 초기화
//
// =====================================================================


// =====================================================================
// 1. HTML 요소 가져오기
// =====================================================================


// ---------------------------------------------------------
// 진료과 / 의료진
// ---------------------------------------------------------

// 진료과 선택창
const departmentSelect =
    document.getElementById("dept_id");

// 의료진 선택창
const doctorSelect =
    document.getElementById("doctor_id");


// ---------------------------------------------------------
// 달력
// ---------------------------------------------------------

// 달력 상단의 "2026년 8월" 같은 제목
const calendarTitle =
    document.getElementById("calendar_title");

// 날짜가 실제로 들어가는 tbody
const calendarBody =
    document.getElementById("calendar_body");

// 이전 달 버튼
const prevMonthButton =
    document.getElementById("prev_month");

// 다음 달 버튼
const nextMonthButton =
    document.getElementById("next_month");


// ---------------------------------------------------------
// 선택한 날짜
// ---------------------------------------------------------

// Flask로 실제 전달되는 예약 날짜
// 화면에는 보이지 않는 hidden input
const reservationDateInput =
    document.getElementById("reservation_date");

// 화면에 "선택한 날짜 : ..."를 보여주는 영역
const selectedDateDisplay =
    document.getElementById("selected_date_display");


// ---------------------------------------------------------
// 예약 시간
// ---------------------------------------------------------

// 날짜를 선택한 뒤 나타나는 전체 시간 선택 영역
const reservationTimeArea =
    document.getElementById("reservation_time_area");

// 시간 버튼들이 들어가는 영역
const timeButtons =
    document.getElementById("time_buttons");

// Flask로 실제 전달되는 예약 시간
// 화면에는 보이지 않는 hidden input
const reservationTimeInput =
    document.getElementById("reservation_time");

// 화면에 "선택한 시간 : ..."을 보여주는 영역
const selectedTimeText =
    document.getElementById("selected_time_text");



// =====================================================================
// 2. 현재 날짜 및 현재 보고 있는 달 설정
// =====================================================================


// 오늘 날짜
const today = new Date();

// 시간 부분을 0으로 만들어 날짜 비교만 정확하게 수행
today.setHours(0, 0, 0, 0);


// 처음에는 현재 연도와 현재 월을 보여줌
let currentYear = today.getFullYear();

// getMonth()는 0부터 시작
// 1월 = 0, 2월 = 1 ... 12월 = 11
let currentMonth = today.getMonth();



// =====================================================================
// 3. 진료과 선택 → 해당 의료진만 표시
// =====================================================================


if (departmentSelect && doctorSelect) {

    departmentSelect.addEventListener(
        "change",
        function () {

            // 현재 선택한 진료과 번호
            const selectedDepartmentId =
                departmentSelect.value;


            // 의료진 select 안의 모든 option
            const doctorOptions =
                doctorSelect.querySelectorAll("option");


            // 진료과가 바뀌면 기존 의료진 선택 초기화
            doctorSelect.value = "";


            // 진료과가 바뀌었으므로
            // 기존 날짜 / 시간 선택도 초기화
            resetReservationSelection();


            // 의료진 목록을 하나씩 확인
            doctorOptions.forEach(
                function (option) {

                    // "의료진을 선택해주세요" 기본 option
                    if (option.value === "") {

                        option.hidden = false;

                        return;
                    }


                    // 해당 의료진이 소속된 진료과 번호
                    const doctorDepartmentId =
                        option.dataset.deptId;


                    // 진료과를 선택하지 않은 경우
                    if (selectedDepartmentId === "") {

                        option.hidden = true;

                    }

                    // 선택한 진료과와
                    // 의료진의 진료과가 같은 경우
                    else if (
                        selectedDepartmentId ===
                        doctorDepartmentId
                    ) {

                        option.hidden = false;

                    }

                    // 다른 진료과의 의료진
                    else {

                        option.hidden = true;

                    }

                }
            );

        }
    );

}



// =====================================================================
// 4. 의료진 변경 시 날짜 / 시간 초기화
// =====================================================================


if (doctorSelect) {

    doctorSelect.addEventListener(
        "change",
        function () {

            // 의료진마다 예약 가능 시간이 다를 수 있으므로
            // 기존에 선택했던 날짜와 시간을 모두 초기화
            resetReservationSelection();

        }
    );

}



// =====================================================================
// 5. 예약 선택 초기화 함수
// =====================================================================
//
// 진료과 또는 의료진이 바뀌었을 때
// 기존 날짜 / 시간 선택값을 모두 없애는 함수
//
// 여러 곳에서 같은 코드를 반복하지 않기 위해
// 하나의 함수로 묶어서 사용
// =====================================================================


function resetReservationSelection() {

    // ---------------------------------------------------------
    // 날짜 값 초기화
    // ---------------------------------------------------------

    if (reservationDateInput) {

        reservationDateInput.value = "";
    }


    // 달력에서 선택되어 있던 날짜 버튼 찾기
    const selectedDateButton =
        document.querySelector(
            ".calendar-date.selected"
        );


    // 선택된 날짜가 있다면 선택 표시 제거
    if (selectedDateButton) {

        selectedDateButton.classList.remove(
            "selected"
        );
    }


    // 화면의 선택 날짜 문구 초기화
    if (selectedDateDisplay) {

        selectedDateDisplay.textContent =
            "선택한 날짜 : 없음";
    }


    // ---------------------------------------------------------
    // 시간 값 초기화
    // ---------------------------------------------------------

    if (reservationTimeInput) {

        reservationTimeInput.value = "";
    }


    // 기존 선택 시간 버튼 찾기
    const selectedTimeButton =
        document.querySelector(
            ".time-button.selected"
        );


    // 선택된 시간이 있다면 선택 표시 제거
    if (selectedTimeButton) {

        selectedTimeButton.classList.remove(
            "selected"
        );
    }


    // 화면의 선택 시간 문구 초기화
    if (selectedTimeText) {

        selectedTimeText.textContent =
            "선택한 시간 : 없음";
    }


    // 기존 시간 버튼 삭제
    if (timeButtons) {

        timeButtons.innerHTML = "";
    }


    // 날짜를 다시 선택하기 전까지
    // 시간 선택 영역 숨김
    if (reservationTimeArea) {

        reservationTimeArea.style.display =
            "none";
    }

}



// =====================================================================
// 6. 달력 생성
// =====================================================================


function renderCalendar() {

    // 달력 관련 요소가 없다면 실행하지 않음
    if (!calendarBody || !calendarTitle) {

        return;
    }


    // 기존 날짜 내용 삭제
    calendarBody.innerHTML = "";


    // 달력 상단 제목 표시
    calendarTitle.textContent =
        `${currentYear}년 ${currentMonth + 1}월`;


    // ---------------------------------------------------------
    // 현재 월의 첫 번째 날짜
    // ---------------------------------------------------------

    const firstDate =
        new Date(
            currentYear,
            currentMonth,
            1
        );


    // ---------------------------------------------------------
    // 현재 월의 마지막 날짜
    // ---------------------------------------------------------
    //
    // 다음 달의 0일을 지정하면
    // 현재 월의 마지막 날짜가 됨
    //
    // 예:
    // new Date(2026, 8, 0)
    // → 2026년 8월 31일
    // ---------------------------------------------------------

    const lastDate =
        new Date(
            currentYear,
            currentMonth + 1,
            0
        );


    // 첫날의 요일
    // 일요일 = 0 ~ 토요일 = 6
    const firstDay =
        firstDate.getDay();


    // 현재 달의 마지막 날짜 숫자
    const lastDay =
        lastDate.getDate();


    // 달력의 한 줄
    let row =
        document.createElement("tr");


    // ---------------------------------------------------------
    // 첫 번째 날짜 이전의 빈칸 생성
    // ---------------------------------------------------------

    for (
        let empty = 0;
        empty < firstDay;
        empty++
    ) {

        const emptyCell =
            document.createElement("td");

        row.appendChild(emptyCell);
    }


    // ---------------------------------------------------------
    // 1일부터 마지막 날짜까지 생성
    // ---------------------------------------------------------

    for (
        let day = 1;
        day <= lastDay;
        day++
    ) {

        // 현재 만들고 있는 날짜
        const date =
            new Date(
                currentYear,
                currentMonth,
                day
            );

        date.setHours(0, 0, 0, 0);


        // 날짜가 들어갈 td
        const cell =
            document.createElement("td");


        // 날짜 버튼 생성
        const dateButton =
            document.createElement("button");

        dateButton.type = "button";

        dateButton.textContent = day;

        dateButton.classList.add(
            "calendar-date"
        );


        // -----------------------------------------------------
        // 오늘 이전 날짜
        // -----------------------------------------------------

        if (date < today) {

            // 클릭 불가능
            dateButton.disabled = true;

            // CSS용 클래스
            dateButton.classList.add(
                "unavailable"
            );

        }

        // -----------------------------------------------------
        // 오늘 이후 날짜
        // -----------------------------------------------------

        else {

            dateButton.classList.add(
                "available"
            );


            // 날짜 클릭 이벤트
            dateButton.addEventListener(
                "click",
                function () {

                    selectDate(
                        currentYear,
                        currentMonth,
                        day,
                        dateButton
                    );

                }
            );

        }


        // 버튼을 td에 추가
        cell.appendChild(dateButton);

        // td를 현재 줄에 추가
        row.appendChild(cell);


        // 토요일이면 한 주가 끝났으므로
        // 현재 줄을 달력에 추가
        if (date.getDay() === 6) {

            calendarBody.appendChild(row);

            row =
                document.createElement("tr");
        }

    }


    // 마지막 주가 토요일로 끝나지 않았다면
    // 남은 줄 추가
    if (row.children.length > 0) {

        calendarBody.appendChild(row);
    }

}



// =====================================================================
// 7. 날짜 선택
// =====================================================================


function selectDate(
    year,
    month,
    day,
    button
) {

    // 기존에 선택된 날짜 찾기
    const selectedButton =
        document.querySelector(
            ".calendar-date.selected"
        );


    // 기존 선택 해제
    if (selectedButton) {

        selectedButton.classList.remove(
            "selected"
        );
    }


    // 새로 클릭한 날짜를 선택 상태로 표시
    button.classList.add("selected");


    // ---------------------------------------------------------
    // 날짜를 YYYY-MM-DD 형식으로 만들기
    // ---------------------------------------------------------

    // 월을 두 자리로 변환
    // 8 → "08"
    const monthText =
        String(month + 1).padStart(
            2,
            "0"
        );


    // 날짜를 두 자리로 변환
    // 5 → "05"
    const dayText =
        String(day).padStart(
            2,
            "0"
        );


    // Flask와 MySQL에서 사용할 날짜 형태
    const selectedDate =
        `${year}-${monthText}-${dayText}`;


    // hidden input에 저장
    reservationDateInput.value =
        selectedDate;


    // 화면에 선택 날짜 표시
    selectedDateDisplay.textContent =
        `선택한 날짜 : ${year}년 ${month + 1}월 ${day}일`;


    // ---------------------------------------------------------
    // 날짜를 바꾸면 기존 시간 선택 초기화
    // ---------------------------------------------------------

    reservationTimeInput.value = "";


    selectedTimeText.textContent =
        "선택한 시간 : 없음";


    // 시간 선택 영역 표시
    reservationTimeArea.style.display =
        "block";


    // 선택한 날짜 기준으로
    // 예약 가능한 시간 조회
    renderTimeButtons();

}



// =====================================================================
// 8. 예약 가능한 시간 조회 및 버튼 생성
// =====================================================================


async function renderTimeButtons() {

    // 기존 시간 버튼 삭제
    timeButtons.innerHTML = "";


    // 현재 선택된 의료진 번호
    const selectedDoctorId =
        doctorSelect.value;


    // 현재 선택된 날짜
    const selectedDate =
        reservationDateInput.value;


    // ---------------------------------------------------------
    // 의료진을 선택하지 않은 경우
    // ---------------------------------------------------------

    if (!selectedDoctorId) {

        timeButtons.innerHTML =
            "<p>의료진을 먼저 선택해주세요.</p>";

        return;
    }


    // ---------------------------------------------------------
    // 테스트용 기본 진료 시간
    // ---------------------------------------------------------
    //
    // 현재 DB에는 별도의 시간 슬롯 테이블이 없기 때문에
    // 우선 30분 단위 시간을 직접 지정함.
    //
    // 이후 doctors.work_hours 구조가 정해지면
    // 의료진별 진료시간으로 확장 가능
    // ---------------------------------------------------------

    const availableTimes = [
        "09:00",
        "09:30",
        "10:00",
        "10:30",
        "11:00",
        "11:30",

        "14:00",
        "14:30",
        "15:00",
        "15:30",
        "16:00",
        "16:30"
    ];


    try {

        // -----------------------------------------------------
        // Flask에 예약된 시간 요청
        // -----------------------------------------------------
        //
        // 예:
        // /reservation/available-times
        // ?doctor_id=1
        // &date=2026-08-20
        // -----------------------------------------------------

        const response =
            await fetch(
                `/reservation/available-times?doctor_id=${selectedDoctorId}&date=${selectedDate}`
            );


        // 서버 오류 처리
        if (!response.ok) {

            throw new Error(
                `HTTP 오류: ${response.status}`
            );
        }


        // JSON 응답 받기
        const data =
            await response.json();


        // 이미 예약된 시간
        const reservedTimes =
            data.reserved_times || [];


        // -----------------------------------------------------
        // 시간 버튼 생성
        // -----------------------------------------------------

        availableTimes.forEach(
            function (time) {

                // 시간 버튼 생성
                const button =
                    document.createElement(
                        "button"
                    );

                button.type = "button";

                button.classList.add(
                    "time-button"
                );


                // -------------------------------------------------
                // 이미 예약된 시간
                // -------------------------------------------------

                if (
                    reservedTimes.includes(time)
                ) {

                    // 클릭 불가능
                    button.disabled = true;

                    // CSS용 클래스
                    button.classList.add(
                        "unavailable"
                    );

                    // 사용자에게 예약된 시간 표시
                    button.textContent =
                        `${time} 예약완료`;

                }

                // -------------------------------------------------
                // 예약 가능한 시간
                // -------------------------------------------------

                else {

                    button.textContent =
                        time;


                    button.addEventListener(
                        "click",
                        function () {

                            selectTime(
                                time,
                                button
                            );

                        }
                    );

                }


                // 생성한 버튼 화면에 추가
                timeButtons.appendChild(
                    button
                );

            }
        );

    }

    catch (error) {

        // 개발자 도구에서 오류 확인
        console.error(
            "예약 가능 시간 조회 오류:",
            error
        );


        // 사용자 화면에 오류 표시
        timeButtons.innerHTML =
            "<p>예약 가능한 시간을 불러오지 못했습니다.</p>";

    }

}



// =====================================================================
// 9. 시간 선택
// =====================================================================


function selectTime(
    time,
    button
) {

    // 기존에 선택되어 있던 시간 버튼 찾기
    const selectedTimeButton =
        document.querySelector(
            ".time-button.selected"
        );


    // 기존 선택 해제
    if (selectedTimeButton) {

        selectedTimeButton.classList.remove(
            "selected"
        );
    }


    // 현재 클릭한 시간 선택
    button.classList.add(
        "selected"
    );


    // Flask로 전달할 hidden input에
    // 선택한 시간 저장
    reservationTimeInput.value =
        time;


    // 화면에 선택한 시간 표시
    selectedTimeText.textContent =
        `선택한 시간 : ${time}`;

}



// =====================================================================
// 10. 이전 달 이동
// =====================================================================


if (prevMonthButton) {

    prevMonthButton.addEventListener(
        "click",
        function () {

            // 현재 월보다 한 달 이전
            currentMonth--;


            // 1월에서 이전을 누른 경우
            // 전년도 12월
            if (currentMonth < 0) {

                currentMonth = 11;

                currentYear--;
            }


            // 달력을 새로 그림
            renderCalendar();

        }
    );

}



// =====================================================================
// 11. 다음 달 이동
// =====================================================================


if (nextMonthButton) {

    nextMonthButton.addEventListener(
        "click",
        function () {

            // 현재 월보다 한 달 다음
            currentMonth++;


            // 12월에서 다음을 누른 경우
            // 다음 연도 1월
            if (currentMonth > 11) {

                currentMonth = 0;

                currentYear++;
            }


            // 달력을 새로 그림
            renderCalendar();

        }
    );

}



// =====================================================================
// 12. 페이지 처음 실행
// =====================================================================


// reservation.html에 달력이 존재하는 경우에만 생성
if (calendarBody && calendarTitle) {

    renderCalendar();

}

// =====================================================================
// 13. 과거이력 재예약
// =====================================================================
//
// 과거 예약마다 각각 별도의 달력과 시간 선택 기능을 제공.
//
// 재예약 흐름
// 기존 의료진
//     ↓
// 새 날짜 선택
//     ↓
// 해당 의료진 + 날짜의 예약된 시간 DB 조회
//     ↓
// 예약 가능한 시간 선택
//     ↓
// 새로운 예약 INSERT
// =====================================================================


// 화면에 존재하는 모든 과거 예약 항목 가져오기
const historyItems =
    document.querySelectorAll(".history-item");


// 과거 예약을 하나씩 처리
historyItems.forEach(function (historyItem) {

    // ---------------------------------------------------------
    // 해당 과거 예약의 의료진 번호
    // ---------------------------------------------------------
    //
    // HTML:
    // data-doctor-id="1"
    //
    // JavaScript:
    // historyItem.dataset.doctorId
    // ---------------------------------------------------------
    const doctorId =
        historyItem.dataset.doctorId;


    // ---------------------------------------------------------
    // 해당 재예약 영역의 HTML 요소 가져오기
    // ---------------------------------------------------------

    const calendarTitle =
        historyItem.querySelector(
            ".rebooking-calendar-title"
        );

    const calendarBody =
        historyItem.querySelector(
            ".rebooking-calendar-body"
        );

    const prevButton =
        historyItem.querySelector(
            ".rebooking-prev-month"
        );

    const nextButton =
        historyItem.querySelector(
            ".rebooking-next-month"
        );


    // Flask로 전달할 날짜
    const dateInput =
        historyItem.querySelector(
            ".rebooking-date-input"
        );


    // 화면에 선택 날짜 표시
    const selectedDateDisplay =
        historyItem.querySelector(
            ".rebooking-selected-date"
        );


    // 시간 선택 영역
    const timeArea =
        historyItem.querySelector(
            ".rebooking-time-area"
        );


    // 시간 버튼 영역
    const timeButtonArea =
        historyItem.querySelector(
            ".rebooking-time-buttons"
        );


    // Flask로 전달할 시간
    const timeInput =
        historyItem.querySelector(
            ".rebooking-time-input"
        );


    // 화면에 선택 시간 표시
    const selectedTimeDisplay =
        historyItem.querySelector(
            ".rebooking-selected-time"
        );


    // ---------------------------------------------------------
    // 각 재예약 달력마다 독립적인 연도 / 월 사용
    // ---------------------------------------------------------

    let year = today.getFullYear();

    let month = today.getMonth();


    // =================================================================
    // 재예약 달력 생성
    // =================================================================

    function renderRebookingCalendar() {

        // 기존 날짜 삭제
        calendarBody.innerHTML = "";


        // 달력 제목
        calendarTitle.textContent =
            `${year}년 ${month + 1}월`;


        // 현재 달 첫날
        const firstDate =
            new Date(year, month, 1);


        // 현재 달 마지막 날
        const lastDate =
            new Date(year, month + 1, 0);


        // 첫날의 요일
        const firstDay =
            firstDate.getDay();


        // 마지막 날짜 숫자
        const lastDay =
            lastDate.getDate();


        // 한 주를 표시할 tr
        let row =
            document.createElement("tr");


        // -------------------------------------------------------------
        // 첫째 주 빈칸
        // -------------------------------------------------------------
        for (
            let empty = 0;
            empty < firstDay;
            empty++
        ) {

            const emptyCell =
                document.createElement("td");

            row.appendChild(emptyCell);
        }


        // -------------------------------------------------------------
        // 날짜 생성
        // -------------------------------------------------------------
        for (
            let day = 1;
            day <= lastDay;
            day++
        ) {

            const date =
                new Date(year, month, day);

            date.setHours(0, 0, 0, 0);


            const cell =
                document.createElement("td");


            const button =
                document.createElement("button");

            button.type = "button";

            button.textContent = day;

            button.classList.add(
                "calendar-date"
            );


            // ---------------------------------------------------------
            // 오늘 이전 날짜
            // ---------------------------------------------------------
            if (date < today) {

                // 과거 날짜 선택 불가
                button.disabled = true;

                button.classList.add(
                    "unavailable"
                );

            }

            // ---------------------------------------------------------
            // 예약 가능한 날짜
            // ---------------------------------------------------------
            else {

                button.classList.add(
                    "available"
                );


                button.addEventListener(
                    "click",
                    function () {

                        selectRebookingDate(
                            day,
                            button
                        );

                    }
                );

            }


            cell.appendChild(button);

            row.appendChild(cell);


            // 토요일이면 한 줄 완료
            if (date.getDay() === 6) {

                calendarBody.appendChild(row);

                row =
                    document.createElement("tr");
            }

        }


        // 마지막 줄 추가
        if (row.children.length > 0) {

            calendarBody.appendChild(row);
        }

    }



    // =================================================================
    // 재예약 날짜 선택
    // =================================================================

    function selectRebookingDate(
        day,
        button
    ) {

        // 현재 재예약 영역 안에서만
        // 기존 선택 날짜 찾기
        const oldSelected =
            historyItem.querySelector(
                ".calendar-date.selected"
            );


        if (oldSelected) {

            oldSelected.classList.remove(
                "selected"
            );
        }


        // 새 날짜 선택 표시
        button.classList.add(
            "selected"
        );


        // 월 두 자리
        const monthText =
            String(month + 1).padStart(
                2,
                "0"
            );


        // 일 두 자리
        const dayText =
            String(day).padStart(
                2,
                "0"
            );


        // YYYY-MM-DD
        const selectedDate =
            `${year}-${monthText}-${dayText}`;


        // Flask로 전달할 날짜
        dateInput.value =
            selectedDate;


        // 사용자에게 표시
        selectedDateDisplay.textContent =
            `선택한 날짜 : ${year}년 ${month + 1}월 ${day}일`;


        // 날짜가 바뀌었으므로
        // 기존 시간 초기화
        timeInput.value = "";


        selectedTimeDisplay.textContent =
            "선택한 시간 : 없음";


        // 시간 영역 표시
        timeArea.style.display =
            "block";


        // 해당 날짜 예약 가능 시간 조회
        renderRebookingTimes(
            selectedDate
        );

    }



    // =================================================================
    // 재예약 가능 시간 조회
    // =================================================================

    async function renderRebookingTimes(
        selectedDate
    ) {

        // 기존 시간 버튼 제거
        timeButtonArea.innerHTML = "";


        // -------------------------------------------------------------
        // 기본 진료 시간
        // -------------------------------------------------------------
        const availableTimes = [
            "09:00",
            "09:30",
            "10:00",
            "10:30",
            "11:00",
            "11:30",

            "14:00",
            "14:30",
            "15:00",
            "15:30",
            "16:00",
            "16:30"
        ];


        try {

            // ---------------------------------------------------------
            // 기존 신규 예약에서 사용하는 Flask API를 그대로 사용
            // ---------------------------------------------------------
            //
            // doctor_id
            // → 과거 예약의 의료진
            //
            // date
            // → 사용자가 새로 선택한 날짜
            // ---------------------------------------------------------
            const response =
                await fetch(
                    `/reservation/available-times?doctor_id=${doctorId}&date=${selectedDate}`
                );


            if (!response.ok) {

                throw new Error(
                    `HTTP 오류: ${response.status}`
                );
            }


            const data =
                await response.json();


            // 이미 예약된 시간 목록
            const reservedTimes =
                data.reserved_times || [];


            // ---------------------------------------------------------
            // 시간 버튼 생성
            // ---------------------------------------------------------
            availableTimes.forEach(
                function (time) {

                    const button =
                        document.createElement(
                            "button"
                        );


                    button.type =
                        "button";


                    button.classList.add(
                        "time-button"
                    );


                    // -------------------------------------------------
                    // 이미 예약된 시간
                    // -------------------------------------------------
                    if (
                        reservedTimes.includes(time)
                    ) {

                        button.disabled =
                            true;


                        button.classList.add(
                            "unavailable"
                        );


                        button.textContent =
                            `${time} 예약완료`;

                    }

                    // -------------------------------------------------
                    // 예약 가능한 시간
                    // -------------------------------------------------
                    else {

                        button.textContent =
                            time;


                        button.addEventListener(
                            "click",
                            function () {

                                // 현재 재예약 영역에서만
                                // 기존 선택 시간 찾기
                                const oldSelected =
                                    historyItem.querySelector(
                                        ".time-button.selected"
                                    );


                                // 기존 선택 해제
                                if (oldSelected) {

                                    oldSelected.classList.remove(
                                        "selected"
                                    );
                                }


                                // 현재 시간 선택
                                button.classList.add(
                                    "selected"
                                );


                                // Flask로 전달
                                timeInput.value =
                                    time;


                                // 사용자에게 표시
                                selectedTimeDisplay.textContent =
                                    `선택한 시간 : ${time}`;

                            }
                        );

                    }


                    // 시간 버튼 화면에 추가
                    timeButtonArea.appendChild(
                        button
                    );

                }
            );

        }

        catch (error) {

            console.error(
                "재예약 가능 시간 조회 오류:",
                error
            );


            timeButtonArea.innerHTML =
                "<p>예약 가능한 시간을 불러오지 못했습니다.</p>";

        }

    }



    // =================================================================
    // 이전 달
    // =================================================================

    prevButton.addEventListener(
        "click",
        function () {

            month--;


            if (month < 0) {

                month = 11;

                year--;
            }


            renderRebookingCalendar();

        }
    );



    // =================================================================
    // 다음 달
    // =================================================================

    nextButton.addEventListener(
        "click",
        function () {

            month++;


            if (month > 11) {

                month = 0;

                year++;
            }


            renderRebookingCalendar();

        }
    );



    // =================================================================
    // 각 과거 예약의 달력 최초 생성
    // =================================================================

    renderRebookingCalendar();

});