<template>
  <div class="student-layout">
    <header class="top-bar">
      <!-- 左侧导航 -->
      <el-menu
        :default-active="$route.path"
        mode="horizontal"
        router
        :ellipsis="false"
        class="nav-bar"
      >
        <el-menu-item index="logo" disabled class="brand-item"
          >智能面试平台</el-menu-item
        >
        <el-menu-item index="/student/lobby">模拟面试</el-menu-item>
        <el-menu-item index="/student/resume">简历分析</el-menu-item>
      </el-menu>

      <!-- 右侧用户入口 -->
      <div class="avatar-container">
        <UserAvatarMenu />
      </div>
    </header>

    <el-main class="main-content">
      <router-view />
    </el-main>
  </div>
</template>

<script setup>
import UserAvatarMenu from "../../components/UserAvatarMenu.vue";
</script>

<style scoped>
.student-layout {
  min-height: 100vh;
  background-color: #f5f7fa;
}

/* 导航栏 */
.top-bar {
  position: sticky;
  top: 0;
  z-index: 100;

  display: flex;
  align-items: center;
  justify-content: space-between;

  width: 100%;
  height: 60px;
  padding: 0 20px 0 0;
  box-sizing: border-box;

  background-color: #ffffff;

  /* 导航栏分隔线 */
  box-shadow:
    0 1px 0 #e4e7ed,
    0 3px 8px rgba(0, 0, 0, 0.03);
}

/* 左侧导航菜单 */
.nav-bar {
  flex: 0 1 auto;
  min-width: 0;

  height: 100%;
  border: 0 !important;
  background-color: transparent;

  --el-menu-horizontal-height: 60px;
}

/* 平台名称 */
.brand-item {
  opacity: 1 !important;
  font-weight: bold;
  color: #409eff !important;
  cursor: default !important;
}

/* 右侧头像 */
.avatar-container {
  display: flex;
  align-items: center;
  justify-content: center;

  flex-shrink: 0;
  margin-left: auto;
  padding-left: 20px;
}

/* 主页面 */
.main-content {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}
</style>
