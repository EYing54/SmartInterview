<template>
  <div style="display: flex; height: 100vh; padding: 20px">
    <div
      style="
        width: 320px;
        border-right: 1px solid #ebeef5;
        padding-right: 20px;
        overflow-y: auto;
      "
    >
      <h3 style="margin-bottom: 20px">历史记录</h3>

      <el-card
        v-for="item in historyList"
        :key="item.interview_id"
        style="margin-bottom: 15px; cursor: pointer"
        shadow="hover"
        @click="handleCardClick(item.interview_id)"
      >
        <div style="font-weight: bold; font-size: 15px">
          意向岗位：{{ item.post }}
        </div>
        <div style="color: #666; font-size: 13px; margin-top: 8px">
          时间：{{ item.create_time }}
        </div>
        <div style="margin-top: 10px">
          <el-tag
            :type="item.status === 1 ? 'success' : 'warning'"
            size="small"
          >
            {{ item.status === 1 ? "已完成" : "进行中" }}
          </el-tag>
        </div>
      </el-card>
    </div>

    <div style="flex: 1; padding-left: 20px">
      <div v-if="currentDetail">
        <h2>{{ currentDetail.post }} 面试详情</h2>
        <p>AI评语：{{ currentDetail.analysis_text }}</p>
        <p>老师评价：{{ currentDetail.teacher_comment || "暂无评价" }}</p>
      </div>

      <div
        v-else
        style="
          height: 100%;
          display: flex;
          justify-content: center;
          align-items: center;
          color: #909399;
        "
      >
        <h3>👈 请在左侧选择一条历史记录查看雷达图及详情</h3>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { getHistoryList, getInterviewDetail } from "../../api/interview";

const historyList = ref([]);
const currentDetail = ref(null);

const fetchHistory = async () => {
  try {
    const res = await getHistoryList();
    historyList.value = res.data.data;
  } catch (error) {
    console.log(error);
  }
};

// 处理卡片点击的动作
const handleCardClick = async (id) => {
  try {
    const res = await getInterviewDetail(id);
    // 把后端传回来的 detail 字典赋值给右侧的响应式变量
    currentDetail.value = res.data.data;
  } catch (error) {
    console.log("获取详情失败", error);
  }
};

onMounted(() => {
  fetchHistory();
});
</script>

<style scoped>
/* 1. 最外层画布：利用 box-sizing 确保 padding 不会撑大视口 */
.page-canvas {
  display: flex;
  height: 100vh;
  box-sizing: border-box;
  padding: 16px;
  gap: 16px;
  background-color: #f5f7fa;
  overflow: hidden;
}

.left-card-box {
  width: 320px;
  background-color: #fff;
  border-radius: 8px;
  border: 1px solid #e4e7ed;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.box-header {
  padding: 16px 20px;
  border-bottom: 1px solid #f2f6fc;
}

.box-header h3 {
  margin: 0;
  font-size: 16px;
  color: #303133;
}

.box-scroll-list {
  flex: 1;
  overflow-y: auto;
  padding: 4px 0;
}

.right-card-box {
  flex: 1;
  background-color: #fff;
  border-radius: 8px;
  border: 1px solid #e4e7ed;
  display: flex;
  justify-content: center;
  align-items: center;
  overflow: hidden;
}

.placeholder-text {
  color: #909399;
  font-size: 14px;
  font-weight: normal;
}

.history-item {
  padding: 14px 20px;
  border-bottom: 1px solid #f5f7fa;
  cursor: pointer;
  transition: all 0.2s ease;
}

.history-item:hover {
  background-color: #f0f7ff;
}

.item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}

.post-text {
  font-size: 14px;
  font-weight: bold;
  color: #303133;
}

.time-text {
  font-size: 12px;
  color: #909399;
}
</style>
