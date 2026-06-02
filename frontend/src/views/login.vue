<template>
  <div>
    <input type="text" v-model="username" />
    <input type="password" v-model="password" />
    <button @click="handleLogin">登录</button>
  </div>
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
