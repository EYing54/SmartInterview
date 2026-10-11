<template>
  <div class="teacher-layout">
    <!-- 顶部导航栏 -->
    <header class="top-bar">
      <!-- 左侧菜单 -->
      <el-menu
        :default-active="$route.path"
        mode="horizontal"
        router
        :ellipsis="false"
        class="nav-bar"
        background-color="#ffffff"
        text-color="#334155"
        active-text-color="#409EFF"
      >
        <el-menu-item index="logo" disabled class="brand-item"
          >智能面试平台</el-menu-item
        >
        <el-menu-item index="/teacher/classes">我的班级</el-menu-item>
        <el-menu-item index="/teacher/question">题目推送</el-menu-item>
      </el-menu>

      <!-- 右侧头像菜单 -->
      <div class="avatar-container">
        <UserAvatarMenu />
      </div>
    </header>

    <!-- 主页面 -->
    <el-main class="main-content">
      <router-view />
    </el-main>
  </div>
</template>

<script setup>
import UserAvatarMenu from "../../components/UserAvatarMenu.vue";
</script>

<style scoped>
/* 教师端整体布局 */
.teacher-layout {
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
  box-sizing: border-box;
  padding-right: 20px;

  background-color: #ffffff;

  /* 连续的底部分隔线 */
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

/* 右侧头像区域 */
.avatar-container {
  display: flex;
  align-items: center;
  justify-content: center;

  flex-shrink: 0;
  margin-left: auto;
  padding-left: 20px;
}

/* 主页面内容 */
.main-content {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}
</style>
