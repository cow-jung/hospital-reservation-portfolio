// =====================================================================
// reservation.js
// 신규예약 + 과거이력 재예약
// =====================================================================


// =====================================================================
// 오늘
// =====================================================================

const now = new Date();


const today =
    new Date(
        now.getFullYear(),
        now.getMonth(),
        now.getDate()
    );



// =====================================================================
// 공통 달력 날짜 버튼 생성
// =====================================================================

function createCalendarButton(
    year,
    month,
    day,
    selectFunction
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


    const dayOfWeek =
        date.getDay();


    const sunday =
        dayOfWeek === 0;


    const saturday =
        dayOfWeek === 6;


    const holiday =
        window.isHospitalHoliday(
            year,
            month,
            day
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



    // =============================================================
    // 일요일
    // =============================================================

    if (sunday) {

        button.classList.add(
            "sunday"
        );
    }



    // =============================================================
    // 토요일
    // =============================================================

    if (saturday) {

        button.classList.add(
            "saturday"
        );
    }



    // =============================================================
    // 공휴일
    // =============================================================

    if (holiday) {

        button.classList.add(
            "holiday"
        );
    }



    // =============================================================
    // 선택 불가
    //
    // 1. 과거 날짜
    // 2. 일요일
    // 3. 공휴일
    // =============================================================

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

        button.addEventListener(
            "click",
            function () {

                selectFunction(
                    year,
                    month,
                    day,
                    button
                );

            }
        );
    }


    return button;
}



// =====================================================================
// 공통 예약 가능시간 불러오기
//
// 신규예약 + 과거이력 재예약 공통
//
// 여기서 Flask API가
// doctors.saturday_available 값을 확인함.
//
// saturday_closed = true
// → 해당 의료진은 토요일 진료 안 함
// =====================================================================

async function loadReservationTimes(
    doctorId,
    selectedDate,
    targetArea,
    targetInput,
    targetText
) {

    // 기존 시간 버튼 제거
    targetArea.innerHTML =
        "";


    // 기존 선택 시간 초기화
    targetInput.value =
        "";


    targetText.textContent =
        "선택한 시간 : 없음";


    // =================================================================
    // 병원 공통 진료시간
    //
    // hospital_schedule.js에서 처리
    //
    // - 일요일
    // - 공휴일
    // - 토요일 13시까지
    // =================================================================

    const hospitalTimes =
        window.getHospitalTimes(
            selectedDate
        );


    // =================================================================
    // 병원 전체 휴진일
    // =================================================================

    if (
        hospitalTimes.length === 0
    ) {

        targetArea.innerHTML =
            `
            <p class="closed-message">
                휴진일입니다.
            </p>
            `;

        return;
    }


    try {

        // =================================================================
        // 해당 의료진의 예약된 시간 조회
        //
        // 동시에 saturday_available 확인
        // =================================================================

        const response =
            await fetch(
                `/reservation/available-times?doctor_id=${doctorId}&date=${selectedDate}`
            );


        if (!response.ok) {

            throw new Error(
                "예약시간 조회 실패"
            );
        }


        const data =
            await response.json();



        // =================================================================
        // 해당 의료진 토요일 진료 없음
        // =================================================================

        if (
            data.saturday_closed
        ) {

            targetArea.innerHTML =
                `
                <p class="closed-message">
                    해당 의료진은 토요일 진료가 없습니다.
                </p>
                `;

            return;
        }



        // =================================================================
        // 이미 예약된 시간
        // =================================================================

        const reservedTimes =
            data.reserved_times || [];



        // =================================================================
        // 선택 날짜 객체
        // =================================================================

        const selectedDateObject =
            new Date(
                selectedDate +
                "T00:00:00"
            );



        // =================================================================
        // 오늘인지 확인
        // =================================================================

        const isToday =

            selectedDateObject.getFullYear()
                === today.getFullYear()

            &&

            selectedDateObject.getMonth()
                === today.getMonth()

            &&

            selectedDateObject.getDate()
                === today.getDate();



        // =================================================================
        // 시간 버튼 생성
        // =================================================================

        hospitalTimes.forEach(
            function (time) {


                // =========================================================
                // 오늘 현재시간 이전 시간 제거
                // =========================================================

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


                    if (
                        slot <= current
                    ) {

                        return;
                    }
                }



                // =========================================================
                // 시간 버튼 생성
                // =========================================================

                const button =
                    document.createElement(
                        "button"
                    );


                button.type =
                    "button";


                button.classList.add(
                    "time-button"
                );



                // =========================================================
                // 이미 예약된 시간
                // =========================================================

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


                // =========================================================
                // 예약 가능한 시간
                // =========================================================

                else {

                    button.textContent =
                        time;


                    button.addEventListener(
                        "click",
                        function () {


                            const oldSelected =
                                targetArea.querySelector(
                                    ".time-button.selected"
                                );


                            if (oldSelected) {

                                oldSelected.classList.remove(
                                    "selected"
                                );
                            }


                            button.classList.add(
                                "selected"
                            );


                            targetInput.value =
                                time;


                            targetText.textContent =
                                "선택한 시간 : "
                                + time;

                        }
                    );

                }


                targetArea.appendChild(
                    button
                );

            }
        );



        // =================================================================
        // 표시할 시간이 하나도 없는 경우
        // =================================================================

        if (
            targetArea.children.length === 0
        ) {

            targetArea.innerHTML =
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


        targetArea.innerHTML =
            `
            <p class="no-time-message">
                예약 가능한 시간을 불러오지 못했습니다.
            </p>
            `;
    }
}



// =====================================================================
// =====================================================================
// 신규 예약
// =====================================================================
// =====================================================================


// =====================================================================
// 요소 가져오기
// =====================================================================

const departmentSelect =
    document.getElementById(
        "dept_id"
    );


const doctorSelect =
    document.getElementById(
        "doctor_id"
    );


const newCalendarTitle =
    document.getElementById(
        "new_calendar_title"
    );


const newCalendarBody =
    document.getElementById(
        "new_calendar_body"
    );


const newPrev =
    document.getElementById(
        "new_prev_month"
    );


const newNext =
    document.getElementById(
        "new_next_month"
    );


const newDateInput =
    document.getElementById(
        "new_reservation_date"
    );


const newTimeInput =
    document.getElementById(
        "new_reservation_time"
    );


const newDateText =
    document.getElementById(
        "new_selected_date"
    );


const newTimeText =
    document.getElementById(
        "new_selected_time"
    );


const newTimeArea =
    document.getElementById(
        "new_time_area"
    );


const newTimeButtons =
    document.getElementById(
        "new_time_buttons"
    );


const newForm =
    document.getElementById(
        "new_reservation_form"
    );



// =====================================================================
// 신규예약 달력 현재 년 / 월
// =====================================================================

let newYear =
    today.getFullYear();


let newMonth =
    today.getMonth();



// =====================================================================
// 진료과 선택에 따른 의료진 필터
// =====================================================================

function filterDoctors() {

    if (
        !departmentSelect ||
        !doctorSelect
    ) {

        return;
    }


    const deptId =
        departmentSelect.value;


    const options =
        doctorSelect.querySelectorAll(
            "option"
        );


    options.forEach(
        function (option) {


            // 기본 선택 option
            if (
                option.value === ""
            ) {

                option.hidden =
                    false;

                return;
            }


            // 진료과가 없거나
            // 해당 과 의료진이 아닌 경우 숨김
            option.hidden =
                !deptId ||
                option.dataset.deptId
                !== deptId;

        }
    );
}



// =====================================================================
// 신규예약 날짜 / 시간 선택 초기화
// =====================================================================

function resetNewSelection() {

    newDateInput.value =
        "";


    newTimeInput.value =
        "";


    newDateText.textContent =
        "선택한 날짜 : 없음";


    newTimeText.textContent =
        "선택한 시간 : 없음";


    newTimeButtons.innerHTML =
        "";


    newTimeArea.style.display =
        "none";


    const selected =
        newCalendarBody.querySelector(
            ".selected"
        );


    if (selected) {

        selected.classList.remove(
            "selected"
        );
    }
}



// =====================================================================
// 진료과 변경
// =====================================================================

if (departmentSelect) {

    departmentSelect.addEventListener(
        "change",
        function () {

            // 의료진 선택 초기화
            doctorSelect.value =
                "";


            // 진료과 의료진 필터
            filterDoctors();


            // 예약 날짜 / 시간 초기화
            resetNewSelection();

        }
    );
}



// =====================================================================
// 의료진 변경
// =====================================================================

if (doctorSelect) {

    doctorSelect.addEventListener(
        "change",
        function () {

            resetNewSelection();

        }
    );
}



// =====================================================================
// 신규예약 달력 생성
// =====================================================================

function renderNewCalendar() {

    newCalendarBody.innerHTML =
        "";


    newCalendarTitle.textContent =
        newYear +
        "년 " +
        (newMonth + 1) +
        "월";


    const first =
        new Date(
            newYear,
            newMonth,
            1
        );


    const last =
        new Date(
            newYear,
            newMonth + 1,
            0
        );


    let row =
        document.createElement(
            "tr"
        );



    // =================================================================
    // 첫 번째 날짜 앞 빈칸
    // =================================================================

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



    // =================================================================
    // 날짜 생성
    // =================================================================

    for (
        let day = 1;
        day <= last.getDate();
        day++
    ) {

        const date =
            new Date(
                newYear,
                newMonth,
                day
            );


        const cell =
            document.createElement(
                "td"
            );


        const button =
            createCalendarButton(
                newYear,
                newMonth,
                day,
                selectNewDate
            );


        cell.appendChild(
            button
        );


        row.appendChild(
            cell
        );


        // 토요일이면 한 줄 완료
        if (
            date.getDay() === 6
        ) {

            newCalendarBody.appendChild(
                row
            );


            row =
                document.createElement(
                    "tr"
                );
        }
    }



    // 마지막 남은 줄 추가
    if (
        row.children.length > 0
    ) {

        newCalendarBody.appendChild(
            row
        );
    }
}



// =====================================================================
// 신규예약 날짜 선택
// =====================================================================

function selectNewDate(
    year,
    month,
    day,
    button
) {

    // 의료진을 먼저 선택해야 함
    if (
        !doctorSelect.value
    ) {

        alert(
            "의료진을 먼저 선택해주세요."
        );

        return;
    }


    // 기존 선택 날짜 해제
    const old =
        newCalendarBody.querySelector(
            ".selected"
        );


    if (old) {

        old.classList.remove(
            "selected"
        );
    }


    // 선택 날짜 표시
    button.classList.add(
        "selected"
    );


    const dateString =
        window.formatHospitalDate(
            year,
            month,
            day
        );


    newDateInput.value =
        dateString;


    newTimeInput.value =
        "";


    newDateText.textContent =
        "선택한 날짜 : "
        + year
        + "년 "
        + (month + 1)
        + "월 "
        + day
        + "일";


    newTimeText.textContent =
        "선택한 시간 : 없음";


    newTimeArea.style.display =
        "block";


    // =================================================================
    // 선택 의료진 + 날짜 기준 예약시간
    // =================================================================

    loadReservationTimes(
        doctorSelect.value,
        dateString,
        newTimeButtons,
        newTimeInput,
        newTimeText
    );
}



// =====================================================================
// 신규예약 이전 달
// =====================================================================

if (newPrev) {

    newPrev.addEventListener(
        "click",
        function () {

            newMonth--;


            if (
                newMonth < 0
            ) {

                newMonth = 11;

                newYear--;
            }


            renderNewCalendar();

        }
    );
}



// =====================================================================
// 신규예약 다음 달
// =====================================================================

if (newNext) {

    newNext.addEventListener(
        "click",
        function () {

            newMonth++;


            if (
                newMonth > 11
            ) {

                newMonth = 0;

                newYear++;
            }


            renderNewCalendar();

        }
    );
}



// =====================================================================
// 신규예약 제출 검사
// =====================================================================

if (newForm) {

    newForm.addEventListener(
        "submit",
        function (event) {

            // 날짜 미선택
            if (
                !newDateInput.value
            ) {

                event.preventDefault();


                alert(
                    "예약 날짜를 선택해주세요."
                );


                return;
            }


            // 시간 미선택
            if (
                !newTimeInput.value
            ) {

                event.preventDefault();


                alert(
                    "예약 시간을 선택해주세요."
                );


                return;
            }

        }
    );
}



// =====================================================================
// =====================================================================
// 과거 이력 재예약
// =====================================================================
// =====================================================================


// =====================================================================
// 요소 가져오기
// =====================================================================

const reButtons =
    document.querySelectorAll(
        ".history-rebook-button"
    );


const rePanel =
    document.getElementById(
        "rebook_panel"
    );


const reDoctorId =
    document.getElementById(
        "re_doctor_id"
    );


const reReservationId =
    document.getElementById(
        "re_source_reservation_id"
    );


const reDeptName =
    document.getElementById(
        "re_dept_name"
    );


const reDoctorName =
    document.getElementById(
        "re_doctor_name"
    );


const reCalendarTitle =
    document.getElementById(
        "re_calendar_title"
    );


const reCalendarBody =
    document.getElementById(
        "re_calendar_body"
    );


const rePrev =
    document.getElementById(
        "re_prev_month"
    );


const reNext =
    document.getElementById(
        "re_next_month"
    );


const reDateInput =
    document.getElementById(
        "re_reservation_date"
    );


const reTimeInput =
    document.getElementById(
        "re_reservation_time"
    );


const reDateText =
    document.getElementById(
        "re_selected_date"
    );


const reTimeText =
    document.getElementById(
        "re_selected_time"
    );


const reTimeArea =
    document.getElementById(
        "re_time_area"
    );


const reTimeButtons =
    document.getElementById(
        "re_time_buttons"
    );


const reForm =
    document.getElementById(
        "rebook_form"
    );



// =====================================================================
// 재예약 달력 현재 년 / 월
// =====================================================================

let reYear =
    today.getFullYear();


let reMonth =
    today.getMonth();



// =====================================================================
// 과거이력 재예약 버튼
// =====================================================================

reButtons.forEach(
    function (button) {

        button.addEventListener(
            "click",
            function () {

                // 의료진 번호 저장
                reDoctorId.value =
                    button.dataset.doctorId;


                // 원래 예약번호 저장
                reReservationId.value =
                    button.dataset.reservationId;


                // 진료과 표시
                reDeptName.textContent =
                    button.dataset.deptName;


                // 의료진 표시
                reDoctorName.textContent =
                    button.dataset.doctorName;


                // 기존 선택값 초기화
                reDateInput.value =
                    "";


                reTimeInput.value =
                    "";


                reDateText.textContent =
                    "선택한 날짜 : 없음";


                reTimeText.textContent =
                    "선택한 시간 : 없음";


                reTimeButtons.innerHTML =
                    "";


                reTimeArea.style.display =
                    "none";


                // 현재 달부터 시작
                reYear =
                    today.getFullYear();


                reMonth =
                    today.getMonth();


                // 재예약 영역 표시
                rePanel.style.display =
                    "block";


                // 달력 생성
                renderReCalendar();


                // 재예약 영역으로 이동
                rePanel.scrollIntoView(
                    {
                        behavior:
                            "smooth"
                    }
                );

            }
        );
    }
);



// =====================================================================
// 재예약 달력 생성
// =====================================================================

function renderReCalendar() {

    reCalendarBody.innerHTML =
        "";


    reCalendarTitle.textContent =
        reYear +
        "년 " +
        (reMonth + 1) +
        "월";


    const first =
        new Date(
            reYear,
            reMonth,
            1
        );


    const last =
        new Date(
            reYear,
            reMonth + 1,
            0
        );


    let row =
        document.createElement(
            "tr"
        );



    // =================================================================
    // 첫 번째 날짜 앞 빈칸
    // =================================================================

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



    // =================================================================
    // 날짜 생성
    // =================================================================

    for (
        let day = 1;
        day <= last.getDate();
        day++
    ) {

        const date =
            new Date(
                reYear,
                reMonth,
                day
            );


        const cell =
            document.createElement(
                "td"
            );


        const button =
            createCalendarButton(
                reYear,
                reMonth,
                day,
                selectReDate
            );


        cell.appendChild(
            button
        );


        row.appendChild(
            cell
        );


        if (
            date.getDay() === 6
        ) {

            reCalendarBody.appendChild(
                row
            );


            row =
                document.createElement(
                    "tr"
                );
        }
    }



    if (
        row.children.length > 0
    ) {

        reCalendarBody.appendChild(
            row
        );
    }
}



// =====================================================================
// 재예약 날짜 선택
// =====================================================================

function selectReDate(
    year,
    month,
    day,
    button
) {

    // 기존 선택 날짜 해제
    const old =
        reCalendarBody.querySelector(
            ".selected"
        );


    if (old) {

        old.classList.remove(
            "selected"
        );
    }


    // 새 날짜 선택
    button.classList.add(
        "selected"
    );


    const dateString =
        window.formatHospitalDate(
            year,
            month,
            day
        );


    reDateInput.value =
        dateString;


    reTimeInput.value =
        "";


    reDateText.textContent =
        "선택한 날짜 : "
        + year
        + "년 "
        + (month + 1)
        + "월 "
        + day
        + "일";


    reTimeText.textContent =
        "선택한 시간 : 없음";


    reTimeArea.style.display =
        "block";


    // =================================================================
    // 과거이력의 의료진 ID를 이용해서
    // 해당 날짜 예약시간 조회
    // =================================================================

    loadReservationTimes(
        reDoctorId.value,
        dateString,
        reTimeButtons,
        reTimeInput,
        reTimeText
    );
}



// =====================================================================
// 재예약 이전 달
// =====================================================================

if (rePrev) {

    rePrev.addEventListener(
        "click",
        function () {

            reMonth--;


            if (
                reMonth < 0
            ) {

                reMonth = 11;

                reYear--;
            }


            renderReCalendar();

        }
    );
}



// =====================================================================
// 재예약 다음 달
// =====================================================================

if (reNext) {

    reNext.addEventListener(
        "click",
        function () {

            reMonth++;


            if (
                reMonth > 11
            ) {

                reMonth = 0;

                reYear++;
            }


            renderReCalendar();

        }
    );
}



// =====================================================================
// 재예약 제출 검사
// =====================================================================

if (reForm) {

    reForm.addEventListener(
        "submit",
        function (event) {


            // 날짜 미선택
            if (
                !reDateInput.value
            ) {

                event.preventDefault();


                alert(
                    "새 예약 날짜를 선택해주세요."
                );


                return;
            }


            // 시간 미선택
            if (
                !reTimeInput.value
            ) {

                event.preventDefault();


                alert(
                    "새 예약 시간을 선택해주세요."
                );


                return;
            }


            // 최종 확인
            if (
                !confirm(
                    "선택한 날짜와 시간으로 재예약하시겠습니까?"
                )
            ) {

                event.preventDefault();
            }

        }
    );
}



// =====================================================================
// 최초 실행
// =====================================================================

// 자동선택으로 들어온 경우에도
// 해당 진료과 의료진만 보이도록 필터
filterDoctors();


// 신규예약 달력 출력
renderNewCalendar();