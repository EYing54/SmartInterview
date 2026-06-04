<template>
  <div class="admin-layout">
    <el-menu
      :default-active="$route.path"
      class="el-menu-demo"
      mode="horizontal"
      router
      background-color="#304156"
      text-color="#fff"
      active-text-color="#409EFF"
    >
      <el-menu-item
        index="logo"
        disabled
        style="
          opacity: 1;
          cursor: default;
          font-size: 18px;
          font-weight: bold;
          color: white;
        "
      >
        智能面试系统
      </el-menu-item>

      <el-menu-item index="/admin/student">学生端管理</el-menu-item>
      <el-menu-item index="/admin/teacher">教师端管理</el-menu-item>
      <el-menu-item index="/admin/question">题库管理</el-menu-item>

      <div style="flex-grow: 1"></div>

      <el-menu-item index="logout" @click="handleLogout">
        <el-button type="danger" size="small">退出登录</el-button>
      </el-menu-item>
    </el-menu>

    <el-main class="main-content">
      <router-view></router-view>
    </el-main>
  </div>
</template>

<script setup>
import { useRouter } from "vue-router";

const router = useRouter();

const handleLogout = () => {
  localStorage.removeItem("token");
  router.push("/login");
};
</script>

<style scoped>
.admin-layout {
  min-height: 100vh;
  background-color: #f5f7fa; /* 稍微给一点浅灰背景，让里面的白色表格更显眼 */
}
.main-content {
  padding: 20px;
}
</style>
