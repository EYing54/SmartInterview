<template>
  <div class="lobby-container">
    <h2 class="lobby-title">欢迎来到模拟面试大厅</h2>

    <el-row :gutter="20" justify="center">
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
      <el-button type="primary" size="large" @click="startInterview"
        >开始面试</el-button
      >
      <div style="margin-top: 15px">
        <el-button text @click="goToHistory" style="color: #909399">
          查看历史记录
        </el-button>
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
      ElMessage.success("面试创建成功，正在进入考场...");
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
  padding: 40px 20px;
}
.lobby-title {
  text-align: center;
  margin-bottom: 50px;
  color: #303133;
}
.step-card {
  height: 220px;
  text-align: center;
  border-radius: 12px;
}
.step-card h3 {
  color: #409eff;
  margin-bottom: 15px;
}
.step-card p {
  color: #606266;
  font-size: 14px;
  line-height: 1.6;
  text-align: left;
}
.start-action {
  margin-top: 60px;
  text-align: center;
}

.start-action .el-button {
  font-size: 20px;
  padding: 20px 60px;
  font-weight: bold;
}
</style>
