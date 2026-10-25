<template>
  <div style="padding: 20px">
    <div class="question-header">
      <h2>题库</h2>
      <el-button type="primary" @click="displayDialog">新增题目</el-button>

      <el-dialog v-model="dialogVisible" title="新 增 题 目" width="900px">
        <div class="question-dialog-layout">
          <el-form label-position="top">
            <el-form-item label="请输入题目：">
              <el-input type="textarea" v-model="question"></el-input>
            </el-form-item>

            <el-form-item label="请输入参考答案：">
              <el-input type="textarea" v-model="answer"></el-input>
            </el-form-item>

            <el-form-item label="题目标签：">
              <el-tag v-for="tag in selectedTags" :key="tag.tag_id" closable>
                {{ tag.tag_name }}
              </el-tag>
            </el-form-item>
          </el-form>

          <div class="tag-pool">
            <p>搜索标签</p>
            <el-input type="text" v-model="searchKeyword"></el-input>
            <el-tag v-for="tag in availableTags" :key="tag.tag_id">
              {{ tag.tag_name }}
            </el-tag>
            <el-input type="text" v-model="newTagName"></el-input>
            <el-button @click="handleAddTag" type="primary">新增标签</el-button>
          </div>
        </div>
      </el-dialog>
    </div>
    <el-table :data="questionList" border style="width: 100%">
      <el-table-column prop="question_id" label="ID" width="80" />
      <el-table-column prop="question" label="面试题目" />
      <el-table-column prop="answer" label="参考答案" />
    </el-table>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { getQuestionList } from "../../api/question_manage";
import {
  getTags,
  addTag,
  modifyTagName,
  deleteTag,
  searchTag,
} from "../../api/tag_manage";

const questionList = ref([]);
const queryQuestions = async () => {
  try {
    const res = await getQuestionList(1, 20);
    questionList.value = res.data.data.list;
  } catch (error) {
    console.log(error);
  }
};

const dialogVisible = ref(false);
const displayDialog = async () => {
  dialogVisible.value = true;
  await loadTags();
};

const question = ref("");
const answer = ref("");
const availableTags = ref([]);
const loadTags = async () => {
  try {
    const res = await getTags();
    availableTags.value = res.data.data;
    console.log("获取标签列表成功！");
  } catch (error) {
    console.log(error);
    console.log("获取标签列表失败！");
  }
};

const selectedTags = ref([]);

onMounted(() => {
  queryQuestions();
});
</script>
<style scoped>
.question-header {
  display: flex;
}

.question-dialog-layout {
  display: flex;
  gap: 24px;
  align-items: flex-start;
}

/* 左侧题目表单 */
.question-dialog-layout > .el-form {
  flex: 11 1 0;
  min-width: 0;
}

/* 右侧标签池 */
.tag-pool {
  flex: 9 1 0;
  min-width: 0;
}

/* 输入框宽度 */
.question-dialog-layout .el-input,
.question-dialog-layout .el-textarea {
  width: 100%;
}

/* 标签池标题 */
.tag-pool p {
  margin: 0 0 10px;
}

/* 标签之间的间距 */
.tag-pool .el-tag {
  margin: 8px 8px 0 0;
}

/* 标签池输入框与按钮间距 */
.tag-pool > .el-input {
  margin-top: 12px;
  margin-bottom: 12px;
}
</style>
