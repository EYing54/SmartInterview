<template>
  <div class="lobby-container">
    <h2 class="lobby-title">欢迎来到模拟面试大厅</h2>

    <el-row :gutter="20" justify="center" class="cards-row">
      <el-col :span="7">
        <el-card shadow="hover" class="step-card">
          <h3>第 1 步：开始面试！</h3>
          <p>
            点击开始来进行一次模拟面试，记得同意我们的权限请求，我们可不想看到您获得0分。
          </p>
        </el-card>
      </el-col>

      <el-col :span="7">
        <el-card shadow="hover" class="step-card">
          <h3>第 2 步：回答问题</h3>
          <p>
            您将通过语音回答来完成我们为您准备的题目，认真回答，努力思考，竭尽所能取得高分吧！
          </p>
        </el-card>
      </el-col>

      <el-col :span="7">
        <el-card shadow="hover" class="step-card">
          <h3>第 3 步：查看结果</h3>
          <p>
            稍等片刻，我们正在分析您的结果。我们将在结束后的片刻为您显示本次面试的相关结果，帮助您了解自己的水平。
          </p>
        </el-card>
      </el-col>
    </el-row>

    <div class="start-action">
      <el-button type="primary" size="large" @click="startInterview">
        开始面试
      </el-button>
      <div class="history-action">
        <el-button text @click="goToHistory"> 查看历史记录 </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { createInterview } from "../../api/interview";

const router = useRouter();

const startInterview = async () => {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({
      video: true,
      audio: true,
    });
    stream.getTracks().forEach((track) => track.stop());
  } catch (error) {
    console.error("授权失败:", error);
    ElMessage.error({
      message:
        "未授权！请点击浏览器地址栏最左侧的“摄像头”图标允许权限，然后刷新页面重试。",
      duration: 5000,
    });
    return;
  }
  try {
    const res = await createInterview();
    if (res.data.code === 201) {
      ElMessage.success("面试创建成功！");
      sessionStorage.setItem(
        "current_interview",
        JSON.stringify(res.data.data),
      );
      router.push("/student/interview_room");
    } else {
      ElMessage.error(res.data.msg);
    }
  } catch (error) {
    console.log("创建面试失败：", error);
    ElMessage.error("网络异常，请稍后再试");
  }
};

const goToHistory = () => {
  router.push("/student/history");
};
</script>

<style scoped>
.lobby-container {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: calc(100vh - 105px);
  box-sizing: border-box;
  overflow: hidden;
  background-color: #f0f2f5;
  border-radius: 8px;
}

.lobby-title {
  font-size: 28px;
  color: #303133;
  margin-bottom: 40px;
  letter-spacing: 1px;
}

.cards-row {
  width: 100%;
  max-width: 1100px;
}

.step-card {
  height: 200px;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
}

.step-card h3 {
  color: #409eff;
  margin-top: 0;
  margin-bottom: 15px;
  text-align: center;
}

.step-card p {
  color: #606266;
  font-size: 14px;
  line-height: 1.6;
  margin: 0;
  text-align: justify;
}

.start-action {
  margin-top: 50px;
  text-align: center;
}

.start-action .el-button--primary {
  font-size: 20px;
  padding: 24px 60px;
  border-radius: 8px;
  font-weight: bold;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
  transition: all 0.3s;
}

.start-action .el-button--primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(64, 158, 255, 0.4);
}

.history-action {
  margin-top: 20px;
}

.history-action .el-button {
  color: #909399;
  font-size: 14px;
}

.history-action .el-button:hover {
  color: #409eff;
}
</style>
