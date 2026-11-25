<template>
  <div class="search-box" @keydown.enter.capture="handleEnter">
    <el-autocomplete
      ref="autocompleteRef"
      v-model="fullSearchWord"
      :fetch-suggestions="fetchSuggestions"
      :prefix-icon="Search"
      :highlight-first-item="true"
      @focus="handleFocus"
      @blur="isFocused = false"
    />
    <div v-show="!fullSearchWord && !isFocused" class="search-placeholder">
      输入
      <span class="search-shortcut">/</span>
      以查询
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { ElMessage } from "element-plus";
import { Search } from "@element-plus/icons-vue";

//定义发给父组件的emit事件
const emit = defineEmits(["search"]);
//定义props，通过props接收父组件提供的搜索条件
const props = defineProps({ suggestions: Array });

// 焦点事件绑定输入框获得焦点
const isFocused = ref(false);
const handleFocus = () => {
  isFocused.value = true;
};

//cb是一个函数，可以将匹配到的建议callback给autocomplete输入框
const fetchSuggestions = (queryString, cb) => {
  if (queryString.includes(":")) {
    cb([]);
    return;
  }
  //找到与用户输入匹配的搜索建议
  const filterSuggestions = props.suggestions.filter((item) =>
    item.value.includes(queryString),
  );
  //callback回调函数，传出fetchSuggestions，并让autocomplete组件决定如何使用
  cb(filterSuggestions);
};

const fullSearchWord = ref("");
//实现回车搜索
const handleSearch = () => {
  //先判断搜索格式是否合法
  const index = fullSearchWord.value.indexOf(":");
  if (!fullSearchWord.value.startsWith("/") || index === -1) {
    ElMessage.warning("(*￣︿￣) 要按照标准格式才可以搜索！");
    return;
  }
  //截取搜索条件和关键字
  const searchCriteria = fullSearchWord.value.slice(0, index + 1);
  const searchKeyword = fullSearchWord.value.slice(index + 1);
  const isValidCriteria = props.suggestions.some(
    (item) => item.value === searchCriteria,
  );
  if (!isValidCriteria) {
    ElMessage.warning("(＃￣～￣＃) 都给你搜索条件了还不会用...");
    return;
  }
  if (!searchKeyword.trim()) {
    ElMessage.warning("ヽ（≧□≦）ノ 不输入关键词怎么搜？");
    return;
  }

  //给父组件传搜索框内的参数
  emit("search", {
    searchCriteria: searchCriteria,
    searchKeyword: searchKeyword.trim(),
  });
};

const autocompleteRef = ref(null);
const handleEnter = (event) => {
  if (event.isComposing) return;
  const autocomplete = autocompleteRef.value;
  if (
    autocomplete?.activated &&
    autocomplete?.highlightedIndex >= 0 &&
    autocomplete?.highlightedIndex < autocomplete?.suggestions.length
  ) {
    return;
  }
  event.preventDefault();
  event.stopPropagation();
  handleSearch();
};
</script>

<style scoped>
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
</style>
