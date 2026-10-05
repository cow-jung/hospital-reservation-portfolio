// =====================================================================
// reservation_edit.js
// 예약 변경
// =====================================================================


// =====================================================================
// 오늘
// =====================================================================

const now =
    new Date();


const today =
    new Date(
        now.getFullYear(),
        now.getMonth(),
        now.getDate()
    );



// =====================================================================
// 요소 가져오기
// =====================================================================


// 의료진 ID
const doctorId =
    document.getElementById(
        "edit_doctor_id"
    );


// 변경 날짜
const dateInput =
    document.getElementById(
        "edit_reservation_date"
    );


// 변경 시간
const timeInput =
    document.getElementById(
        "edit_reservation_time"
    );


// 달력 제목
const calendarTitle =
    document.getElementById(
        "edit_calendar_title"
    );


// 달력 body
const calendarBody =
    document.getElementById(
        "edit_calendar_body"
    );


// 이전 달 버튼
const prevButton =
    document.getElementById(
        "edit_prev_month"
    );


// 다음 달 버튼
const nextButton =
    document.getElementById(
        "edit_next_month"
    );


// 선택 날짜 표시
const selectedDateText =
    document.getElementById(
        "edit_selected_date"
    );


// 선택 시간 표시
const selectedTimeText =
    document.getElementById(
        "edit_selected_time"
    );


// 시간 영역
const timeArea =
    document.getElementById(
        "edit_time_area"
    );


// 시간 버튼 영역
const timeButtons =
    document.getElementById(
        "edit_time_buttons"
    );


// 예약 변경 form
const form =
    document.getElementById(
        "edit_reservation_form"
    );



// =====================================================================
// 확정 상태에서는 form 자체가 없으므로
// form이 있을 때만 실행
// =====================================================================

if (form) {


    // =================================================================
    // 달력 현재 년 / 월
    // =================================================================

    let year =
        today.getFullYear();


    let month =
        today.getMonth();



    // =================================================================
    // 달력 생성
    // =================================================================

    function renderCalendar() {

        calendarBody.innerHTML =
            "";


        calendarTitle.textContent =
            year +
            "년 " +
            (month + 1) +
            "월";


        // 이번 달 첫날
        const first =
            new Date(
                year,
                month,
                1
            );


        // 이번 달 마지막 날
        const last =
            new Date(
                year,
                month + 1,
                0
            );


        let row =
            document.createElement(
                "tr"
            );



        // =============================================================
        // 첫 번째 날짜 앞 빈칸
        // =============================================================

        for (
            let i = 0;
            i < first.getDay();
            i++
        ) {

            row.appendChild(
                document.createElement(
                    "td"
                )
            );
        }



        // =============================================================
        // 날짜 버튼 생성
        // =============================================================

        for (
            let day = 1;
            day <= last.getDate();
            day++
        ) {

            const date =
                new Date(
                    year,
                    month,
                    day
                );


            date.setHours(
                0,
                0,
                0,
                0
            );


            // 요일
            const dayOfWeek =
                date.getDay();


            // 일요일
            const sunday =
                dayOfWeek === 0;


            // 토요일
            const saturday =
                dayOfWeek === 6;


            // 공휴일
            const holiday =
                window.isHospitalHoliday(
                    year,
                    month,
                    day
                );


            const cell =
                document.createElement(
                    "td"
                );


            const button =
                document.createElement(
                    "button"
                );


            button.type =
                "button";


            button.textContent =
                day;


            button.classList.add(
                "calendar-date"
            );



            // =========================================================
            // 일요일 표시
            // =========================================================

            if (sunday) {

                button.classList.add(
                    "sunday"
                );
            }



            // =========================================================
            // 토요일 표시
            // =========================================================

            if (saturday) {

                button.classList.add(
                    "saturday"
                );
            }



            // =========================================================
            // 공휴일 표시
            // =========================================================

            if (holiday) {

                button.classList.add(
                    "holiday"
                );
            }



            // =========================================================
            // 선택 불가 날짜
            //
            // 1. 과거 날짜
            // 2. 일요일
            // 3. 공휴일
            // =========================================================

            if (
                date < today ||
                sunday ||
                holiday
            ) {

                button.disabled =
                    true;


                button.classList.add(
                    "unavailable"
                );

            }

            else {

                // =====================================================
                // 선택 가능한 날짜
                // =====================================================

                button.addEventListener(
                    "click",
                    function () {

                        selectDate(
                            year,
                            month,
                            day,
                            button
                        );

                    }
                );

            }


            cell.appendChild(
                button
            );


            row.appendChild(
                cell
            );


            // =========================================================
            // 토요일이면 한 줄 종료
            // =========================================================

            if (
                date.getDay() === 6
            ) {

                calendarBody.appendChild(
                    row
                );


                row =
                    document.createElement(
                        "tr"
                    );
            }
        }



        // =============================================================
        // 마지막 남은 줄 추가
        // =============================================================

        if (
            row.children.length > 0
        ) {

            calendarBody.appendChild(
                row
            );
        }
    }



    // =================================================================
    // 날짜 선택
    // =================================================================

    function selectDate(
        selectedYear,
        selectedMonth,
        selectedDay,
        button
    ) {

        // =============================================================
        // 기존 선택 날짜 해제
        // =============================================================

        const old =
            calendarBody.querySelector(
                ".selected"
            );


        if (old) {

            old.classList.remove(
                "selected"
            );
        }


        // =============================================================
        // 새 날짜 선택
        // =============================================================

        button.classList.add(
            "selected"
        );


        // =============================================================
        // YYYY-MM-DD
        // =============================================================

        const dateString =
            window.formatHospitalDate(
                selectedYear,
                selectedMonth,
                selectedDay
            );


        // hidden input에 날짜 저장
        dateInput.value =
            dateString;


        // 시간 초기화
        timeInput.value =
            "";


        // 선택 날짜 표시
        selectedDateText.textContent =
            "선택한 날짜 : "
            + selectedYear
            + "년 "
            + (selectedMonth + 1)
            + "월 "
            + selectedDay
            + "일";


        // 선택 시간 초기화
        selectedTimeText.textContent =
            "선택한 시간 : 없음";


        // 시간 영역 표시
        timeArea.style.display =
            "block";


        // 예약 가능시간 조회
        loadTimes(
            dateString
        );
    }



    // =================================================================
    // 예약 가능시간 조회
    // =================================================================

    async function loadTimes(
        selectedDate
    ) {

        // =============================================================
        // 기존 시간 초기화
        // =============================================================

        timeButtons.innerHTML =
            "";


        timeInput.value =
            "";


        selectedTimeText.textContent =
            "선택한 시간 : 없음";



        // =============================================================
        // 병원 공통 진료시간
        //
        // hospital_schedule.js 사용
        //
        // - 일요일 휴진
        // - 공휴일 휴진
        // - 토요일 13시까지
        // =============================================================

        const hospitalTimes =
            window.getHospitalTimes(
                selectedDate
            );


        // =============================================================
        // 병원 전체 휴진일
        // =============================================================

        if (
            hospitalTimes.length === 0
        ) {

            timeButtons.innerHTML =
                `
                <p class="closed-message">
                    휴진일입니다.
                </p>
                `;

            return;
        }



        try {

            // =========================================================
            // 선택 의료진의 예약된 시간
            //
            // 동시에 saturday_available 확인
            // =========================================================

            const response =
                await fetch(
                    `/reservation/available-times?doctor_id=${doctorId.value}&date=${selectedDate}`
                );


            if (!response.ok) {

                throw new Error(
                    "예약시간 조회 실패"
                );
            }


            const data =
                await response.json();



            // =========================================================
            // 해당 의료진 토요일 진료 안 함
            // =========================================================

            if (
                data.saturday_closed
            ) {

                timeButtons.innerHTML =
                    `
                    <p class="closed-message">
                        해당 의료진은 토요일 진료가 없습니다.
                    </p>
                    `;


                timeInput.value =
                    "";


                selectedTimeText.textContent =
                    "선택한 시간 : 없음";


                return;
            }



            // =========================================================
            // 이미 예약된 시간
            // =========================================================

            const reservedTimes =
                data.reserved_times || [];



            // =========================================================
            // 선택 날짜 객체
            // =========================================================

            const selectedDateObject =
                new Date(
                    selectedDate +
                    "T00:00:00"
                );



            // =========================================================
            // 오늘인지 확인
            // =========================================================

            const isToday =

                selectedDateObject.getFullYear()
                    === today.getFullYear()

                &&

                selectedDateObject.getMonth()
                    === today.getMonth()

                &&

                selectedDateObject.getDate()
                    === today.getDate();



            // =========================================================
            // 시간 버튼 생성
            // =========================================================

            hospitalTimes.forEach(
                function (time) {


                    // =================================================
                    // 오늘 현재시간 이전 제거
                    // =================================================

                    if (isToday) {

                        const [
                            hour,
                            minute
                        ] =
                            time
                                .split(":")
                                .map(Number);


                        const current =
                            new Date();


                        const slot =
                            new Date();


                        slot.setHours(
                            hour,
                            minute,
                            0,
                            0
                        );


                        // 현재시간보다 이전이면
                        // 버튼 생성하지 않음
                        if (
                            slot <= current
                        ) {

                            return;
                        }
                    }



                    // =================================================
                    // 시간 버튼 생성
                    // =================================================

                    const button =
                        document.createElement(
                            "button"
                        );


                    button.type =
                        "button";


                    button.classList.add(
                        "time-button"
                    );



                    // =================================================
                    // 이미 예약된 시간
                    // =================================================

                    if (
                        reservedTimes.includes(
                            time
                        )
                    ) {

                        button.disabled =
                            true;


                        button.classList.add(
                            "unavailable"
                        );


                        button.textContent =
                            time +
                            " 예약완료";

                    }


                    // =================================================
                    // 예약 가능한 시간
                    // =================================================

                    else {

                        button.textContent =
                            time;


                        button.addEventListener(
                            "click",
                            function () {


                                // 기존 선택 시간
                                const old =
                                    timeButtons.querySelector(
                                        ".selected"
                                    );


                                if (old) {

                                    old.classList.remove(
                                        "selected"
                                    );
                                }


                                // 새 시간 선택
                                button.classList.add(
                                    "selected"
                                );


                                // hidden input 저장
                                timeInput.value =
                                    time;


                                // 선택 시간 표시
                                selectedTimeText.textContent =
                                    "선택한 시간 : "
                                    + time;

                            }
                        );

                    }


                    timeButtons.appendChild(
                        button
                    );

                }
            );



            // =========================================================
            // 예약 가능한 시간이 없는 경우
            // =========================================================

            if (
                timeButtons.children.length === 0
            ) {

                timeButtons.innerHTML =
                    `
                    <p class="no-time-message">
                        예약 가능한 시간이 없습니다.
                    </p>
                    `;
            }

        }

        catch (error) {

            console.error(
                error
            );


            timeButtons.innerHTML =
                `
                <p class="no-time-message">
                    예약 가능한 시간을 불러오지 못했습니다.
                </p>
                `;
        }
    }



    // =================================================================
    // 이전 달
    // =================================================================

    if (prevButton) {

        prevButton.addEventListener(
            "click",
            function () {

                month--;


                if (
                    month < 0
                ) {

                    month = 11;

                    year--;
                }


                renderCalendar();

            }
        );
    }



    // =================================================================
    // 다음 달
    // =================================================================

    if (nextButton) {

        nextButton.addEventListener(
            "click",
            function () {

                month++;


                if (
                    month > 11
                ) {

                    month = 0;

                    year++;
                }


                renderCalendar();

            }
        );
    }



    // =================================================================
    // 예약 변경 제출 검사
    // =================================================================

    form.addEventListener(
        "submit",
        function (event) {


            // =========================================================
            // 날짜 미선택
            // =========================================================

            if (
                !dateInput.value
            ) {

                event.preventDefault();


                alert(
                    "변경할 날짜를 선택해주세요."
                );


                return;
            }



            // =========================================================
            // 시간 미선택
            // =========================================================

            if (
                !timeInput.value
            ) {

                event.preventDefault();


                alert(
                    "변경할 시간을 선택해주세요."
                );


                return;
            }



            // =========================================================
            // 최종 변경 확인
            // =========================================================

            if (
                !confirm(
                    "선택한 날짜와 시간으로 예약을 변경하시겠습니까?"
                )
            ) {

                event.preventDefault();
            }

        }
    );



    // =================================================================
    // 최초 달력 출력
    // =================================================================

    renderCalendar();

}