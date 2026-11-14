<template>
  <div class="manage-page">
    <div class="manage-header">
      <div class="manage-title">
        <h2>题库</h2>
      </div>
      <div class="manage-toolbar">
        <div class="search-box">
          <el-input
            v-model="searchQuery"
            :prefix-icon="Search"
            @focus="isFocused = true"
            @blur="isFocused = false"
          />
          <div v-show="!searchQuery && !isFocused" class="search-placeholder">
            输入
            <span class="search-shortcut">/</span>
            以查询
          </div>
        </div>
        <el-button plain type="primary" @click="displayDialog" :icon="Plus"
          >新增题目</el-button
        >
        <el-button
          plain
          type="danger"
          @click="handleDeleteQuestions"
          :icon="Delete"
          >删除题目</el-button
        >
      </div>
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
            <el-form-item label="题目">
              <el-input
                type="textarea"
                v-model="question"
                placeholder="请在这里输入题目"
              ></el-input>
            </el-form-item>

            <el-form-item label="参考答案">
              <el-input
                type="textarea"
                v-model="answer"
                placeholder="请在这里输入参考答案"
              ></el-input>
            </el-form-item>

            <el-form-item label="添加标签">
              <div v-if="selectedTags.length === 0" class="selected-tags-empty">
                <span>点击右侧标签，就可以添加到这里啦</span>
              </div>
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
              <el-button
                v-if="!isManageMode"
                @click="isManageMode = true"
                :icon="Setting"
                >管理标签</el-button
              >
              <el-button
                v-else
                @click="isManageMode = false"
                :icon="ArrowLeftBold"
                >返回选择</el-button
              >
              <el-input
                type="text"
                v-model="searchKeyword"
                placeholder="在这里搜索标签"
                :prefix-icon="Search"
              ></el-input>
            </div>

            <!--中部if组件：选择模式-->
            <div v-if="!isManageMode">
              <el-tag
                v-for="tag in filteredTags"
                :key="tag.tag_id"
                @click="handleSelectTag(tag)"
              >
                {{ tag.tag_name }}
              </el-tag>
            </div>

            <!--中部else组件：管理模式-->
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
              <el-input
                type="text"
                v-model="newTagName"
                :placeholder="
                  isManageMode
                    ? '点击上面标签的修改图标进行修改哦'
                    : '在这里可以新增标签'
                "
              ></el-input>
              <el-button
                v-if="!isManageMode"
                @click="handleAddTag"
                type="primary"
                :icon="Plus"
                >新增</el-button
              >
              <el-button
                v-else
                @click="handleSaveTagName"
                type="primary"
                :icon="Check"
                >保存</el-button
              >
            </div>
          </div>
        </div>
        <el-button type="primary" @click="handleAddNewQuestion">确认</el-button>
      </el-dialog>
    </div>
    <el-table
      :data="questionList"
      class="manage-table"
      border
      style="width: 100%"
      @selection-change="handleSelectionChange"
    >
      <el-table-column type="index" label="序号" width="80" align="center" />
      <el-table-column
        prop="question_id"
        label="题目ID"
        width="80"
        align="center"
      />
      <el-table-column prop="question" label="题目" />
      <el-table-column label="标签">
        <template #default="scope">
          <div class="question-tag">
            <el-tag v-for="tag in scope.row.question_tags" :key="tag">{{
              tag
            }}</el-tag>
          </div>
        </template>
      </el-table-column>
      <el-table-column type="selection" width="60" align="center" />
    </el-table>

    <div class="pagination-container">
      <el-pagination
        v-model:current-page="currentPage"
        :page-size="pageSize"
        layout="prev, pager, next"
        :total="total"
        @current-change="handlePageChange"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import {
  getQuestionList,
  addQuestions,
  deleteQuestions,
} from "../../api/question_manage";
import {
  Delete,
  Edit,
  Search,
  Setting,
  Plus,
  ArrowLeftBold,
  Check,
} from "@element-plus/icons-vue";
import {
  getTags,
  addTag,
  modifyTagName,
  deleteTag,
} from "../../api/tag_manage";

const questionList = ref([]);
const total = ref(0);
const currentPage = ref(1);
const pageSize = ref(20);
//获取当前的数据库中的题库并以el-table的形式展现
const getQuestions = async () => {
  try {
    const res = await getQuestionList(currentPage.value, pageSize.value);
    questionList.value = res.data.data.list; //获取到的题目列表
    total.value = res.data.data.total;
    console.log("题库获取成功！");
  } catch (error) {
    console.log(error);
  }
};

//分页功能
const handlePageChange = (val) => {
  currentPage.value = val;
  getQuestions();
};

//控制搜索框的变化
const searchQuery = ref("");
const isFocused = ref(false);

//关联每一行的选择框
const selectedQuestions = ref([]);
const handleSelectionChange = (val) => {
  selectedQuestions.value = val;
  console.log(selectedQuestions);
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

//选择标签
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
    await getQuestions();
  } catch (error) {
    console.log(error);
    console.log("新增题目失败！");
    ElMessage.error(error.response?.data?.msg || "新增题目失败！");
  }
};

//删除题目
const handleDeleteQuestions = async () => {
  try {
    if (selectedQuestions.value.length === 0) {
      ElMessage.error("你还没有选择要删除的题目啊！");
      return;
    }
    const selectedQuestionIds = selectedQuestions.value.map(
      (item) => item.question_id,
    );
    await ElMessageBox.confirm(
      `>_< 你要狠心删除这${selectedQuestions.value.length}道题目吗？`,
      "删除题目",
      {
        confirmButtonText: "确认",
        cancelButtonText: "取消",
        type: "warning",
      },
    );
    const res = await deleteQuestions(selectedQuestionIds);
    ElMessage.success(res.data.msg);
    await getQuestions();
  } catch (error) {
    if (error === "cancel" || error === "close") {
      console.log("用户取消了操作！");
      return;
    }
    ElMessage.error("删除失败！");
    console.log(error);
    console.log(error.response?.data?.msg);
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
  //将找到的元素都赋给filteredTags
  return availableTags.value.filter((item) => {
    const isSelected = selectedTags.value.some(
      (tag) => tag.tag_id === item.tag_id,
    ); //判断当前选择了的标签里有没有和当前遍历到的可用标签一样的，如果有就返回ture
    const isMatched = item.tag_name
      .toLowerCase()
      .includes(searchKeyword.value.trim().toLowerCase()); //判断当前遍历到的标签名称里是否包含搜索关键字，如果包含就返回ture
    const canShow = isManageMode.value || !isSelected; //管理模式默认为false，
    return isMatched && canShow;
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
      console.log("用户取消了操作！");
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
  getQuestions();
});
</script>

<style scoped>
.manage-page {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

/* 题库顶部 */
.manage-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 25px;
}

.manage-title {
  border-left: 5px solid #409eff;
  padding-left: 15px;
}

.manage-title h2 {
  margin: 0;
  font-size: 22px;
}

/* 操作工具栏 */
.manage-toolbar {
  display: flex;
  gap: 12px;
  align-items: center;
}

.manage-toolbar :deep(.el-button) {
  margin-left: 0;
}

/* 搜索框 */
.search-box {
  position: relative;
  width: 250px;
}

.search-placeholder {
  position: absolute;
  left: 32px;
  top: 50%;
  transform: translateY(-50%);
  display: flex;
  align-items: center;
  color: #a8abb2;
  font-size: 14px;
  pointer-events: none;
}

.search-shortcut {
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  padding: 1px 5px;
  margin: 0 4px;
  font-size: 12px;
  background-color: #f4f4f5;
}

/* 数据表格 */
.manage-table {
  width: 100%;
}

/*题目标签 */
.question-tag {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

/* 分页 */
.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

/* 弹窗整体 */
:global(.el-dialog:has(.question-dialog-layout)) {
  margin: 4vh auto 0 !important;
  max-width: calc(100vw - 32px);
  max-height: calc(100dvh - 32px);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* 弹窗标题区域 */
:global(.el-dialog:has(.question-dialog-layout) .el-dialog__header) {
  margin: 0;
  padding: 18px 24px 12px;
  text-align: center;
  flex-shrink: 0;
}

/* 弹窗标题 */
:global(.el-dialog:has(.question-dialog-layout) .el-dialog__title) {
  font-size: 20px;
  font-weight: 600;
  letter-spacing: 2px;
  color: var(--el-text-color-primary);
}

/* 关闭按钮 */
:global(.el-dialog:has(.question-dialog-layout) .el-dialog__headerbtn) {
  top: 12px;
  right: 16px;
}

/* 弹窗内容区域 */
:global(.el-dialog:has(.question-dialog-layout) .el-dialog__body) {
  display: flex;
  flex-direction: column;
  gap: 16px;
  min-height: 0;
  padding: 8px 24px 20px;
  overflow-y: auto;
  scrollbar-width: none;
}

/* 隐藏弹窗内容滚动条 */
:global(
  .el-dialog:has(.question-dialog-layout) .el-dialog__body::-webkit-scrollbar
) {
  display: none;
}

/* 弹窗左右布局 */
.question-dialog-layout {
  display: flex;
  align-items: stretch;
  gap: 24px;
  height: 388px;
  min-height: 0;
  flex-shrink: 0;
  overflow: hidden;
}

/* 输入框宽度 */
.question-dialog-layout .el-input,
.question-dialog-layout .el-textarea {
  width: 100%;
}

/* 左侧题目表单 */
.question-dialog-layout > .el-form {
  flex: 1 1 0;
  min-width: 0;
  height: 100%;
  min-height: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* 表单项间距 */
.question-dialog-layout > .el-form .el-form-item {
  display: flex;
  flex-direction: column;
  min-height: 0;
  margin-bottom: 12px;
}

/* 左右标题统一样式 */
.question-dialog-layout > .el-form :deep(.el-form-item__label),
.tag-pool > div:first-child > span {
  font-size: 14px;
  font-weight: 600;
  color: var(--el-text-color-primary);
  line-height: 22px;
}

/* 左侧表单标题 */
.question-dialog-layout > .el-form :deep(.el-form-item__label) {
  display: flex;
  align-items: center;
  height: 22px;
  min-height: 22px;
  padding: 0;
  margin-bottom: 6px;
}

/* 题目标题行 */
.question-dialog-layout
  > .el-form
  .el-form-item:first-child
  :deep(.el-form-item__label) {
  height: 40px;
  min-height: 40px;
  flex: 0 0 40px;
  margin-bottom: 8px;
}

/* 题目输入框 */
.question-dialog-layout
  > .el-form
  .el-form-item:nth-child(1)
  :deep(.el-textarea__inner) {
  height: 72px;
  min-height: 72px;
  max-height: 72px;
  overflow-y: auto;
  resize: none;
}

/* 参考答案输入框 */
.question-dialog-layout
  > .el-form
  .el-form-item:nth-child(2)
  :deep(.el-textarea__inner) {
  height: 120px;
  min-height: 120px;
  max-height: 120px;
  overflow-y: auto;
  resize: none;
}

/* 已选标签表单项 */
.question-dialog-layout > .el-form .el-form-item:nth-child(3) {
  flex: 1 1 0;
  min-height: 0;
  margin-bottom: 0;
  overflow: hidden;
}

/* 已选标签展示区域 */
.question-dialog-layout
  > .el-form
  .el-form-item:nth-child(3)
  :deep(.el-form-item__content) {
  flex: 1 1 0;
  min-height: 0;
  width: 100%;
  box-sizing: border-box;
  display: flex;
  flex-wrap: wrap;
  align-content: flex-start;
  align-items: flex-start;
  gap: 8px;
  padding: 12px;
  border: 1px dashed var(--el-border-color);
  border-radius: 8px;
  background-color: var(--el-bg-color);
  overflow-y: auto;
  overflow-x: hidden;
  overscroll-behavior: contain;
  scrollbar-width: none;
}

/* 隐藏已选标签滚动条 */
.question-dialog-layout
  > .el-form
  .el-form-item:nth-child(3)
  :deep(.el-form-item__content::-webkit-scrollbar) {
  display: none;
  width: 0;
  height: 0;
}

/* 已选标签样式 */
.question-dialog-layout > .el-form .el-form-item:nth-child(3) .el-tag {
  margin: 0;
  flex-shrink: 0;
}

/* 右侧标签池 */
.tag-pool {
  flex: 1 1 0;
  min-width: 0;
  height: 100%;
  min-height: 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

/* 标签池顶部布局 */
.tag-pool > div:first-child {
  display: grid;
  grid-template-columns: 1fr auto;
  grid-template-rows: 40px 40px;
  align-items: center;
  column-gap: 10px;
  row-gap: 8px;
}

/* 可用标签标题 */
.tag-pool > div:first-child > span {
  display: flex;
  align-items: center;
  height: 40px;
}

/* 管理标签按钮 */
.tag-pool > div:first-child > .el-button {
  margin: 0;
}

/* 搜索输入框 */
.tag-pool > div:first-child > .el-input {
  grid-column: 1 / -1;
  height: 40px;
}

/* 固定标签展示区域 */
.tag-pool > div:nth-child(2) {
  box-sizing: border-box;
  height: 240px;
  min-height: 240px;
  max-height: 240px;
  flex: 0 0 240px;
  padding: 12px;
  border: 1px solid var(--el-border-color-light);
  border-radius: 8px;
  background-color: var(--el-fill-color-lighter);
  overflow-y: auto;
  overflow-x: hidden;
  overscroll-behavior: contain;
  scrollbar-width: thin;
  scrollbar-color: #c4c9d2 transparent;
}

/* 可用标签样式 */
.tag-pool > div:nth-child(2) .el-tag {
  margin: 0 8px 8px 0;
  cursor: pointer;
  transition: all 0.2s ease;
}

/* 标签悬停 */
.tag-pool > div:nth-child(2) .el-tag:hover {
  border-color: var(--el-color-primary);
  background-color: var(--el-color-primary-light-8);
}

/* 管理模式标签行 */
.tag-item {
  display: flex;
  align-items: center;
  gap: 12px;
  box-sizing: border-box;
  min-height: 36px;
  padding: 5px 8px;
  border-bottom: 1px solid var(--el-border-color-lighter);
  transition: background-color 0.2s ease;
}

/* 最后一行标签 */
.tag-item:last-child {
  border-bottom: none;
}

/* 标签行悬停 */
.tag-item:hover {
  background-color: var(--el-fill-color);
  border-radius: 4px;
}

/* 编辑图标靠右 */
.tag-item .el-icon:first-of-type {
  margin-left: auto;
}

/* 操作图标样式 */
.tag-item .el-icon {
  font-size: 17px;
  cursor: pointer;
  flex-shrink: 0;
}

/* 编辑图标悬停 */
.tag-item .el-icon:first-of-type:hover {
  color: var(--el-color-primary);
}

/* 删除图标悬停 */
.tag-item .el-icon:last-of-type:hover {
  color: var(--el-color-danger);
}

/* 标签池底部操作区 */
.tag-pool > div:last-child {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: auto;
  flex-shrink: 0;
}

/* 新增标签输入框 */
.tag-pool > div:last-child > .el-input {
  flex: 1;
  min-width: 0;
}

/* 新增和保存按钮 */
.tag-pool > div:last-child > .el-button {
  min-width: 68px;
  margin: 0;
  flex-shrink: 0;
}

/* 底部确认按钮 */
.question-dialog-layout + .el-button {
  display: block;
  width: 100px;
  min-height: 36px;
  align-self: center;
  flex-shrink: 0;
  margin: 0 auto !important;
}

/* 已选标签容器定位 */
.question-dialog-layout
  > .el-form
  .el-form-item:nth-child(3)
  :deep(.el-form-item__content) {
  position: relative;
}

/* 空状态提示居中 */
.selected-tags-empty {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  pointer-events: none;
}

/* 空状态提示文字 */
.selected-tags-empty span {
  font-size: 13px;
  color: var(--el-text-color-placeholder);
}
</style>
