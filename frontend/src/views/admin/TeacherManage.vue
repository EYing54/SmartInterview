<template>
  <div style="padding: 20px; max-width: 1200px; margin: 0 auto">
    <div
      style="
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 25px;
      "
    >
      <div style="border-left: 5px solid #409eff; padding-left: 15px">
        <h2 style="margin: 0; font-size: 22px">教师表</h2>
      </div>

      <div style="display: flex; gap: 12px; align-items: center">
        <div style="position: relative; width: 250px">
          <el-input
            v-model="searchQuery"
            :prefix-icon="Search"
            @focus="isFocused = true"
            @blur="isFocused = false"
          />
          <div
            v-show="!searchQuery && !isFocused"
            style="
              position: absolute;
              left: 32px;
              top: 50%;
              transform: translateY(-50%);
              display: flex;
              align-items: center;
              color: #a8abb2;
              font-size: 14px;
              pointer-events: none;
            "
          >
            输入
            <span
              style="
                border: 1px solid #dcdfe6;
                border-radius: 4px;
                padding: 1px 5px;
                margin: 0 4px;
                font-size: 12px;
                background-color: #f4f4f5;
              "
              >/</span
            >
            以查询
          </div>
        </div>

        <el-button plain type="primary" :icon="Plus" style="margin-left: 0"
          >新增数据</el-button
        >
        <el-button
          plain
          type="warning"
          :icon="Refresh"
          style="margin-left: 0"
          @click="handleReset"
          >重置密码</el-button
        >
        <el-button
          plain
          type="danger"
          :icon="Delete"
          style="margin-left: 0"
          @click="handleDelete"
          >删除账号</el-button
        >
      </div>
    </div>

    <el-table
      :data="teacherList"
      style="width: 100%"
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

    <div style="display: flex; justify-content: center; margin-top: 20px">
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

const teacherList = ref([]);
const total = ref(0);
const currentPage = ref(1);
const pageSize = ref(20);

const searchQuery = ref("");
const selectedTeachers = ref([]);
const isFocused = ref(false);

const getTeachers = async () => {
  const res = await getTeacherList(currentPage.value, pageSize.value);
  teacherList.value = res.data.data.list;
  total.value = res.data.data.total;
  console.log("获取到的教师账号为：", teacherList.value);
};

const handleSelectionChange = (val) => {
  selectedTeachers.value = val;
  console.log(selectedTeachers);
};

const handlePageChange = (val) => {
  currentPage.value = val;
  getTeachers();
};

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
      console.log("用户取消了操作");
    } else {
      ElMessage.error("系统异常，删除失败！");
      console.error(error);
    }
  }
};

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
      console.log("用户取消了操作");
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
