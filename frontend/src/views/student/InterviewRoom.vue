<template>
  <div class="interview-room-v4">
    <div class="header-v4">
      <div class="timer-badge-v4" :class="{ 'danger-pulse': timeLeft <= 30 }">
        回答倒计时: {{ formattedTime }}
      </div>
    </div>

    <div class="stage-container-v4">
      <div class="left-stage-v4">
        <div class="question-display-v4">
          <div class="question-header-v4">
            <span class="progress-text-v4">
              {{ currentIndex + 1 }} /
              {{ allQuestions.length || 10 }} 已回答/未回答
            </span>
          </div>
          <div class="question-content-v4">
            <span class="question-text-v4">{{ currentQuestion }}</span>
          </div>
        </div>
      </div>

      <div class="right-stage-v4">
        <div class="video-ratio-container-v4">
          <video
            ref="videoElement"
            autoplay
            muted
            playsinline
            class="camera-video-v4"
          ></video>

          <div class="audio-strip-vertical-v4">
            <div
              class="audio-level-fill"
              :style="{ height: audioLevel + '%' }"
            ></div>
          </div>
        </div>

        <div class="action-block-v4">
          <el-button
            v-if="currentIndex < allQuestions.length - 1"
            type="warning"
            size="large"
            class="end-btn-v4"
            :loading="isUploading"
            @click="handleNextClick"
          >
            结束回答
          </el-button>

          <el-button
            v-else
            type="danger"
            size="large"
            class="end-btn-v4"
            :loading="isUploading"
            @click="handleNextClick"
          >
            结束面试
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from "vue";
import { onBeforeRouteLeave, useRouter } from "vue-router";
import { ElMessage, ElMessageBox } from "element-plus";
import {
  finishInterview,
  abortInterview,
  uploadAnswer,
} from "../../api/interview";

const router = useRouter();

const interviewId = ref(null);
const allQuestions = ref([]);
const currentQuestion = ref("");
const currentIndex = ref(0);

const isSubmitting = ref(false);
const isUploading = ref(false);

let videoRecorder = null;
let audioRecorder = null;
let videoChunks = [];
let audioChunks = [];
let videoBlob = null;
let audioBlob = null;

const audioLevel = ref(5);
let audioContext = null;
let analyser = null;
let animationId = null;

const timeLeft = ref(180);
let timer = null;

const formattedTime = computed(() => {
  const m = Math.floor(timeLeft.value / 60)
    .toString()
    .padStart(2, "0");
  const s = (timeLeft.value % 60).toString().padStart(2, "0");
  return `${m}:${s}`;
});

const preventRefresh = (e) => {
  if (!isSubmitting.value) {
    e.preventDefault();
    e.returnValue = "";
  }
};

onBeforeRouteLeave(async (to, from, next) => {
  if (isSubmitting.value) {
    next();
    return;
  }

  try {
    await ElMessageBox.confirm(
      "正在面试中，中途退出将导致考卷作废，确认要强行离开吗？",
      "警告",
      {
        confirmButtonText: "强行离开",
        cancelButtonText: "继续面试",
        type: "warning",
      },
    );

    try {
      await abortInterview(interviewId.value);
    } catch (apiError) {}

    if (timer) clearInterval(timer);
    sessionStorage.removeItem("current_interview");
    sessionStorage.removeItem("interview_current_index");
    sessionStorage.removeItem("interview_time_left");
    next();
  } catch (error) {
    next(false);
  }
});

const startTimer = (isResume = false) => {
  if (timer) clearInterval(timer);

  if (!isResume) {
    timeLeft.value = 180;
    sessionStorage.setItem("interview_time_left", 180);
  }

  timer = setInterval(() => {
    if (timeLeft.value > 0) {
      timeLeft.value--;
      sessionStorage.setItem("interview_time_left", timeLeft.value);
    } else {
      clearInterval(timer);
      const isLast = currentIndex.value >= allQuestions.value.length - 1;
      if (isLast) {
        ElMessage.warning("时间到！已自动为您交卷");
      } else {
        ElMessage.warning("时间到！已自动为您切换至下一题");
      }
      triggerUploadAndNext();
    }
  }, 1000);
};

const videoElement = ref(null);
let currentStream = null;

const startAudioVisualizer = (stream) => {
  audioContext = new (window.AudioContext || window.webkitAudioContext)();
  analyser = audioContext.createAnalyser();
  const source = audioContext.createMediaStreamSource(stream);
  source.connect(analyser);

  analyser.fftSize = 256;
  const bufferLength = analyser.frequencyBinCount;
  const dataArray = new Uint8Array(bufferLength);

  const updateVolume = () => {
    analyser.getByteFrequencyData(dataArray);
    let sum = 0;
    for (let i = 0; i < bufferLength; i++) {
      sum += dataArray[i];
    }
    const average = sum / bufferLength;
    audioLevel.value = Math.max(5, Math.min(100, (average / 128) * 100));
    animationId = requestAnimationFrame(updateVolume);
  };

  updateVolume();
};

const checkAndUpload = async () => {
  if (videoBlob && audioBlob) {
    const formData = new FormData();
    const currentQ = allQuestions.value[currentIndex.value];

    formData.append("interview_id", interviewId.value);
    formData.append("question_id", currentQ.question_id);
    formData.append("video", videoBlob, "answer_video.webm");
    formData.append("audio", audioBlob, "answer_audio.webm");

    try {
      await uploadAnswer(formData);
    } catch (error) {
      ElMessage.error("音视频上传失败，请检查网络！");
    } finally {
      isUploading.value = false;
      videoBlob = null;
      audioBlob = null;
      proceedToNext();
    }
  }
};

const setupMediaRecorder = (stream) => {
  const audioStream = new MediaStream(stream.getAudioTracks());

  videoRecorder = new MediaRecorder(stream, {
    mimeType: "video/webm;codecs=vp8,opus",
  });
  audioRecorder = new MediaRecorder(audioStream, {
    mimeType: "audio/webm;codecs=opus",
  });

  videoRecorder.ondataavailable = (e) => {
    if (e.data.size > 0) videoChunks.push(e.data);
  };
  audioRecorder.ondataavailable = (e) => {
    if (e.data.size > 0) audioChunks.push(e.data);
  };

  videoRecorder.onstop = () => {
    videoBlob = new Blob(videoChunks, { type: "video/webm" });
    videoChunks = [];
    checkAndUpload();
  };

  audioRecorder.onstop = () => {
    audioBlob = new Blob(audioChunks, { type: "audio/webm" });
    audioChunks = [];
    checkAndUpload();
  };
};

const startCamera = async () => {
  try {
    currentStream = await navigator.mediaDevices.getUserMedia({
      video: true,
      audio: true,
    });
    if (videoElement.value) {
      videoElement.value.srcObject = currentStream;
    }
    startAudioVisualizer(currentStream);
    setupMediaRecorder(currentStream);
    videoRecorder.start();
    audioRecorder.start();
  } catch (error) {
    ElMessage.error("无法访问摄像头或麦克风！");
  }
};

const handleNextClick = async () => {
  const isLastQuestion = currentIndex.value >= allQuestions.value.length - 1;

  if (isLastQuestion) {
    try {
      await ElMessageBox.confirm(
        "这是最后一道题，确认要结束本次面试并交卷吗？",
        "交卷确认",
        {
          confirmButtonText: "确认交卷",
          cancelButtonText: "继续作答",
          type: "warning",
        },
      );
      triggerUploadAndNext();
    } catch (error) {}
  } else {
    triggerUploadAndNext();
  }
};

const triggerUploadAndNext = () => {
  if (timer) clearInterval(timer);
  isUploading.value = true;

  if (videoRecorder && videoRecorder.state === "recording") {
    videoRecorder.stop();
    audioRecorder.stop();
  } else {
    proceedToNext();
  }
};

const proceedToNext = async () => {
  if (currentIndex.value < allQuestions.value.length - 1) {
    currentIndex.value++;
    sessionStorage.setItem("interview_current_index", currentIndex.value);
    currentQuestion.value = allQuestions.value[currentIndex.value].question;
    startTimer();
    if (videoRecorder) videoRecorder.start();
    if (audioRecorder) audioRecorder.start();
  } else {
    if (timer) clearInterval(timer);
    ElMessage.success("答题完毕！正在处理交卷逻辑...");

    try {
      await finishInterview(interviewId.value);
    } catch (error) {}

    sessionStorage.removeItem("current_interview");
    sessionStorage.removeItem("interview_current_index");
    sessionStorage.removeItem("interview_time_left");
    isSubmitting.value = true;
    router.replace("/student/history");
  }
};

onMounted(() => {
  window.addEventListener("beforeunload", preventRefresh);
  const interviewDataStr = sessionStorage.getItem("current_interview");

  if (interviewDataStr) {
    const interviewData = JSON.parse(interviewDataStr);
    interviewId.value = interviewData.interview_id;
    allQuestions.value = interviewData.questions;

    const savedIndex = sessionStorage.getItem("interview_current_index");
    currentIndex.value = savedIndex ? parseInt(savedIndex, 10) : 0;

    const savedTime = sessionStorage.getItem("interview_time_left");

    if (allQuestions.value && allQuestions.value.length > 0) {
      currentQuestion.value = allQuestions.value[currentIndex.value].question;
    } else {
      currentQuestion.value = "未分配到题目";
    }

    startCamera();

    if (savedTime !== null) {
      timeLeft.value = parseInt(savedTime, 10);
      startTimer(true);
    } else {
      startTimer();
    }
  } else {
    currentQuestion.value = "请退回大厅，点击“开始面试”进入";
  }
});

onUnmounted(() => {
  window.removeEventListener("beforeunload", preventRefresh);
  if (currentStream) {
    currentStream.getTracks().forEach((track) => track.stop());
  }
  if (timer) {
    clearInterval(timer);
  }
  if (animationId) cancelAnimationFrame(animationId);
  if (audioContext && audioContext.state !== "closed") {
    audioContext.close();
  }
});
</script>

<style scoped>
.interview-room-v4 {
  max-width: 1200px;
  margin: 0 auto;
  height: 100vh;
  display: flex;
  flex-direction: column;
  gap: 15px;
  padding: 15px;
  box-sizing: border-box;
  overflow: hidden;
  background-color: #f5f7fa;
}

.header-v4 {
  display: flex;
  justify-content: center;
}
.timer-badge-v4 {
  background-color: #fff;
  border: 1px solid #dcdfe6;
  border-radius: 20px;
  padding: 8px 20px;
  font-weight: bold;
  color: #303133;
  transition: all 0.3s ease;
}

.danger-pulse {
  color: #f56c6c;
  border-color: #f56c6c;
  box-shadow: 0 0 10px rgba(245, 108, 108, 0.4);
  animation: pulse-bg 1.5s infinite alternate;
}

@keyframes pulse-bg {
  0% {
    background-color: #fff;
  }
  100% {
    background-color: #fef0f0;
  }
}

.stage-container-v4 {
  display: flex;
  gap: 20px;
  flex: 1;
  min-height: 0;
}

.left-stage-v4 {
  flex: 1.5;
  display: flex;
  min-height: 0;
}

.question-display-v4 {
  background-color: #fff;
  border: 1px solid #dcdfe6;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  flex: 1;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.question-header-v4 {
  padding: 15px 20px 5px;
  display: flex;
  justify-content: flex-end;
}
.progress-text-v4 {
  font-size: 14px;
  color: #909399;
}

.question-content-v4 {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 0 40px 40px;
  overflow-y: auto;
}
.question-text-v4 {
  font-size: 24px;
  color: #303133;
  line-height: 1.6;
}

.right-stage-v4 {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 20px;
  min-height: 0;
}

.video-ratio-container-v4 {
  position: relative;
  width: 100%;
  aspect-ratio: 16 / 9;
  background-color: #000;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.camera-video-v4 {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transform: scaleX(-1);
}

.audio-strip-vertical-v4 {
  position: absolute;
  right: 15px;
  bottom: 15px;
  width: 24px;
  height: 60%;
  background-color: rgba(255, 255, 255, 0.85);
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  align-items: center;
  backdrop-filter: blur(4px);
  padding: 2px;
  overflow: hidden;
}

.audio-level-fill {
  width: 100%;
  min-height: 20px;
  background-color: #67c23a;
  border-radius: 10px;
  transition: height 0.05s linear;
}

.action-block-v4 {
  display: flex;
  flex-direction: column;
}
.end-btn-v4 {
  width: 100%;
  border-radius: 8px;
  font-weight: bold;
}
</style>
