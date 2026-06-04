<template>
  <div class="interview-room">
    <div class="room-header">
      <span class="timer">Remaining Time: 03:00</span>
      <span class="progress">1/10</span>
    </div>

    <div class="interview-stage">
      <div class="camera-block">
        <span class="placeholder-text">Camera view / placeholder</span>
      </div>

      <div class="question-block">
        <span class="question-text">{{ currentQuestion }}</span>
      </div>
    </div>

    <div class="audio-strip">
      <span class="placeholder-text">Audio bar / placeholder</span>
    </div>

    <div class="action-footer">
      <el-button type="warning" size="large" class="end-answer-btn">
        结束回答
      </el-button>
      <el-button type="danger" size="large" class="end-interview-btn">
        结束面试
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";

const currentQuestion = ref("题目加载中...");
const interviewId = ref(null);
const allQuestions = ref([]);

onMounted(() => {
  const interviewDataStr = sessionStorage.getItem("current_interview");

  if (interviewDataStr) {
    const interviewData = JSON.parse(interviewDataStr);
    interviewId.value = interviewData.interview_id;
    allQuestions.value = interviewData.questions;
    if (allQuestions.value && allQuestions.value.length > 0) {
      currentQuestion.value = allQuestions.value[0].question;
    } else {
      currentQuestion.value = "未分配到题目";
    }
  } else {
    currentQuestion.value = "请退回大厅，点击“开始面试”进入";
  }
});
</script>

<style scoped>
.interview-room {
  max-width: 1100px;
  margin: 0 auto;
  padding: 20px;
  height: calc(100vh - 100px);
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.room-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  font-weight: bold;
  font-size: 18px;
}

.timer {
  color: #ff9900;
}

.progress {
  color: #409eff;
}

.interview-stage {
  display: flex;
  gap: 20px;
  flex: 1;
}

.camera-block,
.question-block {
  flex: 1;
  background-color: #fff;
  border: 1px solid #dcdfe6;
  border-radius: 8px;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
}

.question-text {
  font-size: 22px;
  color: #303133;
  line-height: 1.5;
  text-align: center;
}

.audio-strip {
  height: 80px;
  background-color: #fff;
  border: 1px solid #dcdfe6;
  border-radius: 8px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.placeholder-text {
  color: #909399;
  font-size: 20px;
  font-style: italic;
}

.action-footer {
  display: flex;
  justify-content: space-between;
  margin-top: 10px;
}

.end-answer-btn {
  background-color: #ff9900;
  border-color: #ff9900;
  color: white;
}

.end-interview-btn {
  background-color: #f56c6c;
  border-color: #f56c6c;
  color: white;
}
</style>
