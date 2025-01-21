document.getElementById("submitButton").addEventListener("click", function () {
    // 获取输入框中的值
    const keyword = document.getElementById("keywordInput").value.trim();

    if (!keyword) {
        alert("请输入关键词！");
        return;
    }

    // 构造请求数据
    const data = {
        keyword: keyword
    };

    // 发送 POST 请求到后端
    fetch("/qa", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(data)
    })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(result => {
            // 处理返回数据
            const answerElement = document.getElementById("answer");
            const videoElement = document.getElementById("videoPlayer");
            const placeholder = document.getElementById("videoPlaceholder");

            if (result.answer) {
                answerElement.textContent = result.answer; // 显示回答
            } else {
                answerElement.textContent = "未找到回答。";
            }

            if (result.webm_file) {
                // 将十六进制文件转换为 Blob 并创建下载链接
                const fileBlob = new Blob([new Uint8Array(result.webm_file.match(/.{1,2}/g).map(byte => parseInt(byte, 16)))], { type: "video/webm" });
                const fileUrl = URL.createObjectURL(fileBlob);

                videoElement.src = fileUrl; // 显示视频
                videoElement.style.display = "block";

                placeholder.style.display = "none";
            } else {
                videoElement.style.display = "none";
            }
        })
        .catch(error => {
            console.error("Error:", error);
            alert("请求失败，请稍后再试！");
        });
});
