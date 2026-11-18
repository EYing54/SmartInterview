<template>
  <div class="search-box">
    <el-autocomplete
      :fetch-suggestions="fetchSuggestions"
      v-model="searchKeyword"
      :prefix-icon="Search"
      @focus="handleFocus"
      @blur="isFocused = false"
    />
    <div v-show="!searchKeyword && !isFocused" class="search-placeholder">
      输入
      <span class="search-shortcut">/</span>
      以查询
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { Search } from "@element-plus/icons-vue";

const searchKeyword = ref("");
const isFocused = ref(false);

// 焦点事件绑定输入框获得焦点
const handleFocus = () => {
  isFocused.value = true;
};

//通过props接收父组件提供的搜索条件
const props = defineProps({ suggestions: Array });
//cb是一个函数，可以将匹配到的建议callback给autocomplete输入框
const fetchSuggestions = (queryString, cb) => {
  //找到与用户输入匹配的搜索建议
  const filterSuggestions = props.suggestions.filter((item) =>
    item.value.includes(queryString),
  );
  //callback回调函数，传出fetchSuggestions，并让autocomplete组件决定如何使用
  cb(filterSuggestions);
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
