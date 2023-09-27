function previewImage(input, previewId) {
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        const imageId = document.getElementById(previewId)
        reader.readAsDataURL(input.files[0]);
        reader.onload = function () {
            imageId.src = reader.result;
            imageId.style.display = "block";
        };
    }
}

function initializeIconStatus() {
    const icons = document.querySelectorAll(".image-icon");
    for (let i = 0; i < icons.length; i++) {
        if (i != 0) {
            icons[i].classList.add("inactive");
        }
    }
}

function changeIconStatus(inputs, i) {
    const icons = document.querySelectorAll(".image-icon");
    if (i != inputs.length - 1) {
        icons[i + 1].classList.remove("inactive");
    }
}

function previewImageManage() {
    const inputs = document.querySelectorAll('input[type="file"]');
    for (let i = 0; i < inputs.length; i++) {
        inputs[i].addEventListener("change", function() {
            const input = this;
            const previewId = "preview-" + i;
            previewImage(input, previewId);
            changeIconStatus(inputs, i);
        });
    }
}

// 商品名の文字数をカウント
function showNameLength(str) {
    document.getElementById("name-form-count").textContent = str.length;
}

// 商品の説明の文字数をカウント
function showExplanationLength(str) {
    document.getElementById("explanation-form-count").textContent = str.length;
}

// 手数料を表示する
function showCommission() {
    const value = document.getElementById("id_value");
    // console.log(value);
    value.addEventListener("change", function() {
        document.getElementById("product-commission").textContent = Math.floor(value.value * 0.1);
    });
}

// ポイントを表示する
function showPoint() {
    const value = document.getElementById("id_value");
    value.addEventListener("change", function() {
        document.getElementById("product-point").textContent = value.value - Math.floor(value.value * 0.1);
    });
}

initializeIconStatus();
previewImageManage();
showCommission();
showPoint();
