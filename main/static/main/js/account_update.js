"use strict";

// 画像プレビュー機能の実装
function previewImage(obj) {
    const fileReader = new FileReader();
    fileReader.onload = (function () {
        document.getElementById('preview').src = fileReader.result;
    });
    fileReader.readAsDataURL(obj.files[0]);
}

// 文字数カウント機能
// ユーザー名の文字数をカウント
function showUsernameLength(str) {
    document.getElementById("edit-username-count").textContent = str.length;
}

// プロフィール文の文字数をカウント
function showProfileLength(str) {
    document.getElementById("edit-profile-count").textContent = str.length;
}
