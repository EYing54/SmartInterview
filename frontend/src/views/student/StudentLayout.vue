<template>
  <div class="student-layout">
    <el-menu
      :default-active="$route.path"
      mode="horizontal"
      router
      class="nav-bar"
    >
      <el-menu-item
        index="logo"
        disabled
        style="opacity: 1; font-weight: bold; color: #409eff; cursor: default"
      >
        智能面试系统
      </el-menu-item>

      <el-menu-item index="/student/lobby">模拟面试</el-menu-item>
      <el-menu-item index="/student/resume">简历分析</el-menu-item>

      <div style="flex-grow: 1"></div>

      <el-menu-item index="logout" @click="handleLogout">
        <el-button type="danger" plain size="small">退出登录</el-button>
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
  localStorage.removeItem("role");
  router.push("/login");
};
</script>

<style scoped>
.student-layout {
  min-height: 100vh;
  background-color: #f5f7fa;
}
.nav-bar {
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}
.main-content {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}
</style>
