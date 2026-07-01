<template>
  <div class="page-container">
    <div class="left-column">
      <div class="column-header">
        <el-button link @click="router.back()" class="back-btn">
          <el-icon><ArrowLeft /></el-icon> 返回
        </el-button>
        <h3>学生历史记录</h3>
      </div>

      <el-scrollbar class="scroll-area">
        <el-card
          v-for="item in historyList"
          :key="item.interview_id"
          class="history-card"
          :class="{
            'is-active': currentDetail?.interview_id === item.interview_id,
          }"
          shadow="hover"
          @click="handleCardClick(item.interview_id)"
        >
          <div class="card-post">意向岗位：{{ item.post }}</div>
          <div class="card-time">时间：{{ item.create_time }}</div>
          <div class="card-status">
            <el-tag
              :type="item.status >= 1 ? 'success' : 'warning'"
              size="small"
            >
              {{ item.status >= 1 ? "已完成" : "进行中" }}
            </el-tag>
          </div>
        </el-card>
      </el-scrollbar>
    </div>

    <div v-if="currentDetail" class="detail-wrapper">
      <div class="middle-column">
        <div class="column-header">
          <h3>{{ currentDetail.post }} - 面试能力画像</h3>
        </div>
        <el-scrollbar class="chart-container">
          <div ref="raderef" style="width: 100%; height: 400px"></div>
        </el-scrollbar>
      </div>

      <div class="right-column">
        <div class="column-header">
          <h3>综合评价</h3>
        </div>

        <el-scrollbar class="evaluation-content">
          <div class="evaluation-inner">
            <div class="ai-section">
              <div class="section-title">
                <el-icon color="#409EFF" style="margin-right: 5px"
                  ><Monitor
                /></el-icon>
                AI 分析报告
              </div>
              <div class="text-box ai-text">
                {{ currentDetail.analysis_text || "AI正在分析中，请稍后..." }}
              </div>
            </div>

            <el-divider border-style="dashed"></el-divider>

            <div class="teacher-section">
              <div class="section-title">
                <el-icon color="#E6A23C" style="margin-right: 5px"
                  ><Avatar
                /></el-icon>
                教师评价
              </div>

              <div v-if="!isEditing">
                <div class="text-box teacher-text">
                  {{
                    currentDetail.teacher_comment ||
                    "暂无评价，请点击下方进行点评。"
                  }}
                </div>
                <div class="edit-actions">
                  <el-button type="primary" size="small" @click="edit">
                    修改
                  </el-button>
                </div>
              </div>

              <div v-else class="edit-box">
                <el-input
                  type="textarea"
                  :rows="5"
                  v-model="commentText"
                  placeholder="请输入详细的指导建议..."
                />
                <div class="edit-actions">
                  <el-button size="small" @click="cancel">取消</el-button>
                  <el-button
                    type="primary"
                    size="small"
                    @click="save(currentDetail.interview_id)"
                  >
                    保存
                  </el-button>
                </div>
              </div>
            </div>
          </div>
        </el-scrollbar>
      </div>
    </div>

    <div v-else class="empty-state">
      <el-empty description="👈 请在左侧选择一条面试记录查看详情" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from "vue";
import {
  getStudentInterviewHistory,
  getStudentInterviewDetail,
  submitComment,
} from "../../api/classes";
import * as echarts from "echarts";
import { useRoute, useRouter } from "vue-router";
import { ArrowLeft, Monitor, Avatar } from "@element-plus/icons-vue";
import { ElMessage } from "element-plus";

const route = useRoute();
const router = useRouter();
const currentStudentId = route.query.id;

const historyList = ref([]);
const currentDetail = ref(null);
const raderef = ref(null);
let myChart = null;

const isEditing = ref(false);
const commentText = ref("");

const fetchHistory = async () => {
  if (!currentStudentId) return;
  try {
    const res = await getStudentInterviewHistory(currentStudentId);
    historyList.value = res.data.data;
  } catch (error) {
    console.log(error);
  }
};

const handleCardClick = async (id) => {
  try {
    isEditing.value = false;
    const res = await getStudentInterviewDetail(id);
    currentDetail.value = res.data.data;
    await nextTick();
    drawRader(currentDetail.value.dimension_grade);
  } catch (error) {
    console.log("获取详情失败", error);
  }
};

const drawRader = (gradeData) => {
  if (myChart != null) {
    myChart.dispose();
  }
  myChart = echarts.init(raderef.value);

  const keys = Object.keys(gradeData);
  const values = Object.values(gradeData);

  const indicatorArray = keys.map((itemName) => ({
    name: itemName,
    max: 100,
  }));

  const option = {
    radar: {
      indicator: indicatorArray,
      shape: "polygon",
      radius: "65%",
    },
    series: [
      {
        type: "radar",
        data: [
          {
            value: values,
            name: "能力评估",
            areaStyle: { color: "rgba(64, 158, 255, 0.2)" },
            lineStyle: { color: "#409EFF" },
            itemStyle: { color: "#409EFF" },
          },
        ],
      },
    ],
  };

  myChart.setOption(option);
};

const edit = () => {
  isEditing.value = true;
  commentText.value = currentDetail.value.teacher_comment || "";
};

const save = async (id) => {
  try {
    await submitComment(id, commentText.value);
    currentDetail.value.teacher_comment = commentText.value;
    isEditing.value = false;
    ElMessage.success("保存成功！");
  } catch (error) {
    ElMessage.error("保存失败，请重试");
  }
};

const cancel = () => {
  isEditing.value = false;
};

onMounted(() => {
  fetchHistory();
});
</script>

<style scoped>
.page-container {
  display: flex;
  height: calc(100vh - 105px);
  box-sizing: border-box;
  gap: 20px;
  overflow: hidden;
}

.left-column,
.middle-column,
.right-column {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.left-column {
  width: 320px;
  flex-shrink: 0;
}

.column-header {
  padding: 16px 20px;
  border-bottom: 1px solid #ebeef5;
  display: flex;
  align-items: center;
}

.column-header h3 {
  margin: 0;
  font-size: 16px;
  color: #303133;
}
.back-btn {
  transform: translateY(2px);
}
.back-btn {
  margin-right: 12px;
  font-size: 15px;
  color: #606266;
}

.scroll-area {
  flex: 1;
  height: 0;
  padding: 15px;
}

.history-card {
  margin-bottom: 15px;
  cursor: pointer;
  border: 1px solid transparent;
  transition: all 0.3s;
}

.history-card:hover {
  border-color: #c6e2ff;
}

.history-card.is-active {
  border-color: #409eff;
  background-color: #f0f7ff;
}

.card-post {
  font-weight: bold;
  font-size: 15px;
  color: #303133;
}

.card-time {
  color: #909399;
  font-size: 13px;
  margin-top: 8px;
}

.card-status {
  margin-top: 10px;
}

.detail-wrapper {
  flex: 1;
  display: flex;
  gap: 20px;
  min-width: 0;
}

.middle-column {
  flex: 1;
}

.chart-container {
  flex: 1;
  height: 0;
}

.right-column {
  width: 380px;
  flex-shrink: 0;
}

.evaluation-content {
  flex: 1;
  height: 0;
}

.evaluation-inner {
  padding: 20px;
}

.section-title {
  font-size: 15px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 12px;
  display: flex;
  align-items: center;
}

.text-box {
  background-color: #f8f9fa;
  border-radius: 6px;
  padding: 15px;
  font-size: 14px;
  line-height: 1.6;
  color: #606266;
  min-height: 80px;
}

.ai-text {
  border-left: 4px solid #409eff;
}

.teacher-text {
  border-left: 4px solid #e6a23c;
}

.edit-box {
  margin-top: 10px;
}

.edit-actions {
  margin-top: 15px;
  text-align: right;
}

.empty-state {
  flex: 1;
  background-color: #fff;
  border-radius: 8px;
  display: flex;
  justify-content: center;
  align-items: center;
}
</style>
