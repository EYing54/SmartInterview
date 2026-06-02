<template>
  <div style="padding: 20px">
    <h2>智能面试系统 - 题库大厅</h2>

    <el-button
      type="primary"
      @click="queryQuestions"
      style="margin-bottom: 20px"
    >
      查询题目
    </el-button>

    <el-table :data="questionList" border style="width: 100%">
      <el-table-column prop="question_id" label="ID" width="80" />
      <el-table-column prop="question" label="面试题目" />
      <el-table-column prop="answer" label="参考答案" />
    </el-table>
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
