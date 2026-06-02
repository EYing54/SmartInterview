<template>
  <el-card style="width: 400px; margin: 150px auto">
    <el-input
      type="text"
      placeholder="请输入账号"
      style="margin-bottom: 20px"
      v-model="username"
    />
    <el-input
      type="password"
      placeholder="请输入密码"
      show-password
      style="margin-bottom: 20px"
      v-model="password"
    />
    <el-button type="primary" style="width: 100%" @click="handleLogin"
      >登录</el-button
    >
  </el-card>
</template>

<script setup>
import { ref } from "vue";
import { loginAPI } from "../api/user";
import { useRouter } from "vue-router";

const router = useRouter();
const username = ref("");
const password = ref("");
const handleLogin = async () => {
  console.log(username.value);
  console.log(password.value);
  try {
    const res = await loginAPI(username.value, password.value);
    console.log("post成功，返回的数据为：", res.data);
    localStorage.setItem("token", res.data.data.token);
    router.push("/home");
  } catch (error) {
    console.log("捕获到错误：", error);
  }
};
</script>
