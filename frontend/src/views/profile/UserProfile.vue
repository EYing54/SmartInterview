<template>
  <div class="profile_layout">
    <el-card class="left_card">左侧导航栏</el-card>
    <div class="right_container">
      <el-card class="right_card_1">
        <el-avatar :size="80" :src="url">头像</el-avatar>
      </el-card>
      <el-card class="right_card_2">
        <h3>账号信息</h3>
        <p>用户名：{{ data?.username }}</p>
        <p>昵称：{{ data?.nickname }}</p>
      </el-card>
    </div>
  </div>
</template>
<script setup>
import { ref, onMounted, onUnmounted } from "vue";
import { ElMessage } from "element-plus";
import {
  getUserProfile,
  uploadAvatar,
  getUserAvatar,
  modifyPost,
  modifyPassword,
  modifyNickname,
} from "../../api/user";

const data = ref(null);
//获取用户信息
const loadUserProfile = async () => {
  try {
    const res = await getUserProfile();
    data.value = res.data.data;
    console.log(data.value);
    const avatarPath = res.data.data.avatar_path;
    if (avatarPath) {
      getAvatarURL(); //若用户未设置头像则不访问接口以节省资源
    }
  } catch (error) {
    console.log("获取用户信息失败：", error);
    ElMessage.error("获取用户信息失败");
  }
};

const url = ref("");
const getAvatarURL = async () => {
  try {
    const res = await getUserAvatar();
    console.log(res.data);
    url.value = URL.createObjectURL(res.data); //使用URL.createObjectURL生成一个临时的url供<el-avatar>使用
  } catch (error) {
    console.log(error);
  }
};

onMounted(() => {
  loadUserProfile();
});

onUnmounted(() => {
  if (url.value) {
    URL.revokeObjectURL(url.value);
  } //避免头像地址为空时还尝试释放
});
</script>

<style scoped>
.profile_layout {
  display: flex;
  gap: 5px;
}
.left_card {
  width: 220px;
}
.right_container {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 5px;
}
</style>
