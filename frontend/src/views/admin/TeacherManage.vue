<template>
  <div class="manage-page">
    <div class="manage-header">
      <div class="manage-title">
        <h2>教师表</h2>
      </div>

      <div class="manage-toolbar">
        <div class="search-box">
          <el-input
            v-model="searchQuery"
            :prefix-icon="Search"
            @focus="isFocused = true"
            @blur="isFocused = false"
          />
          <div v-show="!searchQuery && !isFocused" class="search-placeholder">
            输入
            <span class="search-shortcut">/</span>
            以查询
          </div>
        </div>

        <el-button plain type="primary" :icon="Plus"> 新增数据 </el-button>
        <el-button plain type="warning" :icon="Refresh" @click="handleReset">
          重置密码
        </el-button>
        <el-button plain type="danger" :icon="Delete" @click="handleDelete">
          删除账号
        </el-button>
      </div>
    </div>

    <el-table
      :data="teacherList"
      class="manage-table"
      border
      stripe
      @selection-change="handleSelectionChange"
    >
      <el-table-column type="index" label="序号" width="80" align="center" />
      <el-table-column prop="user_id" label="用户ID" align="center" />
      <el-table-column prop="real_name" label="姓名" align="center" />
      <el-table-column prop="nickname" label="昵称" align="center" />
      <el-table-column prop="username" label="工号" align="center" />
      <el-table-column type="selection" width="60" align="center" />
    </el-table>

    <div class="pagination-container">
      <el-pagination
        v-model:current-page="currentPage"
        :page-size="pageSize"
        layout="prev, pager, next"
        :total="total"
        @current-change="handlePageChange"
      />
    </div>
  </div>
</template>

<script setup>
import {
  getTeacherList,
  deleteAccount,
  resetAccount,
} from "../../api/teacher_manage";
import { ref, onMounted } from "vue";
import { Delete, Plus, Refresh, Search } from "@element-plus/icons-vue";
import { ElMessage, ElMessageBox } from "element-plus";

const searchQuery = ref("");
const isFocused = ref(false);

// 获取教师列表
const teacherList = ref([]);
const total = ref(0);
const currentPage = ref(1);
const pageSize = ref(20);
const getTeachers = async () => {
  const res = await getTeacherList(currentPage.value, pageSize.value);
  teacherList.value = res.data.data.list;
  total.value = res.data.data.total;
  console.log("获取到的教师账号为：", teacherList.value);
};

//分页功能
const handlePageChange = (val) => {
  currentPage.value = val;
  getTeachers();
};

//关联每一行的选择框
const selectedTeachers = ref([]);
const handleSelectionChange = (val) => {
  selectedTeachers.value = val;
  console.log(selectedTeachers);
};

//删除选择的账号
const handleDelete = async () => {
  const selectedUsersId = selectedTeachers.value.map((item) => item.user_id);
  if (selectedUsersId.length == 0) {
    ElMessage.warning("请选择要删除的教师账号！");
    return;
  }
  try {
    await ElMessageBox.confirm("确认要删除选中的账号吗？", "警告", {
      type: "warning",
      confirmButtonText: "确定",
      cancelButtonText: "取消",
    });
    const res = await deleteAccount(selectedUsersId);
    if (res.data.code == 200) {
      ElMessage.success(res.data.msg);
    }
    getTeachers();
  } catch (error) {
    if (error === "cancel" || error === "close") {
      console.log("用户取消了操作！");
    } else {
      ElMessage.error("系统异常，删除失败！");
      console.error(error);
    }
  }
};

//重置选择的账号
const handleReset = async () => {
  const selectedUsersId = selectedTeachers.value.map((item) => item.user_id);
  if (selectedUsersId.length == 0) {
    ElMessage.warning("请选择要重置的教师账号！");
    return;
  }
  try {
    await ElMessageBox.confirm("确认要重置选中的账号吗？", "警告", {
      type: "warning",
      confirmButtonText: "确定",
      cancelButtonText: "取消",
    });
    const res = await resetAccount(selectedUsersId);
    if (res.data.code == 200) {
      ElMessage.success(res.data.msg);
    }
    getTeachers();
  } catch (error) {
    if (error === "cancel" || error === "close") {
      console.log("用户取消了操作！");
    } else {
      ElMessage.error("系统异常，重置失败！");
      console.error(error);
    }
  }
};

onMounted(() => {
  getTeachers();
});
</script>

<style scoped>
.manage-page {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

/* 页面顶部 */
.manage-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 25px;
}

.manage-title {
  border-left: 5px solid #409eff;
  padding-left: 15px;
}

.manage-title h2 {
  margin: 0;
  font-size: 22px;
}

/* 操作工具栏 */
.manage-toolbar {
  display: flex;
  gap: 12px;
  align-items: center;
}

.manage-toolbar :deep(.el-button) {
  margin-left: 0;
}

/* 搜索框 */
.search-box {
  position: relative;
  width: 250px;
}

.search-placeholder {
  position: absolute;
  left: 32px;
  top: 50%;
  transform: translateY(-50%);
  display: flex;
  align-items: center;
  color: #a8abb2;
  font-size: 14px;
  pointer-events: none;
}

.search-shortcut {
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  padding: 1px 5px;
  margin: 0 4px;
  font-size: 12px;
  background-color: #f4f4f5;
}

/* 数据表格 */
.manage-table {
  width: 100%;
}

/* 分页 */
.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}
</style>
