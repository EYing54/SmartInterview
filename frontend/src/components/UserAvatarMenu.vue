<template>
  <el-dropdown
    class="user-dropdown"
    popper-class="avatar-dropdown"
    :show-arrow="false"
    trigger="hover"
    placement="bottom-end"
  >
    <div class="user-trigger">
      <div class="avatar-circle">
        <img v-if="avatarURL" :src="avatarURL" />
        <span v-else>{{ displayName.charAt(0).toUpperCase() }}</span>
      </div>

      <span class="username">{{ displayName }}</span>
    </div>

    <template #dropdown>
      <el-dropdown-menu>
        <el-dropdown-item @click="goToProfile">
          <el-icon><User /></el-icon>
          <span>个人中心</span>
        </el-dropdown-item>

        <el-dropdown-item @click="handleLogout">
          <el-icon><SwitchButton /></el-icon>
          <span>退出登录</span>
        </el-dropdown-item>
      </el-dropdown-menu>
    </template>
  </el-dropdown>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { User, SwitchButton } from "@element-plus/icons-vue";
import { getUserProfile, getUserAvatar } from "../api/user";
import { avatarVersion } from "../stores/avatar";

//获取当前的路由
const currentRoute = useRoute();
const router = useRouter();
//获取当前的客户端种类
const goToProfile = () => {
  const role = currentRoute.path.split("/")[1];
  router.push(`/${role}/profile`);
};

const avatarURL = ref("");
const loadAvatar = async () => {
  const res = await getUserAvatar(); //获取用户头像
  if (avatarURL.value) {
    URL.revokeObjectURL(avatarURL.value);
  }
  avatarURL.value = URL.createObjectURL(res.data);
};

const displayName = ref("我的账户");
//获取当前用户的信息
const loadUserInfo = async () => {
  try {
    const res = await getUserProfile();
    const user = res.data.data;
    if (user) {
      displayName.value = user.nickname || user.username || "我的账户";
    }
    if (user.avatar_path) {
      await loadAvatar();
    }
  } catch (error) {
    console.error("获取用户信息失败：", error);
  }
};

watch(avatarVersion, () => {
  //watch()用来监听响应式变量的更新
  loadAvatar(); //若变量更新则重新加载头像
});

//退出登录
const handleLogout = () => {
  localStorage.removeItem("token");
  localStorage.removeItem("role");
  router.push("/login");
};

onMounted(loadUserInfo);
onUnmounted(() => {
  if (avatarURL.value) {
    URL.revokeObjectURL(avatarURL.value);
  }
});
</script>

<style>
.user-dropdown.el-tooltip__trigger:focus,
.user-dropdown.el-tooltip__trigger:focus-visible {
  outline: none !important;
}

/* 下拉菜单 */
.user-dropdown .user-trigger {
  display: flex;
  align-items: center;
  gap: 10px;

  height: 42px;
  max-width: 210px;
  box-sizing: border-box;
  padding: 5px 16px 5px 5px;

  background-color: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 999px;
  color: #334155;

  cursor: pointer;
  outline: none;

  transition:
    background-color 0.25s ease,
    box-shadow 0.25s ease;
}

/* 边框颜色 */
.user-dropdown:hover .user-trigger {
  background-color: #f6f9fd;
  box-shadow: 0 2px 8px rgba(31, 56, 88, 0.06);
}

/* 柔和的焦点提示 */
.user-dropdown:focus-visible .user-trigger {
  box-shadow: 0 0 0 3px rgba(64, 158, 255, 0.14);
}

/* 首字母头像 */
.user-dropdown .avatar-circle {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;

  width: 30px;
  height: 30px;
  border-radius: 50%;

  background-color: #e8f2ff;
  color: #2878d7;
  font-size: 14px;
  font-weight: 600;
  overflow: hidden;
}

.user-dropdown .avatar-circle img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* 用户名 */
.user-dropdown .username {
  min-width: 0;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;

  font-size: 14px;
  font-weight: 500;
}

/* 下拉菜单弹出层 */
.avatar-dropdown.el-popper {
  background: #ffffff;
  border: 1px solid #e5eaf1;
  border-radius: 12px;

  box-shadow: 0 8px 24px rgba(31, 56, 88, 0.12);
}

/* 菜单本体 */
.avatar-dropdown .el-dropdown-menu {
  min-width: 135px;
  padding: 6px;
  background: #ffffff;
  border-radius: 12px;
}

/* 菜单选项 */
.avatar-dropdown .el-dropdown-menu__item {
  display: flex;
  align-items: center;
  gap: 10px;

  margin: 2px 0;
  padding: 9px 12px;
  border-radius: 7px;

  color: #334155;
  font-size: 14px;
  line-height: 20px;

  transition:
    background-color 0.2s ease,
    color 0.2s ease;
}

.avatar-dropdown .el-dropdown-menu__item .el-icon {
  margin-right: 0;
  font-size: 16px;
  color: inherit;
}

.avatar-dropdown .el-dropdown-menu__item:not(.is-disabled):hover,
.avatar-dropdown .el-dropdown-menu__item:not(.is-disabled):focus {
  background-color: #edf5ff;
  color: #287ddf;
}
</style>
