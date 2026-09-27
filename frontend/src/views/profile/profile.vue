<template></template>
<script setup>
import { ref, onMounted } from "vue";
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
const loadUserProfile = async () => {
  try {
    const res = await getUserProfile();
    data.value = res.data.data;
  } catch (error) {
    console.log("获取用户信息失败：", error);
    ElMessage.error("获取用户信息失败");
  }
};

onMounted(() => {
  loadUserProfile();
});
</script>
