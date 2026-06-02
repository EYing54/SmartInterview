<template>
  <div>
    <h1>欢迎来到主页</h1>
    <button @click="queryQuestions">查询题目</button>
    <ul>
      <li
        v-for="q in questionList"
        :key="q.question_id"
        style="margin-bottom: 20px"
      >
        <strong>题目：</strong> {{ q.question }} <br />
        <strong>答案：</strong> {{ q.answer }}
      </li>
    </ul>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { getQuestionList } from "../api/question";

const questionList = ref([]);
const queryQuestions = async () => {
  try {
    const res = await getQuestionList(1, 20);
    questionList.value = res.data.data.list;
  } catch (error) {
    console.log(error);
  }
};
</script>
