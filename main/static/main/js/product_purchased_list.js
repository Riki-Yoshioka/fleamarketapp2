function sendRequest() {
    const xhr = new XMLHttpRequest();
    const tabList = document.querySelectorAll(".tab");
    tabList.forEach(function (element, index) {
        element.addEventListener("click", function (ev) {
            const preActiveTab = document.querySelector(".active");
            preActiveTab.classList.remove("active");
            const activeTab = element;
            activeTab.classList.add("active");
            const deliveryStatus = ev.target.dataset.deliveryStatus;
            const queryString = new URLSearchParams({
                delivery_status: deliveryStatus,
            }).toString();
            const requestPath = window.location + "?" + queryString;
            xhr.open("GET", requestPath);
            xhr.responseType = "document";
            xhr.send();
            xhr.onload = function () {
                if (xhr.status == 200) {
                    const res = xhr.response;
                    const productList = document.querySelector(".product-list");
                    const newDom = res.querySelectorAll(".product-item");
                    const oldDom = document.querySelectorAll(".product-item");
                    if (newDom) {
                        oldDom.forEach((element) => {
                            productList.removeChild(element);
                        });
                        newDom.forEach((element) => {
                            productList.appendChild(element);
                        });
                    }
                } else {
                    window.alert("通信に失敗しました。");
                }
            };
        });
    });
}
sendRequest();