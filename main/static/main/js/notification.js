function sendRequest(){
    const xhr = new XMLHttpRequest();
    const tabList = document.querySelectorAll(".tab");
    tabList.forEach(function (element, index){
        element.addEventListener("click", function(ev){
            const preActiveTab = document.querySelector(".active");
            preActiveTab.classList.remove("active");
            const activeTab = element;
            activeTab.classList.add("active");
            const isAction = ev.target.dataset.isAction;
            const queryString = new URLSearchParams({"isAction":isAction}).toString();
            const requestPath = window.location + "?" + queryString;
            xhr.open("GET", requestPath);
            xhr.responseType = "document";
            xhr.send();
            xhr.onload = function() {
                if(xhr.status == 200) {
                    const res = xhr.response;
                    const productList = document.querySelector(".notification-list")
                    const newDom = res.querySelectorAll(".notification-item")
                    const oldDom = document.querySelectorAll(".notification-item")
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
            }
        });
    });
}
sendRequest();