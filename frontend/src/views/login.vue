<template>
  <div>
    <input type="text" v-model="username" />
    <input type="password" v-model="password" />
    <button @click="handleLogin">登录</button>
  </div>
</template>

<script setup>
import { ref } from "vue";
import axios from "axios";

const username = ref("");
const password = ref("");
const handleLogin = async () => {
  console.log(username.value);
  console.log(password.value);
  try {
    const res = await axios.post("http://127.0.0.1:5000/login", {
      username: username.value,
      password: password.value,
    });
    console.log("post成功，返回的数据为：", res.data);
  } catch (error) {
    console.log("捕获到错误：", error);
  }
};
</script>
