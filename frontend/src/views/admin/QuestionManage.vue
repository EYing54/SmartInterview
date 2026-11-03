<template>
  <div style="padding: 20px">
    <div class="question-header">
      <h2>题库</h2>
      <el-button type="primary" @click="displayDialog">新增题目</el-button>

      <!--弹窗部分-->
      <el-dialog
        v-model="dialogVisible"
        title="新 增 题 目"
        @closed="handleDialogClosed"
        width="900px"
      >
        <!--弹窗左侧部分-->
        <div class="question-dialog-layout">
          <el-form label-position="top">
            <el-form-item label="请输入题目：">
              <el-input type="textarea" v-model="question"></el-input>
            </el-form-item>

            <el-form-item label="请输入参考答案：">
              <el-input type="textarea" v-model="answer"></el-input>
            </el-form-item>

            <el-form-item label="添加标签：">
              <el-tag
                v-for="tag in selectedTags"
                :key="tag.tag_id"
                closable
                @close="handleRemoveTag(tag)"
              >
                {{ tag.tag_name }}
              </el-tag>
            </el-form-item>
          </el-form>

          <!--弹窗右侧部分-->
          <div class="tag-pool">
            <!--上部搜索公用组件-->
            <div>
              <span>可用标签</span>
              <el-button v-if="!isManageMode" @click="isManageMode = true"
                >管理标签</el-button
              >
              <el-button v-else @click="isManageMode = false"
                >返回选择</el-button
              >
              <el-input type="text" v-model="searchKeyword"></el-input>
            </div>

            <!--中部if组件-->
            <div v-if="!isManageMode">
              <el-tag
                v-for="tag in filteredTags"
                :key="tag.tag_id"
                @click="handleSelectTag(tag)"
              >
                {{ tag.tag_name }}
              </el-tag>
            </div>

            <!--中部else组件-->
            <div v-else>
              <template v-for="tag in filteredTags" :key="tag.tag_id">
                <!--单元行-->
                <div class="tag-item">
                  {{ tag.tag_name
                  }}<el-icon @click="handlegetEditTag(tag)"><Edit /></el-icon>
                  <el-icon @click="handleDeleteTag(tag)"><Delete /></el-icon>
                </div>
              </template>
            </div>

            <!--下部公用组件-->
            <div>
              <el-input type="text" v-model="newTagName"></el-input>
              <el-button
                v-if="!isManageMode"
                @click="handleAddTag"
                type="primary"
                >新增</el-button
              >
              <el-button v-else @click="handleSaveTagName" type="primary"
                >保存</el-button
              >
            </div>
          </div>
        </div>
        <el-button type="primary" @click="handleAddNewQuestion">确认</el-button>
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
import { ref, onMounted, computed } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { getQuestionList, addQuestions } from "../../api/question_manage";
import { Delete, Edit } from "@element-plus/icons-vue";
import {
  getTags,
  addTag,
  modifyTagName,
  deleteTag,
} from "../../api/tag_manage";

const questionList = ref([]);
//获取当前的数据库中的题库并以el-table的形式展现
const queryQuestions = async () => {
  try {
    const res = await getQuestionList(1, 20);
    questionList.value = res.data.data.list; //获取到的题目列表
  } catch (error) {
    console.log(error);
  }
};

//获取当前可用的标签
const dialogVisible = ref(false); //使用dialogVisible变量控制弹窗的弹出与关闭
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
const displayDialog = async () => {
  dialogVisible.value = true;
  await loadTags(); //打开弹窗时获取并显示标签池的标签
};

//添加新的标签
const newTagName = ref("");
const handleAddTag = async () => {
  try {
    newTagName.value = newTagName.value.trim();
    if (!newTagName.value) {
      ElMessage.warning("你还咩有输入标签名！");
      return;
    }
    const exists = availableTags.value.some(
      (item) => item.tag_name.toLowerCase() === newTagName.value.toLowerCase(),
    );
    if (exists) {
      console.log("与已有标签重复！");
      ElMessage.warning("该标签已存在！");
      return;
    }
    //向后端传的是去除了首位空格的字符串
    const res = await addTag(newTagName.value);
    ElMessage.success("新增标签成功！");
    newTagName.value = "";
    await loadTags();
    console.log(res.data.msg);
  } catch (error) {
    console.log(error);
    ElMessage.error("标签添加失败！");
  }
};

const selectedTags = ref([]); //从标签池中选择的标签
//使用handleSelectTag函数从availableTags获取值赋给selectedTags
const handleSelectTag = (tag) => {
  //使用some()检查数组里面有没有与当前tag相同的的tag
  const exists = selectedTags.value.some((item) => item.tag_id === tag.tag_id);
  //如果不为真就往数组里加tag
  if (!exists) {
    selectedTags.value.push(tag);
  }
};

//新增题目
const question = ref("");
const answer = ref("");
const handleAddNewQuestion = async () => {
  try {
    //使用map()遍历selectedTags数组，提取每一个tag元素的id并形成新的数组
    const tagIds = selectedTags.value.map((item) => item.tag_id);
    //判断是否选择了标签
    if (tagIds.length === 0) {
      ElMessage.warning("至少选择一个标签辣！");
      return;
    }
    //判断是否输入了题目
    if (!question.value.trim()) {
      //.trim()用来去除字符串首尾的空白字符，如空格
      ElMessage.warning("你还咩有输入题目！");
      return;
    }
    //判断是否输入了答案
    if (!answer.value.trim()) {
      ElMessage.warning("你还咩有输入答案！");
      return;
    }
    const res = await addQuestions(question.value, answer.value, tagIds); //tagIds是map()返回的普通数组，不要加.value
    console.log(res.data.msg);
    ElMessage.success("添加成功");
    //新增题目完成后自动关闭弹窗
    dialogVisible.value = false;
    await queryQuestions();
  } catch (error) {
    console.log(error);
    console.log("新增题目失败！");
    ElMessage.error(error.response?.data?.msg || "新增题目失败！");
  }
};

//点击"x"去除已选择的Tag
const handleRemoveTag = (tag) => {
  //filter()函数，保留所有符合条件的元素，返回一个新数组。
  selectedTags.value = selectedTags.value.filter(
    (item) => item.tag_id !== tag.tag_id,
  );
};

//关键字搜索
const searchKeyword = ref("");
const filteredTags = computed(() => {
  //将找到的元素数组都赋给filteredTags
  return availableTags.value.filter((item) => {
    //如果关键字包含在当前元素的名字中，就返回ture
    return item.tag_name
      .toLowerCase()
      .includes(searchKeyword.value.trim().toLowerCase());
  });
});

//标签管理
const isManageMode = ref(false);
const editingTagId = ref("");
//修改标签名称
const handlegetEditTag = (tag) => {
  newTagName.value = tag.tag_name;
  editingTagId.value = tag.tag_id;
};
const handleSaveTagName = async () => {
  try {
    newTagName.value = newTagName.value.trim();
    //判空校验
    if (!newTagName.value) {
      ElMessage.warning("你还咩有输入标签名！");
      return;
    }
    //防止未选择标签就修改标签名
    if (!editingTagId.value) {
      ElMessage.warning("不可以凭空修改标签名哦！请先点击修改图标！");
      return;
    }
    //防止未修改标签就进行保存
    const exists = availableTags.value.some(
      (item) =>
        item.tag_id === editingTagId.value &&
        item.tag_name === newTagName.value,
    );
    if (exists) {
      ElMessage.warning("标签名称还没修改呢！");
      return;
    }
    const res = await modifyTagName(editingTagId.value, newTagName.value);
    await loadTags();
    console.log(res?.data?.msg);
    ElMessage.success("标签修改成功！");
    //修改成功后初始化输入框状态
    newTagName.value = "";
    editingTagId.value = "";
  } catch (error) {
    console.log(error);
    console.log("标签修改失败！");
    ElMessage.error(error.response?.data?.msg || "标签修改失败！");
  }
};

//删除标签
const handleDeleteTag = async (tag) => {
  try {
    //二次确认确认框
    await ElMessageBox.confirm(
      `确定要删除标签「${tag.tag_name}」吗？`,
      "删除确认",
      {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning",
      },
    );
    const res = await deleteTag(tag.tag_id, tag.tag_name);
    console.log(res.data.msg);
    ElMessage.success("标签删除成功！");
    await loadTags();
  } catch (error) {
    if (error === "close" || error === "cancel") {
      return; //ElementPlus的确认框在关闭或者取消时会给catch传error，这里不再执行错误处理
    }
    if (error.response?.status === 409) {
      const count = error.response.data.data;
      ElMessageBox.alert(
        `「${tag.tag_name}」标签还有${count}个题目在用呢！你要狠心拆散他们吗？QAQ`,
        "删除失败",
        { confirmButtonText: "确定", type: "error" },
      );
    } else {
      ElMessageBox.alert(error.response?.data?.msg, "删除失败", {
        confirmButtonText: "确定",
        type: "error",
      });
    }
    console.log(error);
    console.log(error.response?.data?.msg || "标签删除失败！");
  }
};

const handleDialogClosed = () => {
  newTagName.value = "";
  selectedTags.value = [];
  question.value = "";
  answer.value = "";
  searchKeyword.value = "";
  isManageMode.value = false;
  editingTagId.value = "";
};

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

/* 管理的每一行标签 */
.tag-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 4px;
  border-bottom: 1px solid #e5e7eb;
}

.tag-item .el-icon:first-of-type {
  margin-left: auto;
}

/* 图标样式 */
.tag-item .el-icon {
  font-size: 17px;
  cursor: pointer;
}

/* 编辑图标悬停样式 */
.tag-item .el-icon:first-of-type:hover {
  color: var(--el-color-primary);
}

/* 删除图标悬停样式 */
.tag-item .el-icon:last-of-type:hover {
  color: var(--el-color-danger);
}
</style>
