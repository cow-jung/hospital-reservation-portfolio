// admin_department.html 전용 스크립트
// 1. 실시간 검색: 서버에 다시 요청하지 않고, 화면에 이미 그려진 행들을
//    진료과명/소개 기준으로 즉시 보여줬다 숨겼다 합니다.
// 2. 드래그 정렬: 행을 드래그해서 순서를 바꾸면, 새 순서를
//    /admin/department/reorder 로 전송해서 DB의 display_order를 갱신합니다.

document.addEventListener("DOMContentLoaded", function () {
    initLiveSearch();
    initDragReorder();
});

// =========================================================
// 1. 실시간 검색
// =========================================================
function initLiveSearch() {
    var input = document.getElementById("dept-search-input");
    var rows = document.querySelectorAll("#dept-table-body .dept-row");
    var noResultMsg = document.getElementById("dept-no-result");

    if (!input) {
        return;
    }

    input.addEventListener("input", function () {
        var keyword = input.value.trim().toLowerCase();
        var visibleCount = 0;

        rows.forEach(function (row) {
            var name = row.getAttribute("data-name") || "";
            var desc = row.getAttribute("data-desc") || "";
            var matched = !keyword || name.indexOf(keyword) !== -1 || desc.indexOf(keyword) !== -1;

            row.style.display = matched ? "" : "none";
            if (matched) {
                visibleCount += 1;
            }
        });

        if (noResultMsg) {
            noResultMsg.style.display = visibleCount === 0 ? "block" : "none";
        }
    });
}

// =========================================================
// 2. 드래그로 표시 순서 변경
// =========================================================
function initDragReorder() {
    var tbody = document.getElementById("dept-table-body");
    if (!tbody) {
        return;
    }

    var draggingRow = null;

    tbody.querySelectorAll(".dept-row").forEach(function (row) {
        row.addEventListener("dragstart", function () {
            draggingRow = row;
            row.classList.add("dept-row-dragging");
        });

        row.addEventListener("dragend", function () {
            row.classList.remove("dept-row-dragging");
            draggingRow = null;
            saveNewOrder(tbody);
        });

        row.addEventListener("dragover", function (event) {
            event.preventDefault();
            if (!draggingRow || draggingRow === row) {
                return;
            }
            var rect = row.getBoundingClientRect();
            var isAfter = (event.clientY - rect.top) > rect.height / 2;
            tbody.insertBefore(draggingRow, isAfter ? row.nextSibling : row);
        });
    });
}

function saveNewOrder(tbody) {
    var orderedIds = Array.from(tbody.querySelectorAll(".dept-row")).map(function (row) {
        return parseInt(row.getAttribute("data-dept-id"), 10);
    });

    // 화면에 보이는 순서 번호도 바로 갱신 (새로고침 없이)
    tbody.querySelectorAll(".dept-row").forEach(function (row, index) {
        var orderCell = row.querySelector(".dept-order-cell");
        if (orderCell) {
            orderCell.textContent = index + 1;
        }
    });

    fetch("/admin/department/reorder", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ order: orderedIds }),
    })
        .then(function (res) { return res.json(); })
        .then(function (data) {
            if (!data.success) {
                alert("순서 저장에 실패했습니다. 새로고침 후 다시 시도해주세요.");
            }
        })
        .catch(function () {
            alert("순서 저장 중 오류가 발생했습니다. 새로고침 후 다시 시도해주세요.");
        });
}
